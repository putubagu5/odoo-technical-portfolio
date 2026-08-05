from num2words import num2words
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'

    is_check = fields.Boolean('Is Check', compute='_compute_is_check',
                              store=False)
    check_no = fields.Char('Check Number')
    amount_text = fields.Char('Amount in Text', compute='_compute_amount_text',
                              store=False)
    is_batch = fields.Boolean('Batch?', default=False)

    @api.constrains('check_no', 'journal_id')
    def _check_number_and_journal(self):
        """ constrains function to check check_no in batch """
        self.ensure_one()
        # check payment records
        domain = [
            ('journal_id', '=', self.journal_id.id),
            ('check_no', '=', self.check_no),
            ('check_no', '!=', False),
            ('batch_payment_id', '=', False),
        ]
        payment = self.env['account.payment'].search(domain)
        if payment:
            raise ValidationError('Check Number is already used!')

        # check self
        domain = [
            ('id', '!=', self.id),
            ('journal_id', '=', self.journal_id.id),
            ('check_no', '=', self.check_no),
            ('check_no', '!=', False),
        ]
        batch = self.env['account.batch.payment'].search(domain)
        if batch:
            raise ValidationError('Check Number is already used!')

    @api.depends('currency_id', 'amount')
    def _compute_amount_text(self):
        """ compute function to assign total in text """
        for rec in self:
            rec.amount_text = num2words(int(rec.amount), lang='id')

    @api.depends('payment_method_id')
    def _compute_is_check(self):
        """ compute function to check if payment method is check """
        for rec in self:
            pmt = rec.payment_method_id
            rec.is_check = pmt and pmt.code == 'check_printing'

    def _has_check_no(self):
        """ helper function to check if record has valid check_no already """
        # valid check_no is check connected to this record
        domain = [
            ('check_id.journal_id', '=', self.journal_id.id),
            ('batch_payment_id', '=', self.id),
        ]
        check = self.env['res.check.line'].search_count(domain)
        return check

    def button_check(self):
        """ function to check check_no existence and generate """
        # quit if record has check_no
        if self._has_check_no():
            return True

        # find unused check data with same journal
        domain = [
            ('check_id.journal_id', '=', self.journal_id.id),
            ('is_used', '=', False),
        ]
        check = self.env['res.check.line'].search(domain, limit=1, order='name')

        if check:
            self.check_no = check.name  # assign if found
            check.write({'batch_payment_id': self.id})  # then write to use
        else:  # check runs out of usable number, raise error
            raise ValidationError('There is no more usable Check Number')

        return True

    def _send_after_validation(self):
        """ inherit function to set check record and payment_ids """
        self.ensure_one()

        if self.check_no:
            if self.payment_ids:  # payments exist, set check to payment_ids
                # pass context to bypass the checking in payment record
                self.payment_ids.with_context({'bypass': True}).write({'check_no': self.check_no})
            # find check number with journal and update
            domain = [
                ('check_id.journal_id', '=', self.journal_id.id),
                ('name', '=', self.check_no),
            ]
            check = self.env['res.check.line'].search(domain)
            if check:  # insert the payment_id
                check.write({'batch_payment_id': self.id})

        res = super(AccountBatchPayment, self)._send_after_validation()
        return res
