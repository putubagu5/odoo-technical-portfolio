from odoo import api, fields, models


class AssetCondition(models.Model):
    _name = 'asset.condition'
    _inherit = 'res.master.mixin'
    _description = 'Asset Condition'
