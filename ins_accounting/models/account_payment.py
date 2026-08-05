from num2words import num2words
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    voucher_no = fields.Char('Payment Voucher', default='/')
    inv_ref = fields.Char('Description', compute='_compute_ref_payment_ids', store=True)
    payment_invoice_ids = fields.One2many('account.payment.invoice',
                                          'payment_id', 'Invoices')
    transfer_id = fields.Many2one('bank.cash.transfer', 'Bank Cash Transfer',
                                  ondelete='cascade', index=True)
    document_no = fields.Char('Document No')
    giro_no = fields.Char('Giro No')
    rate = fields.Float('Rate', compute='_compute_rate')
    amount_in_words = fields.Char('Amount To Words', compute='amount_to_text')
    amount_in_words_2 = fields.Char('Amount To Words 2', compute='amount_to_text_2')
    amount_to_slip = fields.Char('Amount To Slip', compute='compute_amount_to_slip')
    amount_text_idr = fields.Char('Amount To Slip', compute='compute_amount_text_idr')
    amount_payment_invoice = fields.Monetary(currency_field='currency_id', string="Total", compute='_set_amount_payment_invoice')
    payment_doc_master_id = fields.Many2one('res.payment.document', 'Series',
                                            domain='[("journal_id", "=", journal_id)]')
    payment_doc_id = fields.Many2one(
        'res.payment.document.line', 'Document No',
        domain='[("document_id", "=", payment_doc_master_id), ("is_used", "=", False), ("cancelled", "=", False)]')
    giro_master_id = fields.Many2one('res.giro', 'Giro Series',
                                     domain='[("journal_id", "=", journal_id)]')
    giro_id = fields.Many2one(
        'res.giro.line', 'Giro No',
        domain='[("giro_id", "=", giro_master_id), ("is_used", "=", False), ("cancelled", "=", False)]')

    words1 = fields.Char(string="Words 1", compute="_compute_words")
    words2 = fields.Char(string="Words 2", compute="_compute_words")
    words3 = fields.Char(string="Words 3", compute="_compute_words2")
    words4 = fields.Char(string="Words 4", compute="_compute_words2")

    giro_words1 = fields.Char(string="Giro Words 1", compute="_compute_giro_words")
    giro_words2 = fields.Char(string="Giro Words 2", compute="_compute_giro_words")
    # is_assign_to_bank_statement = fields.Boolean(string='Is Assign to Bank Statement', default=False)

    # @api.constrains('payment_invoice_ids', 'id')
    # def _check_payment_invoice_ids(self):
    #     """ constrains function to check if any payment_invoice_ids has duplicate """
    #     self.ensure_one()
    #     # map all payment_invoice_ids based on the invoice_id, get the id
    #     all_invoices = self.payment_invoice_ids.mapped('invoice_id.id')

    #     # then map to dict
    #     invoice_dict = {i: all_invoices.count(i) for i in all_invoices}

    #     # then get the dict values and check if any > 1
    #     d_val = invoice_dict.values()
    #     d_val = [x for x in d_val if x > 1]

    #     if d_val:
    #         raise ValidationError('There is duplicate invoice number!')

    @api.depends('amount_in_words_2')
    def _compute_words(self):
        for record in self:
            words1 = ''
            words2 = ''
            if record.amount_in_words_2:
                txt_split = record.amount_in_words_2.split()
                if len(txt_split) > 0:
                    is_words2 = False
                    for text in txt_split:
                        if len(words1 + text) < 78 and is_words2 == False:
                            words1 = words1 + text + ' '
                        else:
                            is_words2 = True
                            words2 = words2 + text + ' '
                    record.words1 = words1
                    record.words2 = words2

    @api.depends('amount_in_words_2')
    def _compute_giro_words(self):
        for record in self:
            giro_words1 = ''
            giro_words2 = ''
            if record.amount_in_words_2:
                txt_split = record.amount_in_words_2.split()
                if len(txt_split) > 0:
                    is_words2 = False
                    for text in txt_split:
                        if len(giro_words1 + text) < 25 and is_words2 == False:
                            giro_words1 = giro_words1 + text + ' '
                        else:
                            is_words2 = True
                            giro_words2 = giro_words2 + text + ' '
                    record.giro_words1 = giro_words1
                    record.giro_words2 = giro_words2

    @api.depends('amount_to_slip')
    def _compute_words2(self):
        for record in self:
            words3 = ''
            words4 = ''
            if record.amount_to_slip:
                txt_split = record.amount_to_slip.split()
                if len(txt_split) > 0:
                    is_words4 = False
                    for text in txt_split:
                        if len(words3 + text) < 78 and is_words4 == False:
                            words3 = words3 + text + ' '
                        else:
                            is_words4 = True
                            words4 = words4 + text + ' '
                    record.words3 = words3
                    record.words4 = words4

    @api.model
    def create(self, vals):
        """ inherit function to add voucher_no """
        # get from sequence
        if vals.get('voucher_no', '') == '/':
            vals['voucher_no'] = self.env['ir.sequence'].next_by_code('payment.voucher')
        res = super(AccountPayment, self).create(vals)
        return res

    @api.onchange('payment_doc_master_id')
    def _onchange_payment_doc_master(self):
        """ onchange function to set payment_doc_id with the first record """
        self.ensure_one()
        if self.payment_doc_master_id and self.payment_doc_master_id.line_ids:
            first = self.payment_doc_master_id.line_ids.sorted(key=lambda x: x.name)
            first = first.filtered(lambda x: not x.is_used and not x.cancelled)
            if first:
                self.payment_doc_id = first[0].id
            else:
                raise ValidationError('This series has no usable Document Number')

    @api.onchange('payment_invoice_ids')
    def _onchange_payment_invoice_ids2(self):
        """ onchange function to set ref field to contain description of lines """
        self.ref = ', '.join(self.payment_invoice_ids.mapped('description'))

    @api.onchange('giro_master_id')
    def _onchange_giro_master(self):
        """ onchange function to set giro_id with the first record """
        self.ensure_one()
        if self.giro_master_id and self.giro_master_id.line_ids:
            first = self.giro_master_id.line_ids.sorted(key=lambda x: x.name)
            first = first.filtered(lambda x: not x.is_used and not x.cancelled)
            if first:
                self.giro_id = first[0].id
            else:
                raise ValidationError('This series has no usable Giro Number')

    def action_cancel(self):
        """ inherit function to set to cancel """
        super(AccountPayment, self).action_cancel()
        # check if payment_doc_id exists
        if self.payment_doc_id:
            self.payment_doc_id.cancelled = True

        # check if giro_id exists
        if self.giro_id:
            self.giro_id.cancelled = True

        # check if check_id exists
        if self.check_id:
            self.check_id.cancelled = True

    @api.depends('date', 'manual_currency_rate_active', 'manual_currency_rate')
    def _compute_rate(self):
        """ compute function to calculate rate based on date or manual """
        for rec in self:
            if rec.manual_currency_rate_active:
                rec.rate = rec.manual_currency_rate
            else:
                lines = rec.currency_id.rate_ids.filtered(
                    lambda x: x.name <= rec.date)
                rec.rate = lines[0].actual_rate if lines else 0

    @api.depends('payment_invoice_ids')
    def _compute_ref_payment_ids(self):
        for record in self:
            inv = ''
            inv_numbers = record.payment_invoice_ids.mapped('name')
            inv = ', '.join(map(str, inv_numbers))
            record.inv_ref = inv

    @api.depends('amount', 'currency_id')
    def amount_to_text(self):
        for rec in self:
            if rec.currency_id:
                # lang = 'id' if self.currency_id.name == 'IDR' else 'en'
                lang = 'en'
                currency_in_words = rec.currency_id.currency_unit_label
                subunit_in_words = rec.currency_id.currency_subunit_label

                unit, sub_unit = str.format('{:.2f}', rec.amount).split(".")
                unit = num2words(int(unit), lang=lang)
                sub_unit = num2words(int(sub_unit), lang=lang)
                # check if sub unit is zero or not
                if sub_unit != 'zero':
                    rec.amount_in_words = unit.title() + " " + currency_in_words + " " + sub_unit.title() + " " + subunit_in_words
                else:
                    rec.amount_in_words = unit.title() + " " + currency_in_words
            else:
                rec.amount_in_words = ''

    @api.depends('amount', 'currency_id')
    def amount_to_text_2(self):
        for rec in self:
            if rec.currency_id:
                lang = 'id' if rec.currency_id.name == 'IDR' else 'en'
                currency_in_words = rec.currency_id.currency_unit_label
                subunit_in_words = rec.currency_id.currency_subunit_label

                unit, sub_unit = str.format('{:.2f}', rec.amount).split(".")
                unit = num2words(int(unit), lang=lang)
                sub_unit = num2words(int(sub_unit), lang=lang)
                # check if sub unit is zero or not
                if sub_unit not in ["zero", "nol"]:
                    if lang == 'id':
                        rec.amount_in_words_2 = unit.title() + " " + currency_in_words + " " + sub_unit.title() + " " + subunit_in_words
                    else:
                        rec.amount_in_words_2 = unit.title() + " " + currency_in_words + " " + sub_unit.title() + " " + subunit_in_words
                else:
                    rec.amount_in_words_2 = unit.title() + " " + currency_in_words
            else:
                rec.amount_in_words_2 = ''

    @api.depends('amount', 'currency_id')
    def compute_amount_to_slip(self):
        for rec in self:
            if rec.currency_id:
                lang_2 = 'id'
                currency_to_slip = 'Rupiah'
                # convert to integer to remove decimal place
                amount = 0.0
                if rec.manual_currency_rate_active is True:
                    amount = rec.amount * rec.manual_currency_rate
                else:
                    amount = rec.amount
                words_amount_2 = num2words(int(amount), lang=lang_2)
                rec.amount_to_slip = words_amount_2.title() + " " + currency_to_slip
            else:
                rec.amount_to_slip = ''

    @api.depends('amount', 'currency_id')
    def compute_amount_text_idr(self):
        for rec in self:
            if rec.currency_id:
                lang = 'id'
                currency_in_words = rec.currency_id.currency_unit_label
                subunit_in_words = rec.currency_id.currency_subunit_label

                unit, sub_unit = str.format('{:.2f}', rec.amount).split(".")
                unit = num2words(int(unit), lang=lang)
                sub_unit = num2words(int(sub_unit), lang=lang)
                # check if sub unit is zero or not
                if sub_unit not in ["zero", "nol"]:
                    rec.amount_text_idr = unit.title() + " " + currency_in_words + " " + sub_unit.title() + " " + subunit_in_words
                else:
                    rec.amount_text_idr = unit.title() + " " + currency_in_words
            else:
                rec.amount_text_idr = ''

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        self.ensure_one()
        if self.move_id and self.move_id.state == 'posted':
            self.action_reconcile()
        return res

    def action_reconcile(self):
        self.ensure_one()
        for rec in self:
            print(rec.state, 'isi status payment ketika post')
            if rec.state == 'posted':
                # Auto reconcile
                domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
                to_reconcile = []
                for invoice in rec.payment_invoice_ids:
                    for inv_line in invoice.move_id.line_ids.filtered_domain(domain):
                        # print(inv_line,"ini isinya invoice_lines")
                        # print(rec.line_ids, "ini isinya line_ids")
                        payment_lines = rec.line_ids.filtered_domain(domain)
                        # print(payment_lines, "payment_lines ini isinya apa aja",invoice)
                        for pay_lines in payment_lines:
                            # print(abs(pay_lines.balance), "sama dengan ", invoice.amount)
                            # print(pay_lines.move_name, "sama dengan ", invoice.name)
                            # print(inv_line.move_name, "sama dengan ", invoice.name)
                            # print(pay_lines.ref, "sama dengan ", invoice.description)
                            if (abs(pay_lines.balance) == invoice.amount and inv_line.move_name == invoice.name) \
                                or (abs(pay_lines.balance) == invoice.amount and pay_lines.ref == invoice.description) \
                                    or (inv_line.move_name == invoice.name and pay_lines.ref == invoice.description):
                                for account in pay_lines.account_id:
                                    data_reconcile = (pay_lines + inv_line).filtered_domain([
                                        ('account_id', '=', account[0].id),
                                        ('reconciled', '=', False)
                                    ])
                                    # print(data_reconcile, "data_reconcile")
                                    data_reconcile.reconcile()
                        to_reconcile.append(inv_line)
                    if invoice.move_id.amount_residual_signed != 0:
                        if abs(invoice.move_id.amount_residual_signed) == abs(invoice.move_id.amount_total_signed):
                            invoice.move_id.payment_state = 'not_paid'
                        else:
                            invoice.move_id.payment_state = 'partial'
                    elif invoice.move_id.amount_residual_signed == 0:
                        # invoice.move_id.payment_state = 'in_payment'
                        for payment in invoice.payment_id.move_id.line_ids:
                            if payment.reconciled is True:
                                if invoice.payment_id.destination_account_id != payment.account_id:
                                    invoice.move_id.payment_state = 'in_payment'
                                elif invoice.payment_id.date_bank_statement is False:
                                    invoice.move_id.payment_state = 'in_payment'
                                else:
                                    invoice.move_id.payment_state = 'paid'
                            elif payment.reconciled is False:
                                invoice.move_id.payment_state = 'in_payment'
                    # else:
                    #     invoice.move_id.payment_state = 'not_paid'
                # print(to_reconcile,"to_reconcile ini isinya apa aja sih")
                # for lines in to_reconcile:
                #     print(lines,"ini isinya lines")
                #     print(rec.line_ids, "ini isinya line_ids")
                #     payment_lines = rec.line_ids.filtered_domain(domain)
                #     print(payment_lines, "payment_lines ini isinya apa aja")
                #     for account in payment_lines.account_id:
                #         data_reconcile = (payment_lines + lines).filtered_domain([
                #             ('account_id', '=', account[0].id),
                #             ('reconciled', '=', False)
                #         ])
                #         print(data_reconcile, "data_reconcile")
                #         data_reconcile.reconcile()

            if rec.payment_doc_id:
                rec.payment_doc_id.payment_id = rec.id

            if rec.giro_id:
                rec.giro_id.payment_id = rec.id


    def button_to_confirm(self):
        """ function to change state from draft to confirm """
        for rec in self:
            rec.write({'state': 'confirm'})
        return True

    def mark_check_as_sent(self):
        """ function to mark all payments with check to sent """
        if any([x for x in self if not x.is_check]):
            raise ValidationError('Cannot mark payment that is not Check to sent')
        self.mark_as_sent()

    @api.depends('payment_invoice_ids')
    def _set_amount_payment_invoice(self):
        self.amount_payment_invoice = sum(self.payment_invoice_ids.mapped('amount'))

    # @api.onchange('payment_invoice_ids')
    # def _onchange_payment_invoice_ids(self):
    #     self.amount_payment_invoice = sum(self.payment_invoice_ids.mapped('amount'))

    def _has_document_no(self):
        """ helper function to check if record has valid document_no """
        # valid document_no is number connected to this record
        domain = [
            ('document_id.journal_id', '=', self.journal_id.id),
            ('payment_id', '=', self.id),
        ]
        res = self.env['res.payment.document.line'].search_count(domain)
        return res

    def button_get_document_no(self):
        """ function to get document number from payment document records """
        # quit if record has document_no
        if self._has_document_no():
            return True

        # find unused number data with same journal
        domain = [
            ('document_id.journal_id', '=', self.journal_id.id),
            ('is_used', '=', False),
        ]
        res = self.env['res.payment.document.line'].search(domain, limit=1, order='name')

        if res:
            self.document_no = res.name  # assign if found
            res.write({'payment_id': self.id})  # then write to use
        else:  # document runs out of usable number, raise error
            raise ValidationError('There is no more usable Document Number')

        return True

    def _has_giro_no(self):
        """ helper function to check if record has valid giro_no """
        # valid giro_no is number connected to this record
        domain = [
            ('giro_id.journal_id', '=', self.journal_id.id),
            ('payment_id', '=', self.id),
        ]
        res = self.env['res.giro.line'].search_count(domain)
        return res

    def button_get_giro_no(self):
        """ function to get giro number from payment giro records """
        # quit if record has giro_no
        if self._has_giro_no():
            return True

        # find unused number data with same journal
        domain = [
            ('giro_id.journal_id', '=', self.journal_id.id),
            ('is_used', '=', False),
        ]
        res = self.env['res.giro.line'].search(domain, limit=1, order='name')

        if res:
            self.giro_no = res.name  # assign if found
            res.write({'payment_id': self.id})  # then write to use
        else:  # giro runs out of usable number, raise error
            raise ValidationError('There is no more usable giro Number')

        return True
