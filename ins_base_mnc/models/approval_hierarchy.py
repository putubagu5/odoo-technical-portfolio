from odoo import api, fields, models


class ApprovalHierarchy(models.Model):
    _inherit = 'approval.hierarchy'

    buyer_id = fields.Many2one('res.buyer', 'Buyer')
