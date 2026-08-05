from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    cf_activity_id = fields.Many2one('cashflow.activity', 'CF Activity')
    payment_doc_id = fields.Many2one(
        'res.payment.document.line', 'Document No')

    def _create_payment_vals_from_wizard(self):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals['cf_activity_id'] = self.cf_activity_id.id
        payment_vals['payment_doc_id'] = self.payment_doc_id.id
        return payment_vals
