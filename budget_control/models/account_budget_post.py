# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountBudgetPost(models.Model):
    _inherit = 'account.budget.post'

    budget_type = fields.Selection([
        ('abs', "Absolute"), ('adv', "Advisory")
    ], string="Budget Type", default='abs', required=True)

    @api.onchange('account_ids')
    def _onchange_account_ids(self):
        for record in self:
            if record.account_ids:
                first_account = record.account_ids[0]
                record.name = first_account.name
            else:
                record.name = False
