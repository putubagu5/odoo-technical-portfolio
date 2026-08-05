from odoo import fields, models, api


class BankCashTransfer(models.Model):
    _inherit = 'bank.cash.transfer'

    cf_activity_id_sent = fields.Many2one('cashflow.activity', 'CF Activity Sent')
    cf_activity_id_receive = fields.Many2one('cashflow.activity', 'CF Activity Receive')

    # add payment fields
    check_master_id = fields.Many2one('res.check', 'Check Series',
                                      domain='[("journal_id", "=", bank_from)]')
    check_id = fields.Many2one(
        'res.check.line', 'Check No',
        domain='[("check_id", "=", check_master_id), ("is_used", "=", False), ("cancelled", "=", False)]')

    def action_create_transfer(self):
        res = super(BankCashTransfer, self).action_create_transfer()
        send_payment_method_id = self.env['account.payment.method'].search([
            ('payment_type', '=', 'inbound'), ('code', '=', 'manual')], limit=1)
        receive_payment_method_id = self.env['account.payment.method'].search([
            ('payment_type', '=', 'outbound'), ('code', '=', 'manual')], limit=1)
        vals_list = [
            # send transfer
            {
                'payment_type': 'outbound',
                'partner_id': self.partner_id.id or False,
                'destination_account_id': self.clearing_account_id.id,
                'cf_activity_id': self.cf_activity_id_sent.id or False,
                'is_internal_transfer': True,
                'company_id': self.company_id.id or self.env.company,
                'amount': self.amount or 0.0,
                'currency_id': self.currency_id.id,
                'manual_currency_rate_active': self.manual_currency_rate_active,
                'manual_currency_rate': self.manual_currency_rate,
                'date': self.date,
                'ref': self.note or False,
                'journal_id': self.bank_from.id,
                'operating_unit_id': self.operating_unit_id.id or False,
                'payment_method_id': send_payment_method_id.id or False,
                'partner_bank_id': self.partner_bank_from.id or False,
                'payment_doc_master_id': self.payment_doc_master_id.id or False,
                'payment_doc_id': self.payment_doc_id.id or False,
                'giro_master_id': self.giro_master_id.id or False,
                'giro_id': self.giro_id.id or False,
                'transfer_id': self.id,
                'check_master_id': self.check_master_id.id or False,
                'check_id': self.check_id.id or False,
            },
            # Receive transfer
            {
                'payment_type': 'inbound',
                'partner_id': self.partner_id.id or False,
                'destination_account_id': self.clearing_account_id.id,
                'cf_activity_id': self.cf_activity_id_sent.id or False,
                'is_internal_transfer': True,
                'company_id': self.company_id.id or self.env.company,
                'amount': self.receive_bank_to_amount or 0.0,
                'currency_id': self.bank_to_currency_id.id,
                'manual_currency_rate_active': self.manual_currency_rate_active,
                'manual_currency_rate': self.manual_currency_rate2,
                'date': self.date,
                'ref': self.note or False,
                'journal_id': self.bank_to.id,
                'operating_unit_id': self.operating_unit_id.id or False,
                'payment_method_id': receive_payment_method_id.id or False,
                'partner_bank_id': self.partner_bank_to.id or False,
                'payment_doc_master_id': self.payment_doc_master_id.id or False,
                'payment_doc_id': self.payment_doc_id.id or False,
                'giro_master_id': self.giro_master_id.id or False,
                'giro_id': self.giro_id.id or False,
                'transfer_id': self.id,
                'check_master_id': self.check_master_id.id or False,
                'check_id': self.check_id.id or False,
            },
        ]
        return res

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        for record in self:
            if record.transfer_ids:
                for rec in record.transfer_ids:
                    if rec.payment_type == 'outbound':
                        rec.write({'cf_activity_id': self.cf_activity_id_sent.id})
                    if rec.payment_type == 'inbound':
                        rec.write({'cf_activity_id': self.cf_activity_id_receive.id})

    def action_posted(self):
        """ inherit function to change document_ref in transfer_ids """
        # take doc_ref from the record and pass into transfer_ids
        for rec in self.transfer_ids:
            rec.write({'document_ref': self.doc_ref})
        res = super(BankCashTransfer, self).action_posted()
        return res
