from odoo import api, fields, models


class AssetSegment(models.Model):
    _name = 'asset.segment'
    _inherit = 'res.master.mixin'
    _description = 'Asset Segment'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
