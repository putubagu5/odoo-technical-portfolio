# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_line_account(self, product):
        if product.type in ['consu', 'service']:
            account_id = product.property_account_expense_id.id if product.property_account_expense_id else False
        else:
            if product.categ_id.property_valuation == 'real_time':
                account_id = product.categ_id.property_stock_valuation_account_id.id if \
                    product.categ_id.property_stock_valuation_account_id else False
            else:
                account_id = product.property_account_expense_id.id if product.property_account_expense_id else False

        return account_id

    def action_post(self):
        result = super(AccountMove, self).action_post()
        # available, rem_budget = True, 0.0
        # if self.move_type == 'in_invoice':
        #     for line in self.invoice_line_ids:
        #         if self.env.company.budget_check_account_move and line.account_id and line.analytic_account_id:
        #             budget_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
        #                 line.account_id, line.analytic_account_id.id, self.invoice_date)
        #             if budget_id:
        #                 available, rem_budget = budget_id.check_budget_availability(line.price_subtotal)
        #                 if not available:
        #                     raise ValidationError(_("Budget is insuficcient."))
        #             else:
        #                 raise ValidationError(_("There is no budget."))
        # elif self.move_type == 'entry':
        #     for line in self.line_ids:
        #         if self.env.company.budget_check_account_move and line.account_id and line.analytic_account_id:
        #             budget_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
        #                 line.account_id.id, line.analytic_account_id.id, self.invoice_date)
        #             if budget_id and line.debit > 0.0:
        #                 available, rem_budget = budget_id.check_budget_availability(line.price_subtotal)
        #                 if not available:
        #                     raise ValidationError(_("Budget is insuficcient."))
        #             else:
        #                 raise ValidationError(_("There is no budget."))

        return result
