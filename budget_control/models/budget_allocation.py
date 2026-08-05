# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning

MONTH_FIELDS = [
    'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
    'month7', 'month8', 'month9', 'month10', 'month11', 'month12'
]


class BudgetAllocation(models.Model):
    _name = 'budget.allocation'
    _description = "Budget Allocation"

    name = fields.Char(string="Allocation Name", default='', required=True, copy=False)
    state = fields.Selection([
        ('draft', "Draft"), ('request', "Request"), ('to_approve', "To Approve"),
        ('approved', "Approved"), ('cancel', "Cancel")
    ], string="Status", default='draft')
    date_allocation = fields.Date(string="Allocation Date", required=True)
    crossovered_budget_id = fields.Many2one('crossovered.budget', string="Budget", required=True, domain=[('state', '=', 'validate')])
    line_ids = fields.One2many('budget.allocation.line', 'budget_allocation_id', string="Lines")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    def confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            return
        self.state = 'request'

    def submit_request(self):
        self.ensure_one()
        if self.state != 'request':
            return
        self.state = 'to_approve'

    def approve(self):
        self.ensure_one()
        if self.state != 'to_approve':
            return

        if self.crossovered_budget_id:
            for line in self.line_ids:
                cb_line = self.crossovered_budget_id.crossovered_budget_line.filtered(
                    lambda cbl: cbl.general_budget_id.id == line.general_budget_id.id and cbl.analytic_account_id.id == line.analytic_account_id.id)

                if cb_line:
                    line.update_budget_line(cb_line)
                else:
                    line.create_new_budget_line()

        self.state = 'approved'

    def cancel(self):
        self.ensure_one()
        if self.state == 'approved' and self.crossovered_budget_id:
            for line in self.line_ids:
                cb_line = self.crossovered_budget_id.crossovered_budget_line.filtered(
                    lambda cbl: cbl.general_budget_id.id == line.general_budget_id.id and cbl.analytic_account_id.id == line.analytic_account_id.id)

                if cb_line:
                    line.cancel_added_budget(cb_line)

        self.state = 'cancel'

    def set_to_draft(self):
        self.ensure_one()
        if self.state != 'cancel':
            return

        self.state = 'draft'

    def unlink(self):
        for allocation in self:
            if allocation.state != 'draft':
                raise UserError(_("You cannot delete a Budget Allocation which is not draft."))
        super(BudgetAllocation, self).unlink()


class BudgetAllocationLine(models.Model):
    _name = 'budget.allocation.line'
    _description = "Budget Allocation Line"

    name = fields.Char(compute='_compute_line_name')
    budget_allocation_id = fields.Many2one('budget.allocation', string="Allocation", ondelete='cascade', index=True,
                                           required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", required=True)
    analytic_group_id = fields.Many2one('account.analytic.group', string="Analytic Group",
                                        related='analytic_account_id.group_id', readonly=True)
    general_budget_id = fields.Many2one('account.budget.post', string="Budgetary Position", required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', related='budget_allocation_id.company_id', string="Company", store=True,
                                 readonly=True)
    amount_total_budget = fields.Float(string="Total Allocation", compute='_compute_amount_total')
    amount_rem_budget = fields.Float(string="Amount Remaining")
    month1 = fields.Float(string="Jan")
    month2 = fields.Float(string="Feb")
    month3 = fields.Float(string="Mar")
    month4 = fields.Float(string="Apr")
    month5 = fields.Float(string="May")
    month6 = fields.Float(string="Jun")
    month7 = fields.Float(string="Jul")
    month8 = fields.Float(string="Aug")
    month9 = fields.Float(string="Sep")
    month10 = fields.Float(string="Oct")
    month11 = fields.Float(string="Nov")
    month12 = fields.Float(string="Dec")

    def update_budget_line(self, budget_line):
        self.ensure_one()
        allc_month_values = self.read(MONTH_FIELDS)
        cb_month_values = budget_line.read(MONTH_FIELDS)

        for num in range(1, 13):
            month_number = 'month' + str(num)
            new_value = cb_month_values[0][month_number] + allc_month_values[0][month_number]
            update_value = {month_number: new_value}
            budget_line.write(update_value)
            budget_line._onchange_months_set_planned_amount()

    def cancel_added_budget(self, budget_line):
        self.ensure_one()
        allc_month_values = self.read(MONTH_FIELDS)
        cb_month_values = budget_line.read(MONTH_FIELDS)

        for num in range(1, 13):
            month_number = 'month' + str(num)
            new_value = cb_month_values[0][month_number] - allc_month_values[0][month_number]
            update_value = {month_number: new_value}
            budget_line.write(update_value)
            budget_line._onchange_months_set_planned_amount()

    def create_new_budget_line(self):
        line_values = {
            'crossovered_budget_id': self.budget_allocation_id.crossovered_budget_id.id,
            'general_budget_id': self.general_budget_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'date_from': self.budget_allocation_id.crossovered_budget_id.date_from,
            'date_to': self.budget_allocation_id.crossovered_budget_id.date_to,
            'planned_amount': 0.0,
        }

        allc_month_values = self.read(MONTH_FIELDS)
        for num in range(1, 13):
            month_number = 'month' + str(num)
            amount = allc_month_values[0][month_number]
            line_values[month_number] = amount
            line_values['planned_amount'] = line_values['planned_amount'] + amount

        self.env['crossovered.budget.lines'].create(line_values)

    @api.depends("budget_allocation_id", "general_budget_id", "analytic_account_id")
    def _compute_line_name(self):
        # just in case someone opens the budget line in form view
        for record in self:
            computed_name = record.budget_allocation_id.name
            if record.general_budget_id:
                computed_name += ' - ' + record.general_budget_id.name
            if record.analytic_account_id:
                computed_name += ' - ' + record.analytic_account_id.name
            record.name = computed_name

    @api.constrains('amount_total_budget', 'amount_rem_budget')
    def _check_amount_total_budget(self):
        # TODO make validation to check amount total
        for rec in self:
            if rec.amount_total_budget < 0:
                if (rec.amount_rem_budget - abs(rec.amount_total_budget)) < 0: 
                    raise Warning('Amount total exceeds remaining amount!')

    @api.onchange("general_budget_id", "analytic_account_id")
    def _onchange_amount_rem(self):
        # TODO make validation to check amount total
        for rec in self:
            if rec.budget_allocation_id and rec.analytic_account_id:
                rem = 0
                domain = [
                    ('crossovered_budget_id', '=', rec.budget_allocation_id.crossovered_budget_id.id),
                    ('analytic_account_id', '=', rec.analytic_account_id.id),
                    ('general_budget_id', '=', rec.general_budget_id.id)
                ]

                line_ids = self.env['crossovered.budget.lines'].search(domain)

                for line in line_ids:
                    rem += line.remaining_amount

                rec.amount_rem_budget = rem

    @api.onchange(
        'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
        'month7', 'month8', 'month9', 'month10', 'month11', 'month12',
    )
    @api.depends(
        'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
        'month7', 'month8', 'month9', 'month10', 'month11', 'month12',
    )
    def _compute_amount_total(self):
        for record in self:
            record.amount_total_budget = record.month1 + record.month2 + record.month3 + record.month4 + \
                                            record.month5 + record.month6 + record.month7 + record.month8 + \
                                            record.month9 + record.month10 + record.month11 + record.month12
