from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    amount_total = fields.Float('Amount')
    amount_move = fields.Float(
        string='Amount from Move',
        related='move_id.amount_total')
    qty_move = fields.Float(
        string='Quantity total from move',
        related='move_id.product_uom_qty')

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        price_each = 1
        if self.qty_move > 0:
            price_each = self.amount_move / self.qty_move
        self.amount_total = price_each * self.qty_done
        # elif self.qty_move < 0:
        #     raise ValidationError(
        #         'Division by zero, please check qty demand in picking.')

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        price_each = 1
        if self.qty_move > 0:
            price_each = self.amount_move / self.qty_move
            # if not price_each:
            #     raise ValidationError('Division by zero, please check qty demand in picking.')
        self.qty_done = self.amount_total / price_each
        # elif self.qty_move < 0:
        #     raise ValidationError(
        #         'Division by zero, please check qty demand in picking.')
