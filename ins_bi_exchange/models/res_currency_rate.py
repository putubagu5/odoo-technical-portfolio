from odoo import api, fields, models


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    actual_rate = fields.Float(digits=0, default=1.0)

    @api.onchange('rate')
    def _onchange_actual_rate(self):
        """ onchange function to calculate actual_rate based on rate """
        self.actual_rate = 1 / self.rate

    @api.onchange('actual_rate')
    def _onchange_rate(self):
        """ onchange function to calculate rate based on the actual_rate """
        self.rate = 1 / self.actual_rate

    @api.model
    def create(self, vals):
        """ override create function to calculate actual_rate from rate """
        if not vals.get('actual_rate') and vals.get('rate'):
            vals['actual_rate'] = 1 / vals['rate']
        res = super(ResCurrencyRate, self).create(vals)
        return res
