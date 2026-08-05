from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        new_picking_id, pick_type_id = super(StockReturnPicking, self)._create_returns()
        for return_line in self.product_return_moves:
            return_line.move_id.write({'quantity_return': return_line.quantity})
        return new_picking_id, pick_type_id

    def create_returns(self):
        """ inherit function to check vendor bills and credit note """
        # rules, raise error if vendor bills are not in cancel state
        # purchase = self.picking_id.purchase_id
        # if purchase:
        #     invoices = purchase.invoice_ids

        #     # check if invoice state is not cancel
        #     act_invoices = invoices.filtered(lambda x: x.state != 'cancel')

        #     if act_invoices:
        #         raise ValidationError('Vendor Bill is Paid!')

        res = super(StockReturnPicking, self).create_returns()
        return res

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        """ inherit function to change qty """
        res = super(StockReturnPicking, self)._prepare_stock_return_picking_line_vals_from_move(stock_move)
        # NOTE: the quantity here we take from qty_avail_to_bill
        res['quantity'] = stock_move.qty_avail_to_bill
        return res if stock_move.qty_avail_to_bill else {}
