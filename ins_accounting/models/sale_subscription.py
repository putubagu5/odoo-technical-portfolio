from odoo import api, fields, models
from odoo.addons.sale_subscription.models.sale_subscription import INTERVAL_FACTOR


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    deposit_invoice_id = fields.Many2one('account.move', 'Deposit Invoice')
    amount_total = fields.Float('Amount Total Subscription',
                                compute='_compute_amount_deposit', store=False)
    amount_actual_deposit = fields.Float('Amount Actual Deposit',
                                         compute='_compute_amount_deposit',
                                         store=False)
    amount_deposit = fields.Float('Amount Deposit',
                                  compute='_compute_amount_deposit', store=False)
    deposit_tax_ids = fields.Many2many('account.tax', string='Deposit Taxes',
                                       compute='_compute_amount_deposit',
                                       store=False)

    @api.depends('deposit_invoice_id', 'deposit_invoice_id.amount_total',
                 'template_id.recurring_interval',
                 'template_id.recurring_rule_type')
    def _compute_amount_deposit(self):
        """ compute function to find the amount of deposit prorated """
        for rec in self:
            # find total of deposit amount if any
            # take the amount_untaxed, this is the base to calculate prorate
            total = rec.deposit_invoice_id.amount_untaxed if rec.deposit_invoice_id else 0.0
            rec.amount_actual_deposit = total
            # then based on the INTERVAL_FACTOR, calculate the deposit
            tmpl = rec.template_id
            rec.amount_deposit = (
                total / (tmpl.recurring_rule_count if tmpl.recurring_rule_boundary == 'limited' else 1)
            ) if rec.template_id else 0
            rec.deposit_tax_ids = rec.deposit_invoice_id.invoice_line_ids.tax_ids
            rec.amount_total = rec.recurring_total * (
                tmpl.recurring_rule_count if tmpl.recurring_rule_boundary == 'limited' else 1
            ) if rec.template_id else 1

    def _prepare_invoice(self):
        """ inherit function to add deposit product in invoice line """
        res = super(SaleSubscription, self)._prepare_invoice()
        # if deposit is filled, find deposit product
        if self.deposit_invoice_id and self.amount_deposit:
            param_product_id = self.env['ir.config_parameter'].sudo().get_param(
                'sale.default_deposit_product_id')
            deposit_product = self.env['product.product'].browse(int(param_product_id))
            if deposit_product:
                # deposit found, construct data, and make amount negative
                data = {
                    'product_id': deposit_product.id,
                    'name': deposit_product.name,
                    'account_id': deposit_product._get_product_accounts()['income'],
                    'quantity': 1,
                    'tax_ids': [(4, x.id) for x in self.deposit_tax_ids],
                    'price_unit': -self.amount_deposit,
                }
                invoice_lines = res.get('invoice_line_ids')
                invoice_lines.append((0, 0, data))
        return res

    def start_subscription(self):
        """ inherit function to set subscription_id to deposit invoice """
        self.ensure_one()
        res = super(SaleSubscription, self).start_subscription()
        if self.deposit_invoice_id:
            self.deposit_invoice_id.subscription_id = self.id
        return res
