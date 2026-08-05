from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountTransactionType(models.Model):
    _inherit = 'account.transaction.type'
    _description = 'Transaction Type'

    code_gen21 = fields.Char('Code Gen21', copy=False)
