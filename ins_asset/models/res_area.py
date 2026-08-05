from odoo import api, fields, models


class ResArea(models.Model):
    _name = 'res.area'
    _inherit = 'res.master.mixin'
    _description = 'Area'

    city_id = fields.Many2one('res.city', 'City', ondelete='restrict')
