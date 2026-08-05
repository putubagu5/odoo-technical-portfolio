# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    matched_misc_payment_ids = fields.Many2many('miscellaneous.miscellaneous',
                                                relation='bank_statement_line_matched_misc_payment_rel')
