from odoo import api, fields, models


class MncOperatingUnit(models.Model):
    _name = 'mnc.operating.unit'
    _description = 'MNC Operating Unit'

    name = fields.Char('Name', copy=False)
    note = fields.Text('Note')
