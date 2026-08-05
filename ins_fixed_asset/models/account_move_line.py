from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_cip_post_journal = fields.Boolean('Is CIP Post Journal', default=False)