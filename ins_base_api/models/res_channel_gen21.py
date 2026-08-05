from odoo import api, fields, models, _


class ResChannelGen21(models.Model):
    _name = 'res.channel.gen21'

    code = fields.Char(string="Code")
    name = fields.Char(string="Name")
