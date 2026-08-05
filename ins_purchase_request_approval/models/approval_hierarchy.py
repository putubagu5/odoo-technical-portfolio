from odoo import api, fields, models


class ApprovalHierarchy(models.Model):
    _inherit = 'approval.hierarchy'

    module = fields.Selection(selection_add=[
        ('purchase.request', 'Purchase Request'), ('purchase.order',)
    ], ondelete={'purchase.request': 'set default'})
