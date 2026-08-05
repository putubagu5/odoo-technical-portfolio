import base64
from base64 import urlsafe_b64decode as b64dec
from base64 import urlsafe_b64encode as b64enc
from datetime import date, datetime
import logging
import urllib.parse
import zlib
from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.http import request


VALID_STATES = ('approve', 'approve_delegate', 'forward')
# VALID_STATES = ('approve', 'approve_delegate')
_logger = logging.getLogger(__name__)


def _decode_url(data: str) -> str:
    """ helper function to handle data decoding """
    result = ''
    try:  # try to handle decoding first, potentially caused by user
        tmp_data = b64dec(data)
    except Exception as exc:
        tmp_data = ''  # empty out

    if tmp_data:
        try:  # decoded data is valid, but could it be decompressed?
            result = zlib.decompress(tmp_data).decode()
        except zlib.error:  # just log and return empty result
            _logger.info('URL is invalid')
    return result


def _encode_url(data: str) -> str:
    # data in string, encode to bytes first, then pack
    data = data.encode()
    # compress with level 6 (faster and better). Result is decoded
    return b64enc(zlib.compress(data)).decode()


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    hierarchy_id = fields.Many2one('approval.hierarchy', 'Approval Hierarchy')
    approval_history_ids = fields.One2many('purchase.request.approval',
                                           'request_id', 'Approval Histories')
    approval_message_ids = fields.One2many('purchase.request.message',
                                           'request_id', 'Message Histories')
    current_approver_id = fields.Many2one('hr.employee', 'Current Approver',
                                          compute='_compute_current_approver',
                                          store=False)
    current_user_id = fields.Many2one('res.users', 'Current Approver',
                                      compute='_compute_current_user',
                                      store=True)
    is_current_approver = fields.Boolean('Is Current Approver',
                                         compute='_compute_current_approver',
                                         store=False)
    is_requestor = fields.Boolean('Is Requestor',
                                  compute='_compute_is_requestor')
    is_rejected = fields.Boolean('Rejected', default=False,
                                 help='True if record is rejected')
    selected_approver_id = fields.Many2one('hr.employee', 'Selected Approver')
    selected_approver_ids = fields.Many2many('hr.employee',
                                             string='Selected Approvers',
                                             compute='_compute_selected_approvers')
    is_resend = fields.Boolean('Is Resend', default=False)
    has_ask = fields.Boolean('Has Ask', compute='_compute_has_ask')

    @api.onchange('requested_by', 'company_id')
    def _onchange_requested_by(self):
        """ onchange function to filter hierarchy_id based on request user """
        if self.requested_by:
            # find the hierarchy with lines containing the same job as user
            # or just find the lines with the employee
            employee = self.requested_by.employee_id
            domain = [
                ('employee_ids', 'in', [employee.id]),
                ('hierarchy_id.company_id', '=', self.company_id.id),
                ('hierarchy_id.module', '=', 'purchase.request'),
            ]
            lines = self.env['approval.hierarchy.line'].search(domain)
            recs = [x.hierarchy_id.id for x in lines]
            return {
                'domain': {
                    'hierarchy_id': [('id', 'in', recs)],
                }
            }

    @api.depends('approval_history_ids')
    def _compute_has_ask(self):
        """ compute function to determine if there is someone asking """
        # has_ask will be true if there is `ask` state in Approval History and
        # it will show the Answer button for the requestor
        for rec in self:
            rec.has_ask = any([x.state == 'ask' for x in rec.approval_history_ids])

    def _show_selected_approvers(self):
        """ helper function to get valid data for showing selected_approver_ids """
        self.ensure_one()
        return self.is_rejected or self.env.user.has_group('ins_base_mnc.group_super_admin')

    @api.depends('requested_by', 'is_rejected', 'hierarchy_id')
    def _compute_selected_approvers(self):
        """ compute function to get selected approvers based on hierarchy_id """
        # mimic logic from _assign_approval
        for rec in self:
            emps = []
            if rec._show_selected_approvers() and rec.hierarchy_id and rec.requested_by:
                lines = rec.hierarchy_id.line_ids

                user_emp = rec.requested_by.employee_id
                app_line = lines.filtered(lambda x: user_emp in x.employee_ids)
                app_line = app_line.sorted(key=lambda x: x.level)

                while app_line:
                    app_line = app_line[0]
                    parent = app_line.parent_job_id

                    emp = user_emp
                    if app_line.employee_ids and user_emp not in app_line.employee_ids:
                        emp = app_line.employee_ids[0]
                        if emp:
                            emps.append(emp.id)

                    # NOTE: not the requestor, and no employee, find parent, skip
                    if not emp:
                        app_line = lines.filtered(
                            lambda x: x.job_id == parent and x.level < app_line.level
                        ).sorted(key=lambda x: -x.level)
                        continue

                    # if there is group and limit >= total, this is the last approval
                    # no need to process the next
                    group = app_line.approval_group_id
                    if group and group.amount_limit >= self.estimated_cost:
                        break

                    # find line with parent job and level < current level
                    app_line = lines.filtered(
                        lambda x: x.job_id == parent and x.level < app_line.level
                    ).sorted(key=lambda x: -x.level)

                emps = [(6, 0, emps)]
            rec.selected_approver_ids = emps

    @api.depends('requested_by')
    def _compute_is_requestor(self):
        """ function to check if user is requestor """
        for rec in self:
            rec.is_requestor = rec.requested_by == rec.env.user

    @api.depends('company_id.purchase_dynamic_approval', 'approval_history_ids.state')
    def _compute_current_user(self):
        """ compute function to get current approver """
        for rec in self:
            current = rec._get_current_approver()
            rec.current_user_id = current.user_id.id

    @api.depends('company_id.purchase_dynamic_approval', 'approval_history_ids',
                 'approval_history_ids.state')
    def _compute_current_approver(self):
        """ compute function to get current approver """
        for rec in self:
            current = rec._get_current_approver()
            rec.current_approver_id = current.id
            rec.is_current_approver = self.env.user.employee_id == current

    def _assign_approval(self):
        """ helper function to assign approval hierarchy to history """
        # NOTE: hierarchy could have lines with the same parent_job_id
        hierarchy = self.hierarchy_id
        user_emp = self.requested_by.employee_id

        # rule: find the lines with the user_emp, then backtrack to the lines
        # by finding the parent of the current line, then parent of the parent
        # and so on. Finally, construct the approval hierarchy
        if hierarchy:  # records exist, clean lines
            lines = [(2, x.id) for x in self.approval_history_ids]

            app_line = hierarchy.line_ids.filtered(
                lambda x: user_emp in x.employee_ids)

            # if rejected and selected_approver_id exists
            if self._show_selected_approvers() and self.selected_approver_id:
                # before re-filtering the line, get the requestor line
                requestor_line = app_line

                app_line = hierarchy.line_ids.filtered(
                    lambda x: self.selected_approver_id in x.employee_ids)

                # also add the requestor directly by adding level by 1
                data = {
                    'level': requestor_line.level + 1,
                    'employee_id': user_emp.id,
                    'department_id': requestor_line.department_id.id,
                    'job_id': requestor_line.job_id.id,
                    'approval_group_id': requestor_line.approval_group_id.id,
                    'date': datetime.now(),
                    'state': 'approve',
                    'note': 'Submit',
                }
                lines.append((0, 0, data))
                # and send message
                msg = {
                    'employee_id': user_emp.id,
                    'date': datetime.now(),
                    'state': 'approve',
                    'note': 'Submit',
                }
                self.approval_message_ids = [(0, 0, msg)]

            # app_line contains the line with requesting user, we sort by level
            app_line = app_line.sorted(key=lambda x: x.level)
            # iterate by parent_job_id
            while app_line:
                # get the record and the parent job
                app_line = app_line[0]
                parent = app_line.parent_job_id

                emp = user_emp
                if app_line.employee_ids and user_emp not in app_line.employee_ids:
                    emp = app_line.employee_ids[0]

                # NOTE: not the requestor, and no employee, find parent, skip
                if not emp or not app_line.employee_ids:  # probably empty employee
                    app_line = hierarchy.line_ids.filtered(
                        lambda x: x.job_id == parent and x.level < app_line.level
                    ).sorted(key=lambda x: -x.level)
                    continue

                data = {
                    'level': app_line.level,
                    'employee_id': emp.id,
                    'department_id': app_line.department_id.id,
                    'job_id': app_line.job_id.id,
                    'approval_group_id': app_line.approval_group_id.id,
                }

                # before adding to data, if emp == user_emp, add date, make
                # state to approve directly
                if emp == user_emp:
                    data['date'] = datetime.now()
                    data['state'] = 'approve'
                    data['note'] = 'Submit'
                    # this case also record a message
                    msg = {
                        'employee_id': emp.id,
                        'date': datetime.now(),
                        'state': 'approve',
                        'note': 'Submit',
                    }
                    self.approval_message_ids = [(0, 0, msg)]

                # NOTE: or just simply check here before appending
                if emp:  # only append if the employee exists
                    lines.append((0, 0, data))

                # if there is group and limit >= total, this is the last approval
                # no need to process the next
                group = app_line.approval_group_id
                if group and group.amount_limit >= self.estimated_cost:
                    break

                # find line with parent job and level < current level, make
                # sure to sort DESC by level to take the bottom level if there
                # is any approval lines with 2 same user
                app_line = hierarchy.line_ids.filtered(
                    lambda x: x.job_id == parent and x.level < app_line.level
                ).sorted(key=lambda x: -x.level)

            self.approval_history_ids = lines

        # after approvals are assigned, set is_rejected to False
        self.is_rejected = False

    def button_send_approval_email(self):
        self._send_approval_email()
        self.is_resend = True

    def _construct_body(self, url, message='', forward=False):
        """ helper function to construct reply mail body """
        # NOTE: the template is left-justified
        forward_body = ''
        forward_note = ''
        if forward:
            forward_body = """Forward To: ||put email here||\n"""
            forward_note = 'Please put forward email between double pipes'

        # the body is plain text, but will eventually be encoded into HTML
        # quote the string to convert to html-encoded
        body = 'Action: %s\n%s\nNote:\n[[ notes here ]]\n\n%s'\
            'Please put the notes between brackets\n'\
            'Please do not change the encrypted url\n{{%s}}\n' % (
                message, forward_body, forward_note, url)
        body = urllib.parse.quote(body)
        return body

    def _construct_mail(self, url, body='', forward=False):
        """ helper function to construct reply mail """
        # result link consists of mailto, subject and body
        context = self._context
        subject = context.get('subject', '')
        mail_to = context.get('mail_to', '')
        body = self._construct_body(url, body, forward)
        res = 'mailto:%s?subject=%s&body=%s' % (mail_to, subject, body)
        return res

    def _get_approval_template(self):
        """ function to return mail template for approval """
        return 'ins_purchase_request_approval.mail_purchase_request_approval'

    def _get_question_template(self):
        """ function to return mail template for question """
        return 'ins_purchase_request_approval.mail_purchase_request_question'

    def _get_info_template(self):
        """ function to return mail template for info """
        return 'ins_purchase_request_approval.mail_purchase_request_info'

    def _get_fail_template(self):
        """ function to return mail template for fail """
        return 'ins_purchase_request_approval.mail_purchase_request_fail'

    def _send_approval_email(self):
        """ function to send approval email """

        # before sending mail, check if approval is completed to prevent spam
        if self._is_approval_completed():
            return True

        context = self._context

        # get forward employee from context
        forward_employee = context.get('forward_employee', False)

        approver_id = context.get('approver_id', False)
        approver_employee = False
        if approver_id:
            # remember to change to int
            approver_employee = self.env['hr.employee'].sudo().browse(int(approver_id))

        forwarder = context.get('forward_from', '')

        # find delegatee first if any then current approver
        curr = self._get_current_approval()

        prv = self.approval_history_ids.filtered(lambda x: x.state in VALID_STATES)
        prv = prv.sorted(key=lambda x: x.level)[:1].employee_id.name  # previous

        # the approving employee
        approver = forward_employee or approver_employee or self._get_delegatee() or self._get_current_approver()

        # get the current level
        current_level = self._get_current_level()

        nxt = self.approval_history_ids.filtered(
            lambda x: x.state not in VALID_STATES and x.id != curr.id and x.level < curr.level
        )
        nxt = nxt.sorted(key=lambda x: -x.level)[:1].employee_id.name

        date = self.date_start.strftime('%d/%m/%Y') if self.date_start else ''

        # try to check base url, possible comes from email, use ICP
        try:
            url_root = request.httprequest.url_root
            db = request.session.db
        except Exception as e:  # exception happens, get from ICP the web.base.url
            web_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url_root = '%s/' % web_url  # add trailing slash
            db = self.env.cr.dbname  # use db cursor name

        base_url = '%spurchase_request/do' % (url_root)
        url_dict = {
            'id': self.id,
            'approver': approver.sudo().id,
            'db': db,
            'forward': approver.sudo().work_email,  # forward from previous
            'level': current_level,
            'back_url': '',
        }

        apr_url_data = 'approve/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)
        rej_url_data = 'reject/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)
        ask_url_data = 'ask/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)
        ans_url_data = 'answer/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)
        aprfwd_url_data = 'approve_forward/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)
        fwd_url_data = 'forward/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)

        apr_url_data = _encode_url(apr_url_data)
        rej_url_data = _encode_url(rej_url_data)
        ask_url_data = _encode_url(ask_url_data)
        ans_url_data = _encode_url(ans_url_data)
        aprfwd_url_data = _encode_url(aprfwd_url_data)
        fwd_url_data = _encode_url(fwd_url_data)

        approve_url = '%s/%s' % (base_url, apr_url_data)
        reject_url = '%s/%s' % (base_url, rej_url_data)
        ask_url = '%s/%s' % (base_url, ask_url_data)
        ans_url = '%s/%s' % (base_url, ans_url_data)
        aprfwd_url = '%s/%s' % (base_url, aprfwd_url_data)
        fwd_url = '%s/%s' % (base_url, fwd_url_data)

        mail_from = self._get_email_alias()  # use alias to send email

        # approval links without having to call domain. Add default note
        mail_context = {
            'mail_to': mail_from,
            'subject': self.name,
        }
        approve_link = self.with_context(mail_context)._construct_mail(apr_url_data, 'Approve')
        reject_link = self.with_context(mail_context)._construct_mail(rej_url_data, 'Reject')
        ask_link = self.with_context(mail_context)._construct_mail(ask_url_data, 'Ask')
        answer_link = self.with_context(mail_context)._construct_mail(ans_url_data, 'Answer')
        aprfwd_link = self.with_context(mail_context)._construct_mail(aprfwd_url_data, 'Approve and Forward', True)
        fwd_link = self.with_context(mail_context)._construct_mail(fwd_url_data, 'Forward', True)

        note = curr.note or ''
        mail_template = self._get_approval_template()
        if context.get('question'):  # change to question template
            mail_template = self._get_question_template()
            # and change the approver to requested_by, use superuser access
            # to handle portal access
            # TODO might want to change this, not only the requestor but anyone
            approver = self.with_user(SUPERUSER_ID).requested_by.employee_id

        if context.get('answer'):
            # take note from the latest message
            note = self._get_latest_message()

        try:
            template_id = self.env.ref('%s' % mail_template)
        except ValueError:
            template_id = False

        # get attachment or empty list if none
        attachment = self._get_attachment() or []
        if len(attachment) != 0:
            attachment = [(6, 0, attachment.ids)]
            # attachment = [(4, att.id) for att in attachment]

        if template_id:
            approver = approver.sudo().work_email  # get the email
            template_id.attachment_ids = attachment
            template_id.with_context(
                mail_from=mail_from,
                approver=approver,
                forwarder=forwarder,
                approve_url=approve_url,
                reject_url=reject_url,
                ask_url=ask_url,
                ans_url=ans_url,
                date=date,
                aprfwd_url=aprfwd_url,
                fwd_url=fwd_url,
                approve_link=approve_link,
                reject_link=reject_link,
                ask_link=ask_link,
                answer_link=answer_link,
                asker=curr,
                aprfwd_link=aprfwd_link,
                fwd_link=fwd_link,
                prev_approver=prv or '',
                next_approver=nxt or '',
                note=note,
                is_answer=context.get('answer'),
            ).send_mail(self.id)

            # cleanup, but use 3 instead of 2 triplet. 2 is for removing, this
            # could affect the actual attachment in the database
            # template_id.attachment_ids = [(2, x.id) for x in template_id.attachment_ids]
            template_id.attachment_ids = [(3, x.id) for x in template_id.attachment_ids]

        return True

    def _send_info_email(self):
        """ function to send info email to requestor """
        # this email will always be sent to the requestor
        context = self._context

        approver = context.get('approver', '')
        message = context.get('message', '')
        mail_from = self._get_email_alias()  # use alias to send email

        template = self._get_info_template()
        try:
            template_id = self.env.ref('%s' % template)
        except ValueError:
            template_id = False

        if template_id:
            approver = approver.sudo().name  # get name
            template_id.with_context(
                mail_from=mail_from,
                approver=approver,
                message=message,
            ).send_mail(self.id)

        return

    def _send_fail_email(self):
        """ function to send failure email """
        ctx = self._context

        date = self.date_start.strftime('%d/%m/%Y') if self.date_start else ''
        note = ctx.get('note', '')

        mail_from = self._get_email_alias()
        mail_to = ''

        employee = ctx.get('employee', False)

        if not employee:  # no approver found, use mail_to passed
            mail_to = ctx.get('mail_to')  # handles error if encrypted url changes
        else:
            mail_to = employee.work_email

        mail_template = self._get_fail_template()
        try:
            template_id = self.env.ref('%s' % mail_template)
        except ValueError:
            template_id = False

        if template_id:
            template_id.with_context(
                mail_from=mail_from,
                mail_to=mail_to,
                date=date,
                note=note,
            ).send_mail(self.id)
        return True

    def _get_latest_message(self):
        """ helper function to get the latest message """
        res = ''
        sql = """
            SELECT note
            FROM purchase_request_message
            WHERE state = 'answer'
            ORDER BY date DESC
            LIMIT 1
        """
        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchone()
        if res and res is not None:
            res = res['note']
        return res

    def _get_attachment_report_id(self):
        """ function to get attachment report id in string """
        return 'purchase_request.report_purchase_request'

    def _get_attachment(self):
        """ function to get attachment id to add to email """
        attachment = False
        # get the attachment
        rid = self.env.ref(self._get_attachment_report_id())._render_qweb_pdf(self.id)

        # then encode it
        report_data = base64.b64encode(rid[0])

        # create attachment
        vals = {
            'name': self.name,
            'type': 'binary',
            'datas': report_data,
            'store_fname': report_data,
            'mimetype': 'application/x-pdf',
        }
        attachment = self.env['ir.attachment'].create(vals)
        return attachment

    def _get_forward_employee(self, email):
        """ helper function to get the forwarded employee based on email """
        # NOTE: condition 1: make sure forwarded employee is in the
        # hierarchy and with level > current
        # condition 2: if no employee found with such email, look from user
        employee = False
        # get current level first
        current = self._get_current_approver()
        current_line = self.approval_history_ids.filtered(
            lambda x: x.employee_id == current).sorted(key=lambda x: x.level)
        if current_line and len(current_line) > 1:
            current_line = current_line[0]

        line = self.approval_history_ids.filtered(
            lambda x: x.employee_id.work_email == email and x.level > current_line.level
        )
        if line:
            employee = line.with_user(SUPERUSER_ID).employee_id

        # then try to check if the email is in hierarchy or not, if not then
        # find from users
        if not self.approval_history_ids.filtered(lambda x: x.employee_id.work_email == email):
            sql = """
                SELECT id
                FROM hr_employee
                WHERE work_email = '%s' AND (company_id = %s OR company_id IS NULL)
            """ % (email, self.company_id.id)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchone()
            if res and res is not None:
                # access using superuser to handle portal access
                employee = self.with_user(SUPERUSER_ID).env['hr.employee'].browse(int(res['id']))
        return employee

    def _get_delegatee(self):
        """ helper function to get delegatee of the current approver """
        current = self._get_current_approver()
        today = date.today()
        domain = [
            ('module', '=', 'purchase.request'),
            ('delegator_id', '=', current.id),
            ('date_from', '<=', today),
            ('date_to', '>=', today),
            ('company_id', '=', self.company_id.id),
        ]
        delegation = self.env['approval.delegation'].search(
            domain, order='date_from asc', limit=1)
        return delegation.delegatee_id

    def _is_delegatee(self, employee):
        """ function to check if the employee is delegatee """
        # find delegation record having employee with employee in date range
        # with purchase.order module

        # directly return False if user is not connected to employee
        if not employee:
            return False

        # a delegatee could only approved if a delegator exists
        # so, find the current approver
        current = self._get_current_approver()

        today = date.today()
        domain = [
            ('module', '=', 'purchase.request'),
            ('delegator_id', '=', current.id),
            ('delegatee_id', '=', employee.id),
            ('date_from', '<=', today),
            ('date_to', '>=', today),
            ('company_id', '=', self.company_id.id),
        ]
        delegation = self.env['approval.delegation'].search_count(domain)
        return delegation  # True if found

    def _complete_approval(self):
        """ helper function to complete approval with limit """
        # if the approval record has limit and the amount of the purchase is
        # below limit, then everyone with level lesser than this approver
        # will be considered as done
        cur_limit = self._get_current_limit()
        cur_approval = self._get_current_approval()
        amount = self.estimated_cost
        # limit is greater than total, approve all the rest
        if cur_limit >= amount:
            rest = self.approval_history_ids.filtered(
                lambda x: x.level < cur_approval.level)
            rest.write({'state': 'approve', 'date': datetime.now()})
        return True

    def button_user_approve(self):
        """ function to approve, called from button """
        # handles the manual approval in form, pass active user
        context = self._context  # context is filled with state, note

        employee = False

        # check context
        if context.get('employee'):
            employee = context.get('employee')

        # no employee found still, force to use active session
        if not employee:
            employee = self.env.user.employee_id

        if employee:  # failsafe
            self.with_context(context).action_user_approve(employee)
        return True

    def _is_current_limit(self):
        """ helper function to check if current approval has limit """
        cur = self._get_current_approval()
        return cur and cur.approval_group_id and cur.approval_group_id.amount_limit

    def _get_current_limit(self):
        """ helper function to get the current approval limit """
        cur = self._get_current_approval()
        return cur.approval_group_id.amount_limit if cur.approval_group_id else 0

    def _is_current_approver(self, employee):
        """ function to check if employee is current approver """
        # current approval is the latest (sort desc, get the latest employee)
        return self._get_current_approver() == employee

    def _get_current_approver(self):
        """ helper function to get the latest employee approving """
        # current approval is the latest (sort desc, get the latest employee)
        latest = self._get_current_approval()
        return latest[:1].employee_id

    def _get_current_approval(self):
        """ helper function to get the latest approval record """
        latest = self.approval_history_ids.filtered(lambda x: x.state not in VALID_STATES)
        latest = latest.sorted(key=lambda x: -x.level)
        return latest[:1]  # return the latest, exists or not

    def _get_current_level(self):
        """ helper function to get the latest approval level """
        latest = self.approval_history_ids.filtered(lambda x: x.state not in VALID_STATES)
        latest = latest.sorted(key=lambda x: -x.level)
        # return the latest level if found, else return -1
        return latest[:1].level if latest and latest[:1] else -1

    def _shift_level(self, employee, current):
        """ helper function to shift level in purchase_request_approval """
        # store current level
        current_level = current.level

        # CRAZY NOTE: do something crazy here, this function will be called if and
        # only if the forward happen. Means, everytime shift happens, we just need to
        # add 2 new records with sender above

        # from the current record, find all purchase.request.approval with level
        # greater than equal to current level
        # NOTE: with the change of flow, shift to +2
        lines = self.approval_history_ids.filtered(lambda x: x.level >= current.level)
        for line in lines:
            # line.level += 1
            line.level += 2

        # then add to purchase_request_approval using employee, with current_level
        # and shift level will happen for forward, so is_forward is True
        # NOTE: due to change of flow, add new record using current employee
        # using current level, the forwarded employee using current_level + 1
        cur_vals = {
            'employee_id': current.employee_id.id,
            'state': 'draft',
            'level': current_level,
        }
        fwd_vals = {
            'employee_id': employee.id,
            'state': 'draft',
            'level': current_level + 1,
            'is_forward': True,
        }
        self.approval_history_ids = [(0, 0, cur_vals), (0, 0, fwd_vals)]
        return True

    def action_user_approve(self, employee):
        """ function to approve record by using employee """
        # check if the current approval is permitted for "this" employee
        # permission is granted if:
        # 1. previous states are not draft, and date is filled
        # 2. OR if user is in date of delegation by someone

        context = self._context
        state = context.get('state')
        note = context.get('note')
        approver_id = context.get('approver_id')
        is_forward = context.get('is_forward', False)
        forward_to = context.get('forward_to')
        forward_from = context.get('forward_from')
        forward_employee = False
        current_approval = self._get_current_approval()  # for adding
        add_note = ''  # this is to store forward information

        # before doing anything, check state first if forward or approve
        # valid thing: state is approve/forward and forward email exists
        if is_forward and state in ('approve', 'forward'):
            forward_employee = self._get_forward_employee(forward_to)
            add_note = '(Forward)'
            if not forward_employee:  # not valid email, send fail email
                fail_msg = 'Forward E-mail is invalid (not in hierarchy or above this level)!'
                fail_context = {
                    'note': fail_msg,
                    'employee': employee,
                }
                self.with_context(fail_context)._send_fail_email()
                return True

        vals = {
            'employee_id': employee.id,
            'date': datetime.now(),
            'state': state,
            'note': '%s %s' % (note, add_note),
        }

        if self._is_current_approver(employee) or self._is_delegatee(employee):
            # make state to approve_delegate if approving officer is delegeatee
            if self._is_delegatee(employee):
                vals['state'] = 'approve_delegate'

            # if the current has limit, TRY to complete approval
            if self._is_current_limit():
                self._complete_approval()

            # NOTE: heavy special case, if user chooses to forward, meaning
            # the state will become submit. This will make sure _get_current_approval()
            # function will always present the last forwarding employee
            # 馬鹿人
            # if forward_to:
            #     vals['state'] = 'draft'
            self._get_current_approval().write(vals)
            _logger.info('Current Approver is correct')
            _logger.info(employee)
            _logger.info(vals)

        # regardless of what happen, always record message
        self.approval_message_ids = [(0, 0, vals)]

        # if ask, then send mail to requestor
        if state == 'ask':
            # but we also add new things: target approver from approver_id
            self.with_context({
                'question': True,
                'approver_id': approver_id
            })._send_approval_email()
            return True

        # if answer, then send mail to approver with note
        if state == 'answer':
            self.with_context({'answer': True})._send_approval_email()
            return True

        # before checking to done, always try to reject
        if self._is_reject_found():
            # set is_rejected and empty out selected_approver_id
            self.write({'is_rejected': True, 'selected_approver_id': False})
            self.button_rejected()
            # send info email to requestor
            self.with_context({'approver': employee, 'message': 'Reject'})._send_info_email()
            return True

        # always check is approvals are completed, then call the button_approve
        if self._is_approval_completed():
            self.button_approved()
            # send info email to requestor
            self.with_context({'approver': employee, 'message': 'Approve'})._send_info_email()
        else:  # still not completed, send email
            # put forward check here to handle approve and forward
            # if forward, then send mail to forward
            if is_forward and forward_employee:
                # add to purchase.order.approval
                self._shift_level(forward_employee, current_approval)

                ctx = {
                    'forward_employee': forward_employee,
                    'forward_from': forward_from,
                }
                self.with_context(ctx)._send_approval_email()
            else:  # just send email
                self._send_approval_email()
        return True

    def _generate_link(self, type):
        """ helper function to generate link based on type """
        url = ''
        approver = self._get_current_approver()
        current_level = self._get_current_level()
        params = self._context.get('params', {})
        back_url = request.httprequest.url_root
        if params:
            back_url += 'web#' + urllib.parse.urlencode(params)

        base_url = '%spurchase_request/do' % (request.httprequest.url_root)
        db = request.session.db
        url_dict = {
            'type': type,
            'id': self.id,
            'approver': approver.id,
            'db': db,
            'forward': approver.work_email,  # forward from previous
            'level': current_level,
            'back_url': _encode_url(back_url),
        }
        url_data = '%(type)s/%(id)s/%(approver)s/%(db)s/%(forward)s/%(level)s/%(back_url)s' % (url_dict)
        url_data = _encode_url(url_data)
        url = '%s/%s' % (base_url, url_data)
        return url

    def button_action(self):
        """ function to open portal to approve """
        state = self._context.get('state')
        url = self._generate_link(state)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    def button_to_approve(self):
        """ inherit function to generate approval history """
        res = super(PurchaseRequest, self).button_to_approve()
        if self.company_id.purchase_dynamic_approval:
            if not self.requested_by.employee_id:
                raise ValidationError('Please connect the user with the employee')

            self._check_alias()  # always check for the existence of alias

            self._assign_approval()

            # before sending email, make sure to check the limit
            self._check_limit()

            self._send_approval_email()
        return res

    def button_approved(self):
        """ inherit function to check if there incomplete approval """
        res = super(PurchaseRequest, self).button_approved()
        if not self._is_approval_completed():
            return True
        return res

    def _is_approval_completed(self):
        """ function to check if all approvals are completed """
        # return False if there is any record that has not approve
        # for this to complete, only the hierarchical records are considered
        return not any([x.state not in VALID_STATES for x in self.approval_history_ids])

    def _is_reject_found(self):
        """ function to check if any approval contains reject status """
        return any([x.state == 'reject' for x in self.approval_history_ids])

    def get_approval_data(self):
        """ function to return approval data """
        res = {}
        context = self._context  # context is filled with state, note
        _logger.info('Context in get_approval_data')
        _logger.info(context)
        employee = False
        employee = context.get('employee', self.env.user.employee_id)

        level = context.get('level', -1)

        # get active_user from context to check
        active_user = context.get('active_user', False)
        active_emp = employee
        if active_user:
            active_emp = active_user.with_user(SUPERUSER_ID).employee_id

        # if self.env.user:
        #     employee = self.env.user.employee_id
        # else:
        #     employee = context.get('employee', False)

        # proceed only if the employee != current approver
        # NOTE: need to check if there is delegatee
        current = self._get_delegatee() or self._get_current_approver()
        if (employee != current) or (current != active_emp):
            sql = """
                SELECT COALESCE(note, '') AS note,
                date AS date
                FROM purchase_request_approval
                WHERE state IN ('approve', 'approve_delegate', 'forward')
                AND employee_id = %s AND request_id = %s AND level >= %s
            """ % ((active_emp.id or employee.id), self.id, int(level))
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchone()

        approval = self._get_current_approval()
        states = VALID_STATES + ('reject',)
        if employee == current and approval.state in states:
            res = {
                'date': approval.date,
                'note': approval.note,
            }

        return res

    def _check_limit(self):
        """ function to check limit """
        # NOTE: limit data should be checked from the last approval
        # from the hierarchy, sort by level and take firs
        data = self.hierarchy_id.line_ids.sorted(key=lambda x: x.level)
        data = data[0] if data else False
        if data:
            approval_group = data.approval_group_id
            if approval_group and approval_group.amount_limit < self.estimated_cost:
                msg = 'Approval Max Limit is below the Amount! Please check'
                raise ValidationError(msg)

    def _check_alias(self):
        """ function to check the existence of email alias for model """
        # find alias with purchase.request.cache model
        domain = [('alias_model_id.model', '=', 'purchase.request.cache')]
        alias = self.env['mail.alias'].search(domain)
        if not alias:
            raise ValidationError('Please configure an email alias')

        # or if valid, check the email name using regex
        import re
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        match = re.match(pattern, alias.display_name)
        if not match:
            raise ValidationError('Invalid Email format used in alias!')

    def _get_email_alias(self):
        """ function to get email alias """
        domain = [('alias_model_id.model', '=', 'purchase.request.cache')]
        alias = self.env['mail.alias'].search(domain)
        return alias.display_name

    def _process_url(self, url, note=''):
        """ helper function to process url """
        success = True  # assume it is successful
        employee = False
        mail_to = ''  # mail_to is to handle the empty recipient
        context = self._context

        mail_forward = context.get('mail_forward', '')

        # try to decode url
        url = _decode_url(url)
        if not url:
            # in case of parse error, there will be no user parsed, instead
            # pass the mail to send
            success = False
            mail_to = context.get('mail_to')
            note = 'You might have accidentally change the subject containing unique encrypted ID'

        if success:
            # parse url, set db, find record, check validity and store result
            r_type, pid, eid, _, _, level, _ = url.split('/')

            if r_type == 'approve_forward':  # approve & forward, force approve
                r_type = 'approve'

            domain = [('id', '=', pid)]  # find purchase order based on pid
            purchase = self.env['purchase.request'].sudo().search(domain)

            if purchase:  # found, pass context then approve
                employee = self.env['hr.employee'].browse(int(eid))
                is_answer = r_type == 'answer'
                # answering person will always be the requestor
                # if is_answer:
                #     requestor = purchase.with_user(SUPERUSER_ID).requested_by
                #     employee = requestor.employee_id or requestor.employee_ids[0]

                # always check for approval data. If exists, show failed
                # but remember, answering user will be the requestor, so exclude
                # the checking when answering
                ctx = {'employee': employee, 'level': level}
                _logger.info('Employee to send: ')
                _logger.info(employee)
                _logger.info(ctx)
                approved = purchase.with_context(ctx).get_approval_data()
                if approved and approved is not None and not is_answer:
                    success = False
                    process_date = approved['date']
                    note = 'You have already approved/rejected this record on %s' % process_date

                if success:
                    ctx = {
                        'employee': employee,
                        'is_forward': True if mail_forward else False,
                        'forward_to': mail_forward,
                        'forward_from': context.get('mail_to') if mail_forward else '',
                        'state': r_type,
                        'note': note,
                    }
                    purchase.with_context(ctx).button_user_approve()
            else:
                success = False

        # send fail mail if not successful
        if not success:
            ctx = {
                'note': note,
                'employee': employee,
                'mail_to': mail_to,
            }
            self.with_context(ctx)._send_fail_email()
