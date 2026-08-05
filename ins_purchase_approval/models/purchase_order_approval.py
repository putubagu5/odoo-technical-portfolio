from odoo import api, fields, models


class PurchaseOrderApproval(models.Model):
    _name = 'purchase.order.approval'
    _inherit = 'approval.history.mixin'
    _description = 'Purchase Order Approval'

    order_id = fields.Many2one('purchase.order', 'Purchase Order',
                               ondelete='cascade')
