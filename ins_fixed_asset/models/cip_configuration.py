from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CipConfiguration(models.Model):
    _name = 'cip.configuration'
    _description = 'CIP Configuration'

    name = fields.Char('CIP Name')
    code = fields.Char('CIP Code')
    account_id = fields.Many2one('account.account','Account CIP')
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False)
