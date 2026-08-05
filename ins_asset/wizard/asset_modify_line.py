from odoo import api, fields, models


class AssetModifyLine(models.TransientModel):
    _name = 'asset.modify.line'
    _description = 'Asset Modify Line'

    modify_id = fields.Many2one('asset.modify', 'Asset Modify',
                                ondelete='cascade')
    selected = fields.Boolean('Selected', default=False)
    picking_id = fields.Many2one('stock.picking', 'Receipt No.')
    product_id = fields.Many2one('product.product', 'Product',
                                 related='invoice_line_id.product_id')
    invoice_id = fields.Many2one('account.move', 'Invoice')
    invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line')
    date_invoice = fields.Date('Invoice Date', related='invoice_id.invoice_date')
    amount = fields.Float('Amount')
