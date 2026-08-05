from odoo import api, fields, models, _


class ResRegionGen21(models.Model):
    _name = 'res.region.gen21'

    code = fields.Char(string="Code")
    name = fields.Char(string="Name")
