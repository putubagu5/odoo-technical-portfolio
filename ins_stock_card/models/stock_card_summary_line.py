from odoo import fields, models


class StockCardSummaryLine(models.Model):
    _name = 'stock.card.summary.line'
    _description = 'Stock Card Summary Line'

    name = fields.Char('Description')
    summary_id = fields.Many2one('stock.card.summary', 'Related Stock Card',
                                 ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    move_id = fields.Many2one('stock.move', 'Stock Move')
    qty_start = fields.Float('Qty. Start')
    qty_in = fields.Float('Qty. In')
    qty_out = fields.Float('Qty. Out')
    qty_balance = fields.Float('Qty. Balance')
    value = fields.Float('Value')
    price = fields.Float('Price')
