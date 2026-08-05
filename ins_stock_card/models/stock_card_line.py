from odoo import fields, models


class StockCardLine(models.Model):
    _name = 'stock.card.line'
    _description = 'Stock Card Line'

    name = fields.Char('Description')
    stock_card_id = fields.Many2one('stock.card', 'Related Stock Card',
                                    ondelete='cascade')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    move_id = fields.Many2one('stock.move', 'Stock Move')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    date = fields.Datetime('Date')
    qty_start = fields.Float('Qty. Start')
    qty_in = fields.Float('Qty. In')
    qty_out = fields.Float('Qty. Out')
    qty_balance = fields.Float('Qty. Balance')
    value = fields.Float('Value')
    price = fields.Float('Price')
