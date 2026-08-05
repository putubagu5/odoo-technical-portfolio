from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def set_account_move_line_from_po(self, purchase_line_id, service_move):
        self.ensure_one()
        # find move_ids from purchase line and get the first number
        pmoves = purchase_line_id.move_ids
        pmoves = pmoves.filtered(lambda x: x.line_number)
        pmoves = pmoves[0].line_number if pmoves and pmoves[0] else ''
        tax_ids = [(6, False, purchase_line_id.product_id.supplier_taxes_id.ids)] if \
            purchase_line_id.product_id.supplier_taxes_id else False
        move_line = {
            'sequence': purchase_line_id.sequence,
            'name': '%s: %s' % (
                purchase_line_id.order_id.name, purchase_line_id.name),
            'product_id': purchase_line_id.product_id.id,
            'product_uom_id': purchase_line_id.product_uom.id,
            'quantity': service_move.quantity_to_billed,
            'price_unit': purchase_line_id.price_unit,
            'analytic_account_id': purchase_line_id.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, purchase_line_id.analytic_tag_ids.ids)],
            'purchase_line_id': purchase_line_id.id,
            'asset_cost_progress_id': purchase_line_id.asset_cost_progress_id.id,
            'purchase_line_number': purchase_line_id.line_number,
            'picking_line_number': pmoves,
            'po_line_gr_match_ids': [(4, purchase_line_id.id)],
            'tax_ids': tax_ids,
            'project_ids': [(6, 0, purchase_line_id.project_ids.ids)],
        }

        currency = purchase_line_id.order_id.currency_id
        account_id = purchase_line_id.product_id.property_account_expense_id
        if not account_id:
            raise ValidationError(_("Expense Account for product {} not found.".format(
                purchase_line_id.product_id.name)))
        move_line.update({
            'currency_id': currency and currency.id or self.env.user.company_id.currency_id.id,
            'date_maturity': self.invoice_date_due,
            'partner_id': purchase_line_id.order_id.partner_id.id,
            'account_id': account_id.id,
        })

        self.invoice_line_ids = [(0, False, move_line)]

    def set_account_move_line_from_gr_line(self, stock_move, picking_move):
        self.ensure_one()
        tax_ids = [(6, False, stock_move.product_id.supplier_taxes_id.ids)] if \
            stock_move.product_id.supplier_taxes_id else False
        move_line = {
            'sequence': stock_move.sequence,
            'name': '%s: %s' % (
                stock_move.picking_id.purchase_id.name, stock_move.name),
            'product_id': stock_move.product_id.id,
            'product_uom_id': stock_move.product_uom.id,
            'quantity': picking_move.quantity_to_billed,
            'price_unit': stock_move.purchase_line_id.price_unit,
            'analytic_account_id': stock_move.purchase_line_id.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, stock_move.purchase_line_id.analytic_tag_ids.ids)],
            'purchase_line_id': stock_move.purchase_line_id.id,
            'stock_picking_id': stock_move.picking_id.id,
            'stock_move_id': stock_move.id,
            'asset_cost_progress_id': stock_move.purchase_line_id.asset_cost_progress_id.id,
            'purchase_line_number': stock_move.purchase_line_id.line_number,
            'picking_line_number': stock_move.line_number,
            'stock_move_gr_match_ids': [(4, stock_move.id)],
            'tax_ids': tax_ids,
            'project_ids': [(6, 0, stock_move.project_ids.ids)],
        }

        if self.currency_id == stock_move.picking_id.company_id.currency_id:
            currency = False
        else:
            currency = stock_move.picking_id.purchase_id.currency_id

        if stock_move.product_id.categ_id.property_stock_account_input_categ_id:
            account_id = stock_move.product_id.categ_id.property_stock_account_input_categ_id
        else:
            account_id = False

        if not account_id:
            raise ValidationError(_("Stock Input Account for product {} not found.".format(stock_move.product_id.name)))
        move_line.update({
            'currency_id': currency and currency.id or self.env.user.company_id.currency_id.id,
            'date_maturity': self.invoice_date_due,
            'partner_id': stock_move.picking_id.purchase_id.partner_id.id,
            'account_id': account_id.id,
        })

        self.invoice_line_ids = [(0, False, move_line)]
        # stock_move.is_gr_matched = True
