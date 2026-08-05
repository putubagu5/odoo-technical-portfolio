from odoo import api, fields, models


class PurchaseRequestMessage(models.Model):
    _name = 'purchase.request.message'
    _inherit = 'approval.message.mixin'
    _description = 'Purchase Request Message'

    request_id = fields.Many2one('purchase.request', 'Purchase Request',
                                 ondelete='cascade')
