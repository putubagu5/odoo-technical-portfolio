from odoo import api, fields, models


class ProjectInPr(models.Model):
    _name = 'project.pr.line'
    _description = 'Project PR Line'

    name = fields.Char('Name')
    line_number = fields.Integer('No')
    budget_line_id = fields.Many2one('pmis.budget.line', 'Budget Line',
                                     compute='_compute_budget_line_id', store=True)
    project_id = fields.Many2one(
        'pmis.program', string="Project")
    budget_ids = fields.Many2many('pmis.budget', 'rel_project_pr_line_pmis_budget',
                                  'project_pr_line_id', 'budget_id', string='Budgets',
                                  compute='_compute_budget_ids', store=True)
    expenditure_type_ids = fields.Many2many(
        'project.expenditure.type', 'rel_project_pr_line_project_expenditure_type',
        'project_pr_line_id', 'expenditure_type_id', string='Expenditure Types',
        compute='_compute_budget_ids', store=True)
    program_id = fields.Many2one(
        'pmis.budget', string="Program")
    task_id = fields.Many2one(
        'pmis.project.task', 'Task')
    subtask_id = fields.Many2one(
        'pmis.project.task.line', 'Sub Task',
        domain='[("line_id", "=", task_id)]')
    expenditure_type_id = fields.Many2one(
        'project.expenditure.type',
        'Expenditure Type')
    percentage = fields.Float('Percent (%)', default=100)
    qty = fields.Float('Qty', compute='_compute_from_percentage')
    amount = fields.Float('Amount', compute='_compute_from_percentage')
    remaining_budget = fields.Float('Remaining Budget', compute='_compute_remaining')
    # related_pr_line = fields.Char('Related PR line', related='line_id.name')
    pr_description = fields.Char('Description', compute='_compute_pr_description')
    pr_numbers = fields.Char(string="PR Number", compute='_compute_pr_numbers')
    po_numbers = fields.Char(string="PO Number", compute='_compute_po_numbers')
    rr_numbers = fields.Char(string="RR Number", compute='_compute_rr_numbers')
    line_id = fields.Many2one(
        comodel_name="purchase.request.line",
        string="Purchase Request Line",
        ondelete="set null",
        readonly=True,
        copy=False,
        index=True,
    )
    po_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Purchase Order Line",
        ondelete="set null",
        readonly=True,
        copy=False,
        index=True,
    )
    account_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Account Move Line",
        ondelete="set null",
        readonly=True,
        copy=False,
        index=True,
    )
    move_line_id = fields.Many2one(
        comodel_name="stock.move",
        string="Move Line",
        ondelete="set null",
        readonly=True,
        copy=False,
        index=True,
    )

    @api.depends('line_id')
    def _compute_pr_description(self):
        """ compute function to get description """
        for rec in self:
            rec.pr_description = rec.line_id.name if rec.line_id else ''

    @api.depends('line_id', 'line_id.request_id')
    def _compute_pr_numbers(self):
        """ compute function to get numbers """
        for rec in self:
            rec.pr_numbers = rec.line_id.request_id.name if rec.line_id.request_id else ''

    @api.depends('po_line_id', 'po_line_id.order_id')
    def _compute_po_numbers(self):
        """ compute function to get numbers """
        for rec in self:
            rec.po_numbers = rec.po_line_id.order_id.name if rec.po_line_id.order_id else ''

    @api.depends('move_line_id')
    def _compute_rr_numbers(self):
        """ compute function to get numbers """
        for rec in self:
            rec.rr_numbers = rec.move_line_id.reference if rec.move_line_id else ''

    @api.depends('project_id', 'task_id')
    def _compute_budget_ids(self):
        """ compute function to get budgets with program_id = project_id """
        for rec in self:
            # find same pmis.program and task_status is approve, then get all
            # found budgets and expenditures to use as filter
            domain = [
                ('program_id', '=', rec.project_id.id),
                ('task_status', '=', 'approve'),
            ]
            budgets = self.env['pmis.budget'].search(domain)

            # apparently it needs to be filtered again
            budget_lines = budgets.budget_ids.filtered(
                lambda x: x.program_id == rec.project_id and x.task_id == rec.task_id)

            rec.budget_ids = budgets.ids if budgets else False
            rec.expenditure_type_ids = budget_lines.mapped('expenditure_type_id.id') if budget_lines else False

    # @api.onchange('expenditure_type_id')
    # def _onchange_expenditure_type_id(self):
    #     """ filter task for budget per program """
    #     # line = self.line_id
    #     rem_budget = 0.0
    #     domain = [
    #             ('line_id', '=', self.program_id.id),
    #             ('line_id.task_id', '=', self.task_id.id),
    #             ('expenditure_type_id', '=', self.expenditure_type_id.id),
    #             ('line_id.task_status', '=', 'approve'),
    #         ]

    #     budget_ids = self.env['pmis.budget.line'].search(domain)
    #     if self.expenditure_type_id:
    #         for rec in budget_ids:
    #             rem_budget += rec.remaining_amount
    #             self.remaining_budget = rem_budget

    @api.depends('project_id', 'task_id', 'expenditure_type_id')
    def _compute_remaining(self):
        """ compute budget remaining per program """
        # line = self.line_id
        for rec in self:
            rem_budget = 0.0
            rec.remaining_budget = 0.0
            domain = [
                ('program_id', '=', rec.project_id.id),
                ('task_id', '=', rec.task_id.id),
                ('expenditure_type_id', '=', rec.expenditure_type_id.id),
                ('line_id.task_status', '=', 'approve'),
            ]

            budget_ids = self.env['pmis.budget.line'].search(domain)
            if rec.expenditure_type_id and rec.task_id and rec.project_id:
                for line in budget_ids:
                    rem_budget += line.remaining_amount
            rec.remaining_budget = rem_budget

    # @api.onchange('program_id')
    # def _onchange_program_id(self):
    #     if self.program_id:
    #         return {
    #             'domain': {
    #                 'task_id': [
    #                     ('program_id', '=', self.program_id.program_id.id),
    #                     ('state', '=', 'approve')
    #                 ],
    #                 'expenditure_type_id': [
    #                     ('id', 'in', self.program_id.expenditure_ids.ids)
    #                 ],
    #             }
    #         }

    # @api.onchange('program_id')
    # def _onchange_program_id(self):
    #     if self.program_id:
    #         return {
    #             'domain': {
    #                 'expenditure_type_id': [
    #                     ('id', 'in', self.program_id.expenditure_ids.ids)
    #                 ],
    #             }
    #         }

    # @api.onchange('expenditure_type_id')
    # def _onchange_expenditure_type_id(self):
    #     """ filter expenditure type for remaining budget """
    #     if self.expenditure_type_id:
    #         for budget_line in self.program_id.budget_info_ids.filtered(lambda x: x.expenditure_type_id.id):
    #             rem_budget = budget_line.remaining_amount or 0.0
    #             self.remaining_budget = rem_budget
    #         for line in pr_line.project_ids:
    #             budget_id = line.program_id
    #             amount_prline = line.amount
    #             for detail in budget_id.budget_info_ids:
    #                 detail.write({
    #                     'pr_reserve_amount': 0,
    #                 })
    #     return super(PurchaseRequest, self).button_draft()

    # @api.onchange('percentage')
    # def _onchange_percentage(self):
    #     line = self.line_id
    #     qty_proportion = (self.percentage / 100) * line.product_qty
    #     amount_proportion = (self.percentage / 100) * line.estimated_cost

    #     self.qty = qty_proportion
    #     self.amount = amount_proportion

    @api.depends('line_id', 'percentage')
    def _compute_from_percentage(self):
        for rec in self:
            qty_proportion = 0.0
            amount_proportion = 0.0
            line = rec.line_id
            if line:
                qty_proportion = (rec.percentage / 100) * line.product_qty
                amount_proportion = (rec.percentage / 100) * line.estimated_cost

            rec.qty = qty_proportion
            rec.amount = amount_proportion

    # def _default_amount(self):
    #     line = self.line_id
    #     self.amount = line.estimated_cost

    @api.depends('project_id', 'task_id', 'expenditure_type_id')
    def _compute_budget_line_id(self):
        """ compute function to get the respective budget_line_id """
        # NOTE: find pmis.budget.line having the same program and task for the
        # pmis.budget record and the same expenditure type, limit only 1
        for rec in self:
            domain = [
                ('program_id', '=', rec.project_id.id),
                ('task_id', '=', rec.task_id.id),
                ('expenditure_type_id', '=', rec.expenditure_type_id.id),
            ]
            budget_line = self.env['pmis.budget.line'].search(domain, limit=1)
            rec.budget_line_id = budget_line.id
