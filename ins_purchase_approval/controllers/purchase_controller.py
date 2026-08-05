from base64 import urlsafe_b64decode as b64dec
import urllib.parse
import zlib
from odoo import http, SUPERUSER_ID
from odoo.http import request


def _decode_url(data: str) -> str:
    # accept data, decode
    return zlib.decompress(b64dec(data)).decode()


class PurchaseController(http.Controller):
    @http.route('/purchase/do/<string:data>', type='http', auth='none', website=True, csrf=False)
    def purchase_approve(self, data, **kwargs):
        """ endpoint to do purchase approval """

        url_data = data
        url_data = urllib.parse.unquote(url_data)  # unquote string
        param_data = _decode_url(url_data)

        r_type, pid, _, db, forwarder, _ = param_data.split('/')

        request.session.db = db  # use the db

        # check if r_type is forward
        is_forward = False
        if r_type in ('approve_forward', 'forward'):
            is_forward = True
        else:
            forwarder = ''

        values = {}
        template = 'portal_purchase_approval_reply'

        domain = [('id', '=', pid)]  # find purchase order based on pid
        purchase = request.env['purchase.order'].sudo().search(domain)

        values.update({
            'url': data,
            'purchase': purchase,
            'is_forward': is_forward,
            'forwarder': forwarder,
        })

        response = request.render('ins_purchase_approval.%s' % template, values)
        response.headers['X-Frame-Options'] = 'DENY'

        return response

    @http.route('/purchase/note/', type='http', auth='none')
    def purchase_post_question(self, **kwargs):
        # always pass success page for submitting question/answer
        success = True
        values = {}

        body = request.params
        url = body.get('url')
        url = urllib.parse.unquote(url)  # unquote string
        note = body.get('note')
        mail_forward = body.get('mail_forward')

        param_data = _decode_url(url)
        if success:
            r_type, pid, eid, db, forwarder, level = param_data.split('/')
            request.session.db = db  # use the db

            if r_type not in ('approve_forward', 'forward'):
                forwarder = ''

            if r_type == 'approve_forward':  # approve & forward, force approve
                r_type = 'approve'

            domain = [('id', '=', pid)]  # find purchase order based on pid
            purchase = request.env['purchase.order'].sudo().search(domain)

            # mail_forward exists, check existence
            if mail_forward:
                forward_employee = purchase._get_forward_employee(mail_forward)
                if not forward_employee:
                    success = False
                    values = {
                        'msg': 'Warning',
                        'note': '%s is not registered as employee' % mail_forward,
                    }

            if purchase and success:  # found, pass context then approve
                employee = request.env['hr.employee'].browse(int(eid))
                is_answer = r_type == 'answer'
                # answering person will always be the requestor
                if is_answer:  # force with superuser to access employee
                    # portal access needs to use superuser due to the nature of
                    # accessing employee_id
                    requestor = purchase.with_user(SUPERUSER_ID).request_user_id
                    employee = requestor.employee_id or requestor.employee_ids[0]

                # always check for approval data. If exists, show failed
                # but remember, answering user will be the requestor, so exclude
                # the checking when answering
                act_user = request.env['res.users'].browse(request.session.uid)
                ctx = {'employee': employee, 'level': level, 'active_user': act_user}
                approved = purchase.with_context(ctx).get_approval_data()
                if approved and approved is not None and not is_answer:
                    success = False
                    values['msg'] = 'Approved On '
                    values.update(approved)

                if success:
                    ctx = {
                        'employee': employee,
                        'is_forward': True if mail_forward else False,
                        'forward_to': mail_forward,
                        'forward_from': forwarder,
                        'state': r_type,
                        'note': note,
                    }
                    purchase.with_context(ctx).button_user_approve()

        template = 'portal_purchase_approval_%s' % ('success' if success else 'failed')
        response = request.render('ins_purchase_approval.%s' % template, values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
