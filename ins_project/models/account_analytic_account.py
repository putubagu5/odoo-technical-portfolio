from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    departement_code = fields.Char('Departement Code')
    analytic_seq_id = fields.Many2one(
        'ir.sequence', 'Analytic Account Sequence')
