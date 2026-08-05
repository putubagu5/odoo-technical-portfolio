from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning


class AccountPaymentInvoice(models.Model):
    _name = 'account.payment.invoice'
    _description = 'Payment Invoice'

    payment_id = fields.Many2one('account.payment', 'Payment', required=True)
    name = fields.Char('Invoice No.')
    payment_reference = fields.Char('Payment Reference.')
    date_invoice = fields.Date('Bill Date')
    date_accounting = fields.Date('GL Date')
    account_id = fields.Many2one('account.account', 'Account', compute='_compute_account_id')
    description = fields.Char('Description')
    po_number = fields.Char('PO Number')
    currency_id = fields.Many2one('res.currency', 'Currency')
    amount = fields.Float('Amount')
    move_id = fields.Many2one('account.move', string='Invoices', required=True)
    invoice_state = fields.Selection(selection=[
        ('unapplied', 'Unapplied'),
        ('applied', 'Applied'),
    ], string='Status', default='unapplied', compute='_compute_invoice_state')
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'Inpayment'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled Payment'),
    ], string='Invoice Status', default='not_paid', compute='_compute_invoice_state')

    @api.constrains('payment_id', 'move_id', 'date_accounting', 'invoice_state')
    def _check_invoice_unique(self):
        invoices = []
        for record in self:
            invoice = self.env['account.payment.invoice'].search([('payment_id', '=', record.payment_id.id),
                                                           ('move_id', '=', record.move_id.id)])
            invoices.append(invoice.move_id.id)
        for rec in self:
            jumlah = invoices.count(rec.move_id.id)
            total_count = self.search_count(
                [('payment_id', '=', rec.payment_id.id), ('move_id', '=', rec.move_id.id)])
            print(jumlah, 'sama dengan', total_count)
            if total_count > 1 or jumlah > 1:
                print(rec.move_id.id, 'jumlah', total_count)
                raise ValidationError("Invoice number %s already exists!" % rec.move_id.payment_reference)

    @api.constrains('amount', 'move_id')
    def _check_amount_residual_limit(self):
        for rec in self:
            if rec.amount > rec.move_id.amount_residual:
                raise Warning("Invoice number %s has more amount than amount due!" % rec.move_id.payment_reference)

    @api.depends('payment_id.state', 'move_id.state', 'payment_id.is_matched')
    def _compute_invoice_state(self):
        for invoice in self:
            print(invoice.payment_id.state, 'ini apa statusnya ??')
            invoice.invoice_payment_state = 'not_paid'
            if invoice.payment_id.state != 'posted' \
                    or (invoice.payment_id.reverse_date and invoice.payment_id.state == 'posted'):
                invoice.invoice_state = 'unapplied'
                print(invoice.payment_id.state, 'masuk kondisi pertama ??')
                if invoice.payment_id.reverse_date and invoice.payment_id.state == 'posted':
                    invoice.invoice_payment_state = 'cancelled'
                for line in invoice.move_id.line_ids:
                    if invoice.move_id.amount_residual_signed != 0 and line.reconciled is False:
                        line.payment_id = None
                    elif line.reconciled is True and not invoice.payment_id.reverse_date:
                        invoice.invoice_state = 'unapplied'
                        invoice.invoice_payment_state = 'in_payment'
                    elif line.reconciled is True and invoice.payment_id.reverse_date:
                        print(line, 'masuk kondisi remove_reconcile')
                        # if abs(pay_lines.balance) == invoice.amount and pay_lines.name == invoice.name:
                        #     for account in pay_lines.account_id:
                        #         data_reconcile = (pay_lines + inv_line).filtered_domain([
                        #             ('account_id', '=', account[0].id),
                        #             ('reconciled', '=', False)
                        #         ])
                        #         # print(data_reconcile, "data_reconcile")
                        #         data_reconcile.reconcile()
                        line.remove_move_reconcile()
                        invoice.invoice_state = 'unapplied'
                        invoice.invoice_payment_state = 'cancelled'

                if invoice.move_id.amount_residual_signed != 0 and invoice.payment_id.state == 'posted':
                    print(invoice.payment_id.state, 'masuk kondisi ke 1 dengan dikondisi lagi 1.2')
                    if abs(invoice.move_id.amount_residual_signed) == abs(invoice.move_id.amount_total_signed) \
                            and not invoice.payment_id.reverse_date:
                        print(invoice.payment_id.state, 'masuk kondisi ke 1 dengan dikondisi lagi 1.2.1')
                        # invoice.move_id.payment_state = 'in_payment'
                    elif invoice.payment_id.reverse_date:
                        invoice.invoice_payment_state = 'cancelled'
                    else:
                        print(invoice.payment_id.state, 'masuk kondisi ke 1 dengan dikondisi lagi 1.2.3 kesini?')
                        # invoice.move_id.payment_state = 'in_payment'
                        invoice.invoice_payment_state = 'in_payment'
                elif invoice.move_id.amount_residual_signed == 0 and not invoice.payment_id.is_matched:
                    print(invoice.payment_id.state, 'masuk kondisi ke 1 dengan dikondisi lagi 1.3')
                    # invoice.move_id.payment_state = 'in_payment'
                    invoice.invoice_payment_state = 'in_payment'
                # else:
                #     invoice.move_id.payment_state = 'not_paid'
            elif invoice.payment_id.state == 'posted' and not invoice.payment_id.reverse_date:
                print(invoice.payment_id.state, 'masuk kondisi ke 2 dg status posted tapi tidak di reverse ??')
                invoice.invoice_state = 'applied'
                if invoice.move_id.amount_residual_signed != 0:
                    if abs(invoice.move_id.amount_residual_signed) == abs(invoice.move_id.amount_total_signed):
                        # invoice.move_id.payment_state = 'not_paid'
                        invoice.invoice_payment_state = 'in_payment'
                    else:
                        print(invoice.move_id.payment_state, 'kapan masuk kesini ??')
                        # invoice.move_id.payment_state = 'partial'
                        invoice.invoice_payment_state = 'in_payment'
                elif invoice.move_id.amount_residual_signed == 0:
                    # invoice.move_id.payment_state = 'in_payment'
                    for payment in invoice.payment_id.move_id.line_ids:
                        if payment.reconciled is True:
                            if invoice.payment_id.destination_account_id != payment.account_id:
                                # invoice.move_id.payment_state = 'in_payment'
                                invoice.invoice_payment_state = 'in_payment'
                            elif invoice.payment_id.date_bank_statement is False \
                                    or invoice.payment_id.is_matched is False:
                                # invoice.move_id.payment_state = 'in_payment'
                                invoice.invoice_payment_state = 'in_payment'
                            else:
                                # invoice.move_id.payment_state = 'paid'
                                invoice.invoice_payment_state = 'paid'
                        else:
                            print(invoice.payment_id.state, 'jangan2 masuk sini')
                            # invoice.move_id.payment_state = 'not_paid'
                elif invoice.payment_id.reverse_date or invoice.payment_id.reverse_user_by:
                    invoice.invoice_payment_state = 'cancelled'
            else:
                print(invoice.payment_id.state, 'masuk kondisi ke 3 dengan semua kondisi tidak ada yang masuk')
                invoice.invoice_payment_state = 'not_paid'
                invoice.move_id.payment_state = 'not_paid'
                # else:
                #     invoice.move_id.payment_state = 'not_paid'

    @api.onchange('move_id')
    def _onchange_set_values(self):
        for rec in self:
            if rec.move_id:
                move = self.env['account.move'].sudo().browse(rec.move_id.id)
                description = '%s' % (move.ref or '')
                rec.name = move.name
                rec.payment_reference = move.payment_reference or False
                rec.date_invoice = move.invoice_date
                rec.date_accounting = move.date
                rec.description = description
                rec.po_number = move.po_numbers
                rec.currency_id = move.currency_id.id
                rec.amount = move.amount_residual

    @api.depends('move_id.line_ids')
    def _compute_account_id(self):
        for rec in self:
            if rec.move_id:
                ln = rec.move_id.line_ids.filtered(lambda x: x.credit and x.account_id.internal_type == 'payable')
                account = ln.account_id
                rec.account_id = account.id or False
            else:
                rec.account_id = False
