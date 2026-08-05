from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    use_product_expense = fields.Boolean('Use Product Expense Account',
                                         default=False)
