from odoo import api, fields, models


class AssetLocation(models.Model):
    _name = 'asset.location'
    _inherit = 'res.master.mixin'
    _description = 'Asset Location'

    building_id = fields.Many2one('res.building', 'Building', ondelete='restrict')
    floor_id = fields.Many2one('res.floor', 'Floor', ondelete='restrict')
    city_id = fields.Many2one('res.city', 'City', ondelete='restrict')
    area_id = fields.Many2one('res.area', 'Area', ondelete='restrict')
