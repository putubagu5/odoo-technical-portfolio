from odoo import api, fields, models


class ResKecamatan(models.Model):
    _name = 'res.kecamatan'
    _description = 'List of Kecamatan'

    name = fields.Char('Kecamatan', index=True)
    city_id = fields.Many2one('res.city', 'City')

    _sql_constraints = [
        ('kecamatan_uniq', 'UNIQUE(name, city_id)',
         'Kecamatan already exists, Kecamatan must be unique !')
    ]
