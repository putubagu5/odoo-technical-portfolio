from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_default = fields.Boolean('Is Default', default=False)
    is_none_budget = fields.Boolean('None Budget')
