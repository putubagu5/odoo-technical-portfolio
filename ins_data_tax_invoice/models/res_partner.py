from odoo import api, fields, models
from .check_npwp import _check_npwp


class ResPartner(models.Model):
    _inherit = 'res.partner'

    kelurahan_id = fields.Many2one('res.kelurahan', 'Kelurahan',
                                   domain='[("kecamatan_id", "=?", kecamatan_id)]')
    kecamatan_id = fields.Many2one('res.kecamatan', 'Kecamatan',
                                   domain='[("city_id", "=?", city_id)]')
    city_id = fields.Many2one('res.city', 'Kota/Kabupaten',
                              domain='[("state_id", "=?", state_id)]')
    npwp = fields.Char('NPWP')
    blok = fields.Char('Blok')
    nomor = fields.Char('Nomor')
    rt = fields.Char('RT')
    rw = fields.Char('RW')
    full_address = fields.Char('Full Address', compute='_compute_full_address')

    @api.onchange('npwp')
    def _onchange_npwp(self):
        """ onchange function to format npwp """
        return _check_npwp(self.npwp)

    @api.onchange('state_id')
    def _onchange_state(self):
        """ onchange function to empty city_id """
        if self.city_id and self.state_id != self.city_id.state_id:
            self.city_id = False

    @api.onchange('city_id')
    def _onchange_city(self):
        """ onchange function to empty kecamatan_id """
        if self.kecamatan_id and self.city_id != self.kecamatan_id.city_id:
            self.kecamatan_id = False

    @api.onchange('kecamatan_id')
    def _onchange_kecamatan(self):
        """ onchange function to empty kelurahan_id """
        if self.kelurahan_id and self.kecamatan_id != self.kelurahan_id.kecamatan_id:
            self.kelurahan_id = False

    @api.depends('street', 'street2', 'city', 'state_id', 'country_id', 'blok',
                 'nomor', 'rt', 'rw', 'kecamatan_id', 'kelurahan_id')
    def _compute_full_address(self):
        for rec in self:
            address = rec.street or ''
            address += ' ' + (rec.street2 or '')

            if rec.blok:
                address += ' Blok: ' + rec.blok + ', '
            if rec.nomor:
                address += ' Nomor: ' + rec.nomor + ', '

            if rec.rt:
                address += ' RT: ' + rec.rt
            if rec.rw:
                address += ' RW: ' + rec.rw

            if rec.kelurahan_id:
                address += ' Kel: ' + rec.kelurahan_id.name + ','

            if rec.kecamatan_id:
                address += ' Kec: ' + rec.kecamatan_id.name

            if rec.city_id:
                address += """
            """ + rec.city_id.name + ','

            if not rec.city_id and rec.city:
                address += """
            """ + rec.city + ','

            if rec.state_id:
                address += ' ' + rec.state_id.name

            rec.full_address = address.upper()
