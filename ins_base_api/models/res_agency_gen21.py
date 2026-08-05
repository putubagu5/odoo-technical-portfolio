from odoo import api, fields, models, _


class ResAgencyGen21(models.Model):
    _name = 'res.agency.gen21'

    code = fields.Char(string="Code")
    name = fields.Char(string="Name")
    type = fields.Char(string="Type")
    source = fields.Char(string="Source")
