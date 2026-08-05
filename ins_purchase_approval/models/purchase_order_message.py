from odoo import api, fields, models


class PurchaseOrderMessage(models.Model):
    _name = 'purchase.order.message'
    _inherit = 'approval.message.mixin'
    _description = 'Purchase Order Message'

    order_id = fields.Many2one('purchase.order', 'Purchase Order',
                               ondelete='cascade')
