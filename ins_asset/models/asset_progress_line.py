from odoo import api, fields, models


class AssetProgressLine(models.Model):
    _name = 'asset.progress.line'
    _description = 'Asset Progress Line'

    progress_id = fields.Many2one('asset.progress', 'Progress',
                                  ondelete='cascade')
    selected = fields.Boolean('Selected', default=True)
    move_id = fields.Many2one('account.move', 'Invoice')
    move_line_id = fields.Many2one('account.move.line', 'Invoice Line')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='move_line_id.analytic_account_id')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    product_id = fields.Many2one('product.product', 'Product',
                                 related='move_line_id.product_id')
    asset_cost_progress_id = fields.Many2one('cip.configuration', 'CIP',
                                             ondelete='restrict')
    qty = fields.Float('Qty Invoice')
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Float('Subtotal')
