from odoo import api, fields, models


class ResKelurahan(models.Model):
    _name = 'res.kelurahan'
    _description = 'List of Kelurahan'

    name = fields.Char('Kelurahan', index=True)
    zip_code = fields.Char('ZIP Code')
    kecamatan_id = fields.Many2one('res.kecamatan', 'Kecamatan')

    _sql_constraints = [
        ('kelurahan_uniq', 'UNIQUE(name, kecamatan_id)',
         'Kelurahan already exist, Kelurahan must be unique !')
    ]