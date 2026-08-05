from odoo import api, fields, models


class ApprovalDelegation(models.Model):
    _inherit = 'approval.delegation'

    module = fields.Selection(selection_add=[
        ('purchase.request', 'Purchase Request'), ('purchase.order',)
    ], ondelete={'purchase.request': 'set default'})
