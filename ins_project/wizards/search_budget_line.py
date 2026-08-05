# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SearchBudgetLine(models.TransientModel):
    _name = 'pmis.search.budget.lines'
    _description = "Search Budget Line (PMIS)"

    budget_id = fields.Many2one('pmis.budget', string="Budget", required=True)
    # item_name = fields.Char('Item Code')
    expenditure_category_ids = fields.Many2many(
        'project.expenditure.category', 'search_b_cat_rel', 'Expenditure Category')
    expenditure_subcategory_ids = fields.Many2many(
        'project.expenditure.subcategory',
        'search_b_subcat_rel',
        'Expenditure Subcategory',
        domain='[("expenditure_category_id", "in", expenditure_category_ids)]')
    expenditure_type_ids = fields.Many2many(
        'project.expenditure.type',
        'search_b_extype_rel',
        'Expenditure Type',
        domain='[("category_id", "in", expenditure_subcategory_ids)]')
    budget_line_ids = fields.Many2many('pmis.budget.line', 'search_b_line_rel',
                                       string="Budget Lines")
    total_budget = fields.Float(
        compute="_compute_total_budget",
        string="Total Budget",
        store=True,
    )

    @api.onchange('expenditure_category_ids', 'expenditure_subcategory_ids')
    def _onchange_filters(self):
        self.ensure_one()
        category_ids = self.expenditure_category_ids.ids if self.expenditure_category_ids else []
        subcategory_ids = self.expenditure_subcategory_ids.ids if self.expenditure_subcategory_ids else []
        type_ids = self.expenditure_type_ids.ids if self.expenditure_type_ids else []
        domain = [
            ('line_id', '=', self.budget_id.id),
            ('category_id', 'in', category_ids),
        ]

        if self.expenditure_subcategory_ids:
            domain.append(('subcategory_id', 'in', subcategory_ids))
        if self.expenditure_type_ids:
            domain.append(('expenditure_type_id', 'in', type_ids))

        line_ids = self.env['pmis.budget.line'].search(domain)

        self.budget_line_ids = [(5, 0)]
        self.budget_line_ids = [(6, False, line_ids.ids)] if line_ids else False

    @api.depends("budget_line_ids", "budget_line_ids.budget")
    def _compute_total_budget(self):
        for rec in self:
            rec.total_budget = sum(rec.budget_line_ids.mapped("budget"))
