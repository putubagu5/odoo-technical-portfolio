from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    balance_end_real = fields.Monetary(compute='_compute_ending_balance_real')
    total_debit_real = fields.Monetary(compute='_compute_total_debit_credit_real', string="Total Debit")
    total_credit_real = fields.Monetary(compute='_compute_total_debit_credit_real', string="Total Credit")
    
    partner_line_names = fields.Text('Partners', compute='_compute_name_in_lines',
                                     store=True)
    label_names = fields.Text('Labels', compute='_compute_name_in_lines',
                              store=True)
    multi_payment_reference = fields.Char('Payment References',
                                          compute='_compute_payment_references',
                                          store=True)

    @api.depends('line_ids')
    def _compute_payment_references(self):
        """ compute function to get multi_payment_reference """
        for rec in self:
            rec.multi_payment_reference = ', '.join(x.multi_payment_reference if x.multi_payment_reference else '' for x in rec.line_ids)

    @api.depends('balance_end')
    def _compute_ending_balance_real(self):
        """ compute function to bypass _compute_ending_balance """
        # to safely done this, the original function is not replaced
        for rec in self:
            rec.balance_end_real = rec.balance_end
    
    @api.depends('line_ids')
    def _compute_total_debit_credit_real(self):
        for rec in self:
            total_debit_real_amount = 0.0
            total_credit_real_amount = 0.0
            if rec.line_ids:
                if len(rec.line_ids) > 0:
                    for line in rec.line_ids:
                        if line.amount > 0 and not line.cancel_reversal:
                            total_debit_real_amount += line.amount
                        if line.amount < 0 and not line.cancel_reversal:
                            total_credit_real_amount += abs(line.amount)
            rec.total_debit_real = total_debit_real_amount
            rec.total_credit_real = total_credit_real_amount

    @api.depends('line_ids')
    def _compute_name_in_lines(self):
        """ compute function to get all names in lines """
        for rec in self:
            partners = '\n'.join(x.partner_id.name for x in rec.line_ids if x.partner_id)
            labels = '\n'.join(x.payment_ref for x in rec.line_ids if x.payment_ref)
            rec.partner_line_names = partners if rec.line_ids else ''
            rec.label_names = labels if rec.line_ids else ''

    def button_post_reconcile(self):
        if self.state == 'open':
            self.button_post()
        self.action_reconcile()
