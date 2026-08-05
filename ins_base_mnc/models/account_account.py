from odoo import api, fields, models, _
from odoo.tools.misc import format_date


class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    is_none_budget = fields.Boolean('None Budget')
    is_reverse_budget = fields.Boolean("Reverse Budget Credit")
