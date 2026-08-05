from odoo import fields, models, api


class InheritAccountJournal(models.Model):
    _inherit = "account.journal"

    remitted_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Remitted Account')
