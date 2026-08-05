from odoo import api, fields, models


class PaymentInvoiceLine(models.TransientModel):
    _name = 'wizard.payment.invoice.line'
    _description = 'Payment Invoice Line'

    payment_id = fields.Many2one('wizard.payment.invoice', 'Payment',
                                 ondelete='cascade')
    name = fields.Char('Invoice No.')
    payment_reference = fields.Char('Payment Reference.')
    date_invoice = fields.Date('Bill Date')
    date_accounting = fields.Date('GL Date')
    account_id = fields.Many2one('account.account', 'Account')
    description = fields.Char('Description')
    po_number = fields.Char('PO Number')
    currency_id = fields.Many2one('res.currency', 'Currency')
    amount = fields.Float('Amount')
    move_id = fields.Many2one('account.move', string='Invoices')
