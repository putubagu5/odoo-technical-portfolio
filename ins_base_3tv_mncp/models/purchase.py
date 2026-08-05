from odoo import api, fields, models
from datetime import datetime, timedelta, date


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line.filtered(lambda x: x.state != 'cancel'):
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })


# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'

#     @api.depends('product_qty', 'price_unit', 'taxes_id')
#     def _compute_amount(self):
#         for line in self.filtered(lambda x: x.order_id.state in ['purchase', 'done']):
#             vals = line._prepare_compute_all_values()
#             taxes = line.taxes_id.compute_all(
#                 vals['price_unit'],
#                 vals['currency_id'],
#                 vals['product_qty'],
#                 vals['product'],
#                 vals['partner'])
#             line.update({
#                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                 'price_total': taxes['total_included'],
#                 'price_subtotal': taxes['total_excluded'],
#             })

#     def _prepare_compute_all_values(self):
#         # Hook method to returns the different argument values for the
#         # compute_all method, due to the fact that discounts mechanism
#         # is not implemented yet on the purchase orders.
#         # This method should disappear as soon as this feature is
#         # also introduced like in the sales module.
#         self.ensure_one()
#         return {
#             'price_unit': self.price_unit,
#             'currency_id': self.order_id.currency_id,
#             'product_qty': self.product_qty,
#             'product': self.product_id,
#             'partner': self.order_id.partner_id,
#         }
