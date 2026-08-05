# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        if self.move_type == 'out_refund':
            user_limit_id = self.env['credit.note.limit'].search([
                ('user_id', '=', self.invoice_user_id.id), ('limit_usage', '=', 'credit_note'),
                ('currency_id', '=', self.currency_id.id),
            ], limit=1)

            if user_limit_id and self.amount_total > user_limit_id.amount_to:
                raise ValidationError(_("Total Amount exceeds the Credit Memo limit."))

        return res
