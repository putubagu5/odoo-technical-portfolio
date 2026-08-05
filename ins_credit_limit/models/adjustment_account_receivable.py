# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Adjustment(models.Model):
    _inherit = 'ar.adjustment'

    def action_post(self):
        res = super(Adjustment, self).action_post()

        user_limit_id = self.env['credit.note.limit'].search([
            ('user_id', '=', self.create_uid.id), ('limit_usage', '=', 'ar_adjustment'),
            ('currency_id', '=', self.currency_id.id),
        ], limit=1)

        if user_limit_id and self.total_amount > user_limit_id.amount_to:
            raise ValidationError(_("Total Amount exceeds the AR Adjustment limit."))

        return res
