# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SearchBudgetLine(models.TransientModel):
    _name = 'search.crossovered.budget.lines'
    _description = "Search Crossovered Budget Line"

    crossovered_budget_id = fields.Many2one('crossovered.budget', string="Budget", required=True)
    general_budget_ids = fields.Many2many('account.budget.post', 'search_cb_budget_post_rel',
                                          string="Budgetary Positions")
    analytic_account_ids = fields.Many2many('account.analytic.account', 'search_cb_analytic_rel',
                                            string="Analytic Accounts")
    crossovered_budget_line_ids = fields.Many2many('crossovered.budget.lines', 'search_cb_cb_rel',
                                                   string="Budget Lines")

    @api.onchange('general_budget_ids', 'analytic_account_ids')
    def _onchange_filters(self):
        self.ensure_one()
        analytic_account_ids = self.analytic_account_ids.ids if self.analytic_account_ids else []
        budget_post_ids = self.general_budget_ids.ids if self.general_budget_ids else []
        domain = [
            ('crossovered_budget_id', '=', self.crossovered_budget_id.id),
            ('analytic_account_id', 'in', analytic_account_ids)
        ]
        if budget_post_ids:
            domain.append(('general_budget_id', 'in', budget_post_ids))

        line_ids = self.env['crossovered.budget.lines'].search(domain)

        self.crossovered_budget_line_ids = [(5, 0)]
        self.crossovered_budget_line_ids = [(6, False, line_ids.ids)] if line_ids else False
