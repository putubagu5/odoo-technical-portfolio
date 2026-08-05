from datetime import datetime
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.osv import expression


class PmisBudgetDetail(models.Model):
    _name = 'pmis.budget.detail'
    _description = 'Budget Detail'

    line_id = fields.Many2one('pmis.budget.line', 'Related Line', ondelete='cascade')
    no = fields.Integer('Episode No')
    name = fields.Char('Episode Name')
    code = fields.Char('Episode Code')
    amount = fields.Float('Amount')


class PmisBudgetLine(models.Model):
    _name = 'pmis.budget.line'
    _description = 'Input Budget'
    _rec_name = 'expenditure_type_id'

    no = fields.Integer('No', default=1)
    line_id = fields.Many2one('pmis.budget', 'Line ID',
                              ondelete='cascade', index=True,
                              required=False)
    review_line_id = fields.Many2one('pmis.budget.review', 'Review Line ID',
                                     ondelete='cascade', index=True)
    expenditure_type_id = fields.Many2one('project.expenditure.type',
                                          'Expenditure Type')
    subcategory_id = fields.Many2one('project.expenditure.subcategory',
                                     'Expenditure Subcategory',
                                     related='expenditure_type_id.category_id',
                                     store=True)
    category_id = fields.Many2one('project.expenditure.category',
                                  'Expenditure Category',
                                  related='subcategory_id.expenditure_category_id',
                                  store=True)
    item_code = fields.Char('Item Name', related='expenditure_type_id.name', store=True)
    item_name = fields.Char('Item Code', related='expenditure_type_id.code', store=True)
    description = fields.Text('Description')
    pax = fields.Integer('Pax')
    eps = fields.Integer('Eps')
    day = fields.Integer('Day')
    rate = fields.Float('Rate')
    average_by_eps = fields.Float('Average by Eps', compute='_compute_budget_average')
    budget = fields.Float('Budget', compute='_compute_budget_average')
    amount_budget_in = fields.Float('Budget In')
    amount_budget_out = fields.Float('Budget Out')
    amount_budget_line = fields.Float('Total Budget Line',
                                      compute='_compute_amount_budget_line')
    # planned_budget = fields.Float('Planned Budget')
    actual_budget = fields.Float('Actual Budget', compute='_compute_actual_budget')
    pr_reserve_amount = fields.Float('PR Reserve', compute='_compute_pr_reserve')
    pr_reserve_draft_amount = fields.Float('PR Reserve Include Draft', compute='_compute_pr_reserve_draft')
    po_reserve_amount = fields.Float('PO Reserve', compute='_compute_po_reserve')
    remaining_amount = fields.Float(string="Budget Remaining", compute='_compute_budget_remaining')
    remaining_draft_amount = fields.Float(string="Budget Remaining Include Draft", compute='_compute_budget_remaining_draft')
    # purchase_request_ids = fields.One2many('purchase.request.line', 'crossovered_budget_line_id',
    #                                        string="Purchase Request Lines")
    remarks = fields.Text('Remarks')
    do_copy = fields.Boolean('Copy?', default=False, copy=False)
    detail_ids = fields.One2many('pmis.budget.detail', 'line_id', 'Details')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    project_pr_line_ids = fields.One2many('project.pr.line', 'budget_line_id',
                                          'Project PR Lines')
    main_project_id = fields.Many2one('pmis.main.project',
                                      'Main Project',
                                      related='line_id.main_project_id',
                                      store=True)
    program_id = fields.Many2one('pmis.program',
                                 'Program',
                                 related='line_id.program_id',
                                 store=True)
    task_id = fields.Many2one('pmis.project.task',
                              'Task (Phase)',
                              related='line_id.task_id',
                              store=True)

    @api.constrains('eps')
    def _check_eps(self):
        """ constrains function to check episode """
        # NOTE: prevent validation if it is a review
        review = self._context.get('review', False)
        for rec in self:
            if rec.eps > rec.line_id.episode_number and not review:
                raise Warning('Episode number in line exceeds the limit.')

    @api.depends('project_pr_line_ids', 'project_pr_line_ids.line_id', 'po_reserve_amount', 'actual_budget')
    def _compute_pr_reserve(self):
        """ compute function to get reserve amount """
        # NOTE: PR Reserve rules:
        # 1. PR Line states must be in to_approve, approved OR
        # 2. PO Line states must be in draft, cancel OR no PO Line found
        pr_line_states = ('to_approved', 'approved', 'done')
        po_line_states = ('draft', 'cancel')
        for rec in self:
            line = rec.project_pr_line_ids.filtered(
                lambda x: x.line_id.request_state in pr_line_states
                and (x.line_id.purchase_state in po_line_states or not x.po_line_id))
            amount = sum(line.mapped('line_id.estimated_cost'))
            rec.pr_reserve_amount = amount

    @api.depends('project_pr_line_ids', 'project_pr_line_ids.line_id', 'po_reserve_amount', 'actual_budget')
    def _compute_pr_reserve_draft(self):
        """ compute function to get reserve amount in draft """
        # NOTE: PR Reserve Draft rules:
        # 1. PR Line states must be in draft, rejected
        pr_line_states = ('draft', 'rejected')
        for rec in self:
            line = rec.project_pr_line_ids.filtered(
                lambda x: x.line_id.request_state in pr_line_states)
            amount = sum(line.mapped('line_id.estimated_cost'))
            rec.pr_reserve_draft_amount = amount

    @api.depends('project_pr_line_ids', 'project_pr_line_ids.po_line_id', 'actual_budget')
    def _compute_po_reserve(self):
        """ compute function to get reserve amount """
        # NOTE: po_reserve_amount is based on project_pr_line_ids, connected to
        # po_line_id, but only the one having the state purchase or done
        valid_states = ('to approve', 'purchase', 'done')
        for rec in self:
            po_reserve = 0
            actual_budget = 0
            lines = rec.project_pr_line_ids.mapped('po_line_id')
            valid_lines = lines.filtered(lambda x: x.state in valid_states)
            # NOTE: this logic below is still experimental, to simulate movement of
            # reserves amount into each other
            if valid_lines:
                po_reserve = sum(valid_lines.mapped('price_subtotal'))
                actual_budget = rec.actual_budget
            # NOTE: the summed field could change
            rec.po_reserve_amount = po_reserve - actual_budget

    # this function is temporary to check amount for actual budget
    @api.depends('project_pr_line_ids', 'project_pr_line_ids.move_line_id')
    def _compute_actual_budget(self):
        """ compute function to get reserve amount """
        # NOTE: actual_budget is based on project_pr_line_ids, connected to
        # account_line_id, but only the one having the state confirmed or assigned
        # valid_states = ('confirmed', 'assigned')
        for rec in self:
            lines = rec.project_pr_line_ids.mapped('move_line_id')
            valid_lines = lines.filtered(lambda x: x.state == 'done')
            # NOTE: the summed field could change
            rec.actual_budget = sum(valid_lines.mapped('amount_total'))

    @api.depends('amount_budget_in', 'amount_budget_out', 'budget')
    def _compute_amount_budget_line(self):
        """ compute function to get amount_budget_line """
        for rec in self:
            rec.amount_budget_line = rec.budget + rec.amount_budget_in - rec.amount_budget_out

    @api.depends('pax', 'eps', 'day', 'rate', 'line_id.episode_number')
    def _compute_budget_average(self):
        """ compute function to calculate budget and average per episode """
        for rec in self:
            budget = 0
            eps_number = 1
            if rec.pax and rec.eps and rec.day and rec.rate:
                budget = rec.pax * rec.eps * rec.day * rec.rate
                eps_number = rec.line_id.episode_number or 1
            rec.budget = budget
            rec.average_by_eps = budget / eps_number

    @api.depends('amount_budget_line', 'pr_reserve_amount', 'po_reserve_amount', 'actual_budget')
    def _compute_budget_remaining(self):
        """ compute function to calculate budget remaining """
        for rec in self:
            rec.remaining_amount = rec.amount_budget_line - rec.pr_reserve_amount - rec.po_reserve_amount - rec.actual_budget

    @api.depends('amount_budget_line', 'pr_reserve_amount', 'pr_reserve_draft_amount', 'po_reserve_amount', 'actual_budget')
    def _compute_budget_remaining_draft(self):
        """ compute function to calculate budget remaining """
        for rec in self:
            rec.remaining_draft_amount = rec.amount_budget_line - rec.pr_reserve_draft_amount - rec.pr_reserve_amount - rec.po_reserve_amount - rec.actual_budget

    def _prepare_distribution(self):
        """ function to prepare rate distribution """
        # get details and assign
        self.ensure_one()
        details = []
        if not details:
            total = self.budget
            # NOTE: the number for line is taken from task_id.range_start
            task = self.line_id.task_id

            # sort the task ids based on episode_no
            subtasks = task.episode_ids.sorted(lambda x: x.episode_no) if task else []

            # loop the range, take the index and assign to episode
            if task.is_batch is True:
                for idx, x in enumerate(range(task.range_end, task.range_end + 1)):
                    amt = self.budget
                    total -= amt
                    dt = {
                        'code': subtasks[idx].episode_code,
                        'name': subtasks[idx].episode_name,
                        'no': subtasks[idx].episode_no,
                        'amount': amt if total >= 0 else 0,
                    }
                    details.append((0, 0, dt))

            if task.is_batch is False:
                for idx, x in enumerate(range(task.range_start, task.range_end + 1)):
                    amt = self.budget / self.eps
                    total -= amt
                    dt = {
                        'code': subtasks[idx].episode_code,
                        'name': subtasks[idx].episode_name,
                        'no': subtasks[idx].episode_no,
                        'amount': amt if total >= 0 else 0,
                    }
                    details.append((0, 0, dt))

        return details

    def _process_distribution(self):
        """ function to process multiple records' distribution """
        for rec in self:
            details = [(2, x.id) for x in rec.detail_ids]
            prepared_data = rec._prepare_distribution()
            details += prepared_data
            rec.detail_ids = details

    def action_distribute(self):
        """ function to open Distribution wizard """
        # get details and assign
        details = self._prepare_distribution()
        action = {
            'name': 'Rate Distribution',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.pmis.budget.line',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_line_id': self.id,
                'default_detail_ids': details,
            }
        }
        return action


class PmisBudget(models.Model):
    _name = 'pmis.budget'
    _description = 'PMIS Budget'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Text('Description', copy=False)
    program_id = fields.Many2one(
        'pmis.program', string="Program")
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project')
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic Account',
                                          related='program_id.analytic_account_id')
    department_type_id = fields.Many2one(
        'pmis.departement.type', 'Department Type',
        domain='[("analytic_account_id", "=", analytic_account_id)]')
    date_shoot_start = fields.Date('Estimate Shoot Date', related='task_id.date_shoot_start')
    date_shoot_end = fields.Date('Until', related='task_id.date_shoot_end')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    range_start = fields.Integer('Episode Range', related='task_id.range_start')
    range_end = fields.Integer('To', related='task_id.range_end')
    episode_number = fields.Integer('Episode Number', related='task_id.episode_sum')
    day_number = fields.Integer('Day Number', related='task_id.day_number')
    duration = fields.Integer('Duration (Minutes)', related='task_id.duration')
    task_id = fields.Many2one('pmis.project.task', 'Task (Phase)')
    manager_task_id = fields.Many2one('hr.employee', 'Manager', related='task_id.manager_id')
    user_manager_task_id = fields.Many2one('res.users', 'User Manager', related='task_id.manager_id.user_id')
    button_visible = fields.Boolean(compute='_compute_button_visible', string="Visible Button")
    task_status = fields.Selection([
        ('draft', 'Incomplete/Draft'),
        ('submit', 'Submitted'),
        ('verify', 'Verified'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], 'Status', default='draft', tracking=True)
    budget_ids = fields.One2many(
        'pmis.budget.line',
        'line_id',
        string="Budget Lines")
    budget_info_ids = fields.One2many(
        'pmis.budget.line',
        'line_id',
        string="Budget Info Lines")
    total_budget = fields.Float(
        compute="_compute_total_budget",
        string="Total Budget",
    )
    total_remaining = fields.Float(
        compute="_compute_total_remaining",
        string="Total Remaining Budget",
    )
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    group_id = fields.Many2one(
        'project.group.type', 'Group',
        related='task_id.group_type_id', store=True)
    expenditure_ids = fields.Many2many(
        'project.expenditure.type',
        'Expenditure Type',
        compute='_get_expenditure_id')
    venue_names = fields.Char(
        string="Venue Names", compute='_compute_venue_names')
    unit_pm_id = fields.Many2one(
        'hr.employee', 'Unit PM',
        domain='[("analytic_account_id", "=", analytic_account_id)]')
    # info_ids = fields.One2many('pmis.budget.info', 'budget_id', 'Info')

    def button_copy(self):
        """ function to copy all lines with do_copy = True """
        for rec in self:
            lines = rec.budget_ids.filtered(lambda x: x.do_copy)
            if lines:
                lines.copy()

    # def copy(self, default=None):
    #     self.ensure_one()
    #     default = dict(default or {})
    #     default.update({
    #         'budget_ids': self.budget_ids,
    #         })

    #     return super(PmisBudget, self).copy(default)

    def button_search_budget(self):
        self.ensure_one()
        return {
            "name": _("Search Budget Line"),
            "view_mode": "form",
            "res_model": "pmis.search.budget.lines",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {'default_budget_id': self.id},
        }

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.program_id.code}] {rec.program_id.name}'
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('program_id.code', operator, name), ('program_id.name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('budget_ids', []):  # check if project_ids exist
            lines = vals.get('budget_ids', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                line[2].update({'no': idx + 1})
        res = super(PmisBudget, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(PmisBudget, self).write(vals)
        # find project_ids, rewrite the line number
        for idx, line in enumerate(self.budget_ids):
            line.no = idx + 1
        return res

    @api.depends("budget_ids", "budget_ids.amount_budget_line")
    def _compute_total_budget(self):
        for rec in self:
            rec.total_budget = sum(rec.budget_ids.mapped('amount_budget_line'))

    @api.depends("budget_ids", "budget_ids.task_id")
    def _compute_venue_names(self):
        for record in self:
            venue_name_list = []
            for line in record.budget_ids:
                for venue_line in line.task_id.episode_ids:
                    venue_name_list.append(venue_line.venue)

            venue_name_list = list(set(venue_name_list))
            venue_name_list.sort()
            venue_names = ', '.join(map(str, venue_name_list))
            record.venue_names = venue_names

    @api.depends("budget_info_ids", "budget_info_ids.remaining_amount")
    def _compute_total_remaining(self):
        for rec in self:
            rec.total_remaining = sum(rec.budget_info_ids.mapped('remaining_amount'))

    @api.depends('budget_ids', 'budget_ids.expenditure_type_id')
    def _get_expenditure_id(self):
        for rec in self:
            expenditures = [(5, 0, 0)]
            expenditures += [(4, x.expenditure_type_id.id) for x in rec.budget_ids if x.expenditure_type_id]
            rec.expenditure_ids = expenditures

    @api.onchange('task_id')
    def _onchange_task_id(self):
        for record in self:
            if record.task_id.date_start and record.task_id.date_end:
                record.date_start = record.task_id.date_start
                record.date_end = record.task_id.date_end

    def button_submit(self):
        """ TODO function to submit """
        for rec in self:
            if all([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email]):
                email_to = ','.join([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email])
                rec.with_context({'email_to': email_to})._send_email()
            rec.write({'task_status': 'submit'})
            rec.task_id.state = 'submit'

    def _compute_button_visible(self):
        for rec in self:
            print(rec.user_manager_task_id.id, self._uid, 'ini usernya berapa ?')
            if rec.user_manager_task_id.id == self._uid:
                rec.button_visible = True
                print(rec.button_visible, 'masuk sini True')
            else:
                rec.button_visible = False

    def button_verify(self):
        """ TODO function to verify """
        for rec in self:
            if all([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email]):
                email_to = ','.join([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email])
                rec.with_context({'email_to': email_to})._send_email()
            rec.write({'task_status': 'verify'})
            rec.task_id.state = 'verify'

    def button_approve(self):
        """ TODO function to approve """
        for rec in self:
            if all([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email]):
                email_to = ','.join([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email])
                rec.with_context({'email_to': email_to})._send_email()
            rec.write({'task_status': 'approve'})
            rec.task_id.state = 'approve'

    def button_reject(self):
        """ TODO function to reject """
        return {
            'name': _("Reject Reason"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.reject.task.reason',
            'target': 'new',
            'context': {'default_task_id': self.id},
        }

    def button_cancel(self):
        """ TODO function to cancel """
        for rec in self:
            if all([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email]):
                email_to = ','.join([rec.task_id.manager_id.work_email, rec.task_id.control_id.work_email])
                rec.with_context({'email_to': email_to})._send_email()
            rec.write({'task_status': 'cancel'})
            rec.task_id.state = 'cancel'

    def button_draft(self):
        """ TODO function to draft """
        for rec in self:
            rec.write({'task_status': 'draft'})
            rec.task_id.state = 'draft'

    def _get_email_template(self):
        """ helper function to get email template """
        return 'ins_project.budget_mail_template'

    def _get_total_budget(self):
        """ helper function to get total budget """
        amount = sum(self.budget_ids.mapped('budget'))
        return amount

    def _send_email(self):
        """ function to send email to user """
        # TODO we might want to pass a context into this function to assign
        # From, To, Sent, Log ID, Total Budget and Description
        # NOTE: this function will be called in every button
        ctx = self._context
        try:
            template = self._get_email_template()
            template_id = self.env.ref(template)
        except ValueError:
            template_id = False

        # TODO FIXME might need a new model to contain the history?

        # NOTE: data
        # From: the approving user or self.env.user
        # To: target user depending on the state. Submit will send to task_id.manager_id
        # and Verified will send to task_id.control_id
        # Sent: datetime object with information
        # Verified will send to Budget Control
        # Total Budget: Budget of the Task, find budget with program and task
        # Description: taken from task name

        email_to = ctx.get('email_to', '')

        tz_asia_jkt = timezone('Asia/Jakarta')
        date_sent = datetime.now(tz=tz_asia_jkt).strftime('%d-%m-%Y %H:%M:%S')
        amount_budget_str = '{:,.2f}'.format(self._get_total_budget())

        state_dict = dict(self.env['pmis.budget']._fields['task_status']._description_selection(self.env))
        state = state_dict.get(self.task_status)

        mail_subject = '[%s] Budget Program %s - %s' % (
            state, self.program_id.name, self.program_id.code)

        email_from = self.env.user.email

        email_cc = ','.join([
            self.task_id.manager_id.work_email, self.task_id.executive_producer_id.work_email,
            self.task_id.producer_id.work_email, self.task_id.control_id.work_email,
        ])

        if template_id:
            template_id.with_context(
                mail_subject=mail_subject,
                date_sent=date_sent,
                amount_budget=amount_budget_str,
                email_from=email_from,
                email_to=email_to,
                email_cc=email_cc
            ).send_mail(self.id, force_send=True)
        return
