from odoo import models, fields, api


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'
    _description = 'Account Payment Term'

    is_default_gen21 = fields.Boolean(string="Is Default Gen21")
