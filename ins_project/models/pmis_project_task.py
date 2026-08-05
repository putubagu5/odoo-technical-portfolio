from datetime import datetime
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError


class PmisProjectTask(models.Model):
    _name = 'pmis.project.task.line'
    _description = 'Task Details'

    no = fields.Integer('No')
    line_id = fields.Many2one('pmis.project.task', 'Line ID',
                              ondelete='cascade', index=True,
                              required=True)
    episode_line_id = fields.Many2one('pmis.episode.line', 'Episode')
    episode_code = fields.Char('Episode Code', related='episode_line_id.code')
    episode_no = fields.Integer('Episode No', related='episode_line_id.episode_no')
    episode_name = fields.Char('Episode Name', related='episode_line_id.name')
    venue = fields.Char('Venue')
    remarks = fields.Char('Remarks')
    budget_type = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
    ], string="Budget Type")
    status = fields.Selection([
        ('active', "Active"),
        ('inactive', "Inactive"),
    ], string="Status")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    budget_type = fields.Selection([
        ('absolute', 'Absolute'),
        ('advisory', 'Advisory'),
    ], 'Budget Type', related='company_id.default_budget_type_subtask', store=True)

    # CUSTOM DISPLAY NAME IF USED AS MANY2ONE FIELDS
    def name_get(self):
        result = []
        for record in self:
            name = record.episode_name
            result.append((record.id, name))
        return result


class PmisProjectTask(models.Model):
    _name = 'pmis.project.task'
    _description = 'Task'

    code = fields.Char('Code', default='/')
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Description')
    task_id = fields.Many2one('pmis.project.task', 'Additional Task')
    program_id = fields.Many2one('pmis.program', 'Program Title')
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project ID',
                                      related='program_id.main_project_id',
                                      store=True)
    phase_type_id = fields.Many2one(
        'project.phase.type', string="Phase Type")
    manager_id = fields.Many2one(
        'hr.employee', 'Manager',
        domain='[("analytic_account_id", "=", analytic_account_id)]')
    executive_producer_id = fields.Many2one(
        'hr.employee', 'Exc. Producer',
        domain='[("analytic_account_id", "=", analytic_account_id)]')
    producer_id = fields.Many2one(
        'hr.employee', 'Producer',
        domain='[("analytic_account_id", "=", analytic_account_id)]')
    control_id = fields.Many2one('hr.employee', 'Budget Control')
    date_shoot_start = fields.Date('Estimate Shoot Date')
    date_shoot_end = fields.Date('Until')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    group_type_id = fields.Many2one(
        'project.group.type', string="Group Type")
    episode_count = fields.Integer('Episode Count')
    range_start = fields.Integer('Range')
    range_end = fields.Integer('To')
    episode_sum = fields.Integer('Episode Sum', compute='_compute_episode_sum',
                                 store=True)
    day_number = fields.Integer('Day Number')
    duration = fields.Integer('Duration (Minutes)')
    live_tapping = fields.Many2one('broadcast.type', 'Live / Taping')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='program_id.analytic_account_id')
    episode_ids = fields.One2many(
        'pmis.project.task.line',
        'line_id',
        string="Episode Lines")
    create_date = fields.Datetime(string='Created On')
    is_additional = fields.Boolean(related='phase_type_id.is_additional')
    state = fields.Selection([
        ('draft', 'Incomplete/Draft'),
        ('submit', 'Submitted'),
        ('verify', 'Verified'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], 'Status', default='draft')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    is_batch = fields.Boolean('Batch Episode ?', default=True)
    budget_type = fields.Selection([
        ('absolute', 'Absolute'),
        ('advisory', 'Advisory'),
    ], 'Budget Type', related='company_id.default_budget_type_task', store=True)
    reference = fields.Char(string='Reference Number')

    def name_get(self):
        result = []
        for rec in self:
            desc = rec.name or '-'
            name = f'[{rec.code}] {desc}'
            result.append((rec.id, name))
        return result

    @api.onchange('program_id')
    def _onchange_program_id(self):
        for record in self:
            if record.program_id.date_start and record.program_id.date_end:
                record.date_start = record.program_id.date_start
                record.date_end = record.program_id.date_end

    @api.constrains('date_start', 'date_end', 'program_id.date_start', 'program_id.date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_start > self.date_end:
            raise Warning('Start Date must be earlier than End Date')

        if self.date_start < self.program_id.date_start or self.date_end > self.program_id.date_end:
            raise Warning('Start/End Date Exceeds Program Period')

    @api.constrains('range_start', 'range_end')
    def _check_range(self):
        """ constrains function to check range validity """
        for rec in self:
            if rec.range_start > rec.range_end:
                raise Warning('Range Start must be less than Range End')

    @api.depends('range_start', 'range_end')
    def _compute_episode_sum(self):
        """ compute function to get episode_sum """
        for rec in self:
            if not rec.range_end and not rec.range_start:
                rec.episode_sum = 0
            else:
                rec.episode_sum = rec.range_end - rec.range_start + 1

    def button_generate(self):
        """ function to generate episodes """
        # NOTE: find pmis.episode data with the same program_id, limit to 1
        # and construct data and assign to line
        domain = [('program_id', '=', self.program_id.id)]
        limit = self.episode_count
        episode = self.env['pmis.episode'].search(domain, limit=1)
        if episode:
            lines = [(2, x.id) for x in self.episode_ids]
            i = 1
            eps_no = self.range_start
            eps_batch = self.range_end
            date_end = self.date_end
            if self.is_batch is True:
                if date_end is True:
                    for x in episode.line_ids.filtered(lambda x: x.episode_no == eps_batch and x.date_end <= date_end):
                        data = {
                            'no': i,
                            'episode_line_id': x.id,
                            'status': x.company_id.status_task,
                        }
                        eps_no += 1
                        lines.append((0, 0, data))
                        if i == limit:
                            break
                        i += 1
                else:
                    for x in episode.line_ids.filtered(lambda x: x.episode_no == eps_batch):
                        data = {
                            'no': i,
                            'episode_line_id': x.id,
                            'status': x.company_id.status_task,
                        }
                        eps_no += 1
                        lines.append((0, 0, data))
                        if i == limit:
                            break
                        i += 1

            elif self.is_batch is False:
                if date_end is True:
                    for x in episode.line_ids.filtered(lambda x: x.episode_no >= eps_no and x.date_end <= date_end):
                        data = {
                            'no': i,
                            'episode_line_id': x.id,
                            'status': x.company_id.status_task,
                        }
                        eps_no += 1
                        lines.append((0, 0, data))
                        if i == limit:
                            break
                        i += 1
                else:
                    for x in episode.line_ids.filtered(lambda x: x.episode_no >= eps_no):
                        data = {
                            'no': i,
                            'episode_line_id': x.id,
                            'status': x.company_id.status_task,
                        }
                        eps_no += 1
                        lines.append((0, 0, data))
                        if i == limit:
                            break
                        i += 1

            self.episode_ids = lines
        return True

    def button_submit(self):
        """ TODO function to submit """
        for rec in self:
            # email_to = ','.join([rec.manager_id.email, rec.control_id.email])
            # rec.with_context({'email_to': email_to})._send_email()
            rec.write({'state': 'submit'})

    def button_verify(self):
        """ TODO function to verify """
        for rec in self:
            # email_to = ','.join([rec.manager_id.email, rec.control_id.email])
            # rec.with_context({'email_to': email_to})._send_email()
            rec.write({'state': 'verify'})

    def button_approve(self):
        """ TODO function to approve """
        for rec in self:
            # email_to = ','.join([rec.manager_id.email, rec.control_id.email])
            # rec.with_context({'email_to': email_to})._send_email()
            rec.write({'state': 'approve'})

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
            # email_to = ','.join([rec.manager_id.email, rec.control_id.email])
            # rec.with_context({'email_to': email_to})._send_email()
            rec.write({'state': 'cancel'})

    def button_draft(self):
        """ TODO function to draft """
        for rec in self:
            rec.write({'state': 'draft'})

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [
            ('code', '!=', '/'),
            ('code', '=ilike', self.code),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Code already exists!')

    # @api.model
    # def create(self, vals):
    #     """ inherit create function to assign code to auto-generate """
    #     if vals.get('code') == '/':
    #         vals['code'] = self.env['ir.sequence'].next_by_code('pmis.program')
    #     res = super(PmisProjectTask, self).create(vals)
    #     return res

    @api.model
    def create(self, vals):
        """ inherit create function to assign code to auto-generate """
        # sequence = self.analytic_account_id.analytic_seq_id
        # aa_code = self.analytic_account_id.analytic_seq_id.code
        # last_id = self.env['your.model'].search([], order='id desc', limit=1)
        sequence = self.env['ir.sequence'].next_by_code('pmis.project.task')
        res = super(PmisProjectTask, self).create(vals)
        task_number = res.program_id.code or '--False--'
        task_name = '0'
        if res.phase_type_id.is_additional is True:
            task_name = '1'
        # task_desc = res.name or 'False'
        res.write({
             'code': sequence.format(
                task_number=task_number[6:],
                task_name=task_name,
                ),
         })
        return res

    # @api.model
    # def write(self, vals):
    #     """ inherit write function to restrict edit """
    #     if any(state == 'approve' for state in set(self.mapped('state'))):
    #         raise UserError(_("No edit in done state"))
    #     else:
    #         return super(PmisProjectTask, self).write(vals)

    @api.model
    def unlink(self, vals):
        """ inherit unlink to restrict delete """
        if self.state not in ('draft', 'reject'):
            raise UserError(_("Cannot delete created task!"))
        return super(PmisProjectTask, self).unlink()

    # @api.model
    # def default_get(self, fields):
    #     res = super(PmisProjectTask, self).default_get(fields)
    #     company_code = self.env.user.company_id.company_code or ''
    #     dept_code = ''
    #     sequence = '000'
    #     full_code = ''

    #     # if self.company_id.company_code:
    #     #     company_code = self.company_id.departement_code

    #     if self.analytic_account_id.departement_code:
    #         dept_code = self.analytic_account_id.departement_code

    #     full_code = company_code + '-' + dept_code + '-' + sequence
    #     res.update({
    #         'code': full_code,
    #     })
    #     return res
