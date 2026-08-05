from odoo import api, fields, models


class ResBuilding(models.Model):
    _name = 'res.building'
    _inherit = 'res.master.mixin'
    _description = 'Building'

    area_id = fields.Many2one('res.area', 'Area', ondelete='restrict')
    city_id = fields.Many2one('res.city', 'City', ondelete='restrict')
