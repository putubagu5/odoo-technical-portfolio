from odoo import api, fields, models


class ResCity(models.Model):
    _name = 'res.city'
    _description = 'List of Cities'

    name = fields.Char('Kota/Kabupaten', index=True)
    type = fields.Selection([
        ('kota', 'Kota'),
        ('kab', 'Kabupaten'),
    ], 'Type', index=True)
    state_id = fields.Many2one('res.country.state', 'State', ondelete='restrict',
                               domain='[("country_id", "=?", country_id)]')
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')

    _sql_constraints = [
        ('city_uniq', 'UNIQUE(name, type)',
         'City already exist, City must be unique !')
    ]

    @api.onchange('country_id')
    def _onchange_country(self):
        """ onchange function to empty state_id """
        # check if state's country and country is the same
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        """ onchange function to set country_id using states's country """
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
