# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountBankStatementGenerate(models.TransientModel):
    _inherit = 'account.bank.statement.generate'

    misc_payment_ids = fields.Many2many('miscellaneous.miscellaneous', ondelete='cascade')

    def process(self):
        res = super(AccountBankStatementGenerate, self).process()
        for misc_payment in self.misc_payment_ids:
            amount = misc_payment.amount
            if misc_payment.currency_id != misc_payment.journal_id.currency_id:
                for line in misc_payment.move_id.line_ids:
                    if line.balance > 0:
                        amount = line.balance

            self.env['account.bank.statement.line'].create({
                'statement_id': self.statement_id.id,
                'payment_ref': misc_payment.name,
                'partner_id': misc_payment.misc_partner_id.id or False,
                'ref': misc_payment.misc_name,
                'amount': misc_payment.receipt_type_id.type == 'receive' and amount or -amount,
                'matched_misc_payment_ids': [(6, 0, misc_payment.ids)],
                'date': self.statement_id.date
            })

        return res
