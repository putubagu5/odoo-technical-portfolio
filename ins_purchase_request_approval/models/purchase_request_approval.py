from odoo import api, fields, models


class PurchaseRequestApproval(models.Model):
    _name = 'purchase.request.approval'
    _inherit = 'approval.history.mixin'
    _description = 'Purchase Request Approval'

    request_id = fields.Many2one('purchase.request', 'Purchase Request',
                                 ondelete='cascade')
