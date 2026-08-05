from datetime import datetime
from pytz import timezone
from odoo import api, fields, models, _


class PmisBudgetReview(models.Model):
    _name = 'pmis.budget.review'
    _description = 'PMIS Budget Review'

    budget_id = fields.Many2one(
        'pmis.budget', string="Budget")
    name = fields.Text('Description', copy=False)
    program_id = fields.Many2one(
        'pmis.program', string="Program")
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project')
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic Account',
                                          related='program_id.analytic_account_id')
    department_type_id = fields.Many2one(
        'pmis.departement.type', 'Department Type')
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
    budget_ids = fields.One2many(
        'pmis.budget.line',
        'review_line_id',
        string="Budget Lines")
    total_budget = fields.Float(
        compute="_compute_total_budget",
        string="Total Budget",
        store=True,
    )
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    group_id = fields.Many2one(
        'project.group.type', 'Group',
        related='task_id.group_type_id', store=True
        )
    venue_names = fields.Char(
        string="Venue Names", compute='_compute_venue_names')
    unit_pm_id = fields.Many2one(
        'hr.employee', 'Unit PM',
        domain='[("analytic_account_id", "=", analytic_account_id)]')

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.program_id.code}] {rec.program_id.name}'
            result.append((rec.id, name))
        return result

    # @api.model
    # def create(self, vals):
    #     """ inherit function to create line_number """
    #     if vals.get('budget_ids', []):  # check if project_ids exist
    #         lines = vals.get('budget_ids', [])  # loop and assign line_number
    #         for idx, line in enumerate(lines):
    #             line[2].update({'no': idx + 1})
    #     res = super(PmisBudgetReview, self).create(vals)
    #     return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        # update context to add review
        context = dict(self._context)
        context.update({'review': True})
        res = super(PmisBudgetReview, self.with_context(context)).write(vals)
        # find project_ids, rewrite the line number
        for idx, line in enumerate(self.budget_ids):
            line.no = idx + 1
        return res

    @api.depends("budget_ids", "budget_ids.budget")
    def _compute_total_budget(self):
        for rec in self:
            rec.total_budget = sum(rec.budget_ids.mapped("budget"))

    @api.onchange('budget_id')
    def _onchange_budget_id(self):
        for record in self:
            record.program_id = record.budget_id.program_id.id
            record.main_project_id = record.budget_id.main_project_id.id
            record.task_id = record.budget_id.task_id.id
            record.date_start = record.budget_id.task_id.date_start
            record.date_end = record.budget_id.task_id.date_end
            record.department_type_id = record.budget_id.department_type_id.id
            record.unit_pm_id = record.budget_id.unit_pm_id.id

            domain = [
                ('line_id', '=', record.budget_id.id),
            ]

            line_ids = self.env['pmis.budget.line'].search(domain)

            record.budget_ids = [(5, 0)]
            record.budget_ids = [(6, False, line_ids.ids)] if line_ids else False

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
