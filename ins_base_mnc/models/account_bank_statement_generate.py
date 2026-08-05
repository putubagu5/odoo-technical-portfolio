from odoo import fields, models, api


class AccountBankStatementGenerate(models.TransientModel):
    _inherit = 'account.bank.statement.generate'

    payment_ids = fields.Many2many('account.payment')

    # @api.onchange('payment_ids')
    # def _compute_check_payment_not_reversed(self):
    #     """ compute function to get multi_payment_reference """
    #     print('masuk statement line')
    #     reverse_move = self.env["account.bank.statement.line"].search([('cancel_reversal', '=', True)])
    #     for rec in reverse_move:
    #         if rec:
    #             payments = self.payment_ids
    #             payments.append(reverse_move.payment_id)


    # def process(self):
    #     res = super(AccountBankStatementGenerate, self).process()
    #     for payment in self.payment_ids:
    #         print(payment)
    #         amount = payment.amount
    #         # check if currency journal is difference with currency transaction, then use currency journal
    #         if payment.currency_id.id != payment.journal_id.currency_id.id \
    #                 or payment.currency_id.id != payment.company_id.currency_id.id:
    #             amount = payment.move_id.amount_total_signed
    #         self.env['account.bank.statement.line'].create({
    #             'statement_id': self.statement_id.id,
    #             'payment_ref': payment.name,
    #             'partner_id': payment.partner_id.id or False,
    #             'ref': payment.payment_reference,
    #             'amount': payment.payment_type == 'inbound' and amount or -amount,
    #             'matched_payment_ids': [(6, 0, payment.ids)],
    #             'date': self.statement_id.date
    #         })
    #
    #     for invoice in self.invoice_ids:
    #         amount_residual = invoice.currency_id._convert(invoice.amount_residual, self.statement_id.currency_id,
    #                                                        self.statement_id.company_id, self.statement_id.date)
    #         sign = invoice.is_inbound() and 1 or -1
    #         self.env['account.bank.statement.line'].create({
    #             'statement_id': self.statement_id.id,
    #             'payment_ref': invoice.name,
    #             'partner_id': invoice.partner_id.id or False,
    #             'ref': invoice.ref,
    #             'amount': self.statement_id.currency_id.round(amount_residual * sign),
    #             'matched_move_line_ids': [(6, 0, invoice.line_ids.filtered(
    #                 lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')).ids)],
    #             'date': self.statement_id.date
    #         })
    #
    #     return res
