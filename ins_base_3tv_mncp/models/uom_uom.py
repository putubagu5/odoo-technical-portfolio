from odoo import api, fields, models


class UomUom(models.Model):
    _inherit = 'uom.uom'

    note = fields.Text('Description')
