from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_overlimit = fields.Boolean('Allow Credit Overlimit', default=False,
                                     help='Allow overlimit for partner')
