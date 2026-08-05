# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class BudgetSummary(models.TransientModel):
    _name = 'budget.summary'

    period_id = fields.Many2one('crossovered.budget.period',  string="Period")
    company_ids = fields.Many2many('res.company', 'budget_sumary_company_rel', string="Company")
    analytic_account_group_ids = fields.Many2many('account.analytic.group', 'budget_sumary_ac_group_rel', string="Group")

    def submit(self):
        self.ensure_one()

        context = {}
        domain = []

        if self.period_id:
            domain.append(('crossovered_budget_id.period_id', '=', self.period_id.id))

        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
            context['search_default_group_company_id'] = 1
        else:
            context['search_default_group_crossevered_budgdet_id'] = 1

        if self.analytic_account_group_ids:
            domain.append(('analytic_account_id.group_id', 'in', self.analytic_account_group_ids.ids))

        cb_line_ids = self.env['crossovered.budget.lines'].search(domain)
        if cb_line_ids:
            budget_summary_ids = cb_line_ids.ids
        else:
            budget_summary_ids = []

        if self.analytic_account_group_ids:
            grouped_cb_line_ids = []
            grouped_cb_line = {}
            for cb_line in cb_line_ids:
                if cb_line.analytic_group_id.id not in grouped_cb_line:
                    grouped_cb_line[cb_line.analytic_group_id.id] = {
                        'company_id': cb_line.company_id.id,
                        'planned_amount': cb_line.planned_amount,
                        'practical_amount': cb_line.practical_amount,
                        'theoritical_amount': cb_line.theoritical_amount,
                        'analytic_group_id': cb_line.analytic_group_id.id,
                        'month1': cb_line.month1,
                        'month2': cb_line.month2,
                        'month3': cb_line.month3,
                        'month4': cb_line.month4,
                        'month5': cb_line.month5,
                        'month6': cb_line.month6,
                        'month7': cb_line.month7,
                        'month8': cb_line.month8,
                        'month9': cb_line.month9,
                        'month10': cb_line.month10,
                        'month11': cb_line.month11,
                        'month12': cb_line.month12,
                        'amount_total_budget': cb_line.amount_total_budget,
                        'pr_reserve_amount': cb_line.pr_reserve_amount,
                        'po_reserve_amount': cb_line.remaining_amount
                    }
                else:
                    grouped_cb_line[cb_line.analytic_group_id.id]['planned_amount'] = grouped_cb_line[cb_line.analytic_group_id.id]['planned_amount'] + cb_line.planned_amount
                    grouped_cb_line[cb_line.analytic_group_id.id]['practical_amount'] = grouped_cb_line[cb_line.analytic_group_id.id]['practical_amount'] + cb_line.practical_amount
                    grouped_cb_line[cb_line.analytic_group_id.id]['theoritical_amount'] = grouped_cb_line[cb_line.analytic_group_id.id]['theoritical_amount'] + cb_line.theoritical_amount
                    grouped_cb_line[cb_line.analytic_group_id.id]['month1'] = grouped_cb_line[cb_line.analytic_group_id.id]['month1'] + cb_line.month1
                    grouped_cb_line[cb_line.analytic_group_id.id]['month2'] = grouped_cb_line[cb_line.analytic_group_id.id]['month2'] + cb_line.month2
                    grouped_cb_line[cb_line.analytic_group_id.id]['month3'] = grouped_cb_line[cb_line.analytic_group_id.id]['month3'] + cb_line.month3
                    grouped_cb_line[cb_line.analytic_group_id.id]['month4'] = grouped_cb_line[cb_line.analytic_group_id.id]['month4'] + cb_line.month4
                    grouped_cb_line[cb_line.analytic_group_id.id]['month5'] = grouped_cb_line[cb_line.analytic_group_id.id]['month5'] + cb_line.month5
                    grouped_cb_line[cb_line.analytic_group_id.id]['month6'] = grouped_cb_line[cb_line.analytic_group_id.id]['month6'] + cb_line.month6
                    grouped_cb_line[cb_line.analytic_group_id.id]['month7'] = grouped_cb_line[cb_line.analytic_group_id.id]['month7'] + cb_line.month7
                    grouped_cb_line[cb_line.analytic_group_id.id]['month8'] = grouped_cb_line[cb_line.analytic_group_id.id]['month8'] + cb_line.month8
                    grouped_cb_line[cb_line.analytic_group_id.id]['month9'] = grouped_cb_line[cb_line.analytic_group_id.id]['month9'] + cb_line.month9
                    grouped_cb_line[cb_line.analytic_group_id.id]['month10'] = grouped_cb_line[cb_line.analytic_group_id.id]['month10'] + cb_line.month10
                    grouped_cb_line[cb_line.analytic_group_id.id]['month11'] = grouped_cb_line[cb_line.analytic_group_id.id]['month11'] + cb_line.month11
                    grouped_cb_line[cb_line.analytic_group_id.id]['month12'] = grouped_cb_line[cb_line.analytic_group_id.id]['month12'] + cb_line.month12
                    grouped_cb_line[cb_line.analytic_group_id.id]['amount_total_budget'] = grouped_cb_line[cb_line.analytic_group_id.id]['amount_total_budget'] + cb_line.amount_total_budget
                    grouped_cb_line[cb_line.analytic_group_id.id]['pr_reserve_amount'] = grouped_cb_line[cb_line.analytic_group_id.id]['pr_reserve_amount'] + cb_line.pr_reserve_amount
                    grouped_cb_line[cb_line.analytic_group_id.id]['po_reserve_amount'] = grouped_cb_line[cb_line.analytic_group_id.id]['po_reserve_amount'] + cb_line.po_reserve_amount

            for k, v in grouped_cb_line.items():
                grouped_line = self.env['budget.summary.group'].create(v)
                grouped_cb_line_ids.append(grouped_line.id)

            grouped_context = {}
            if self.company_ids:
                grouped_context['search_default_group_company_id'] = 1

            return {
                'name': _('Budget Summary'),
                'view_mode': 'tree',
                'res_model': 'budget.summary.group',
                'type': 'ir.actions.act_window',
                'target': 'main',
                'view_id': self.env.ref('budget_control.budget_summary_grouped_tree_view').id,
                'domain': [('id', 'in', grouped_cb_line_ids)],
                'context': grouped_context
            }
        else:
            return {
                'name': _('Budget Summary'),
                'view_mode': 'tree',
                'res_model': 'crossovered.budget.lines',
                'type': 'ir.actions.act_window',
                'target': 'main',
                'view_id': self.env.ref('budget_control.budget_summary_tree_view').id,
                'domain': [('id', 'in', budget_summary_ids)],
                'context': context
            }
