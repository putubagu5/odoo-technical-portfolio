# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    budget_check_account_move = fields.Boolean(string="Budget Checking on Journal Entry", default=True,
                                  help="Check this field if Journal Entry must check Budget.")
