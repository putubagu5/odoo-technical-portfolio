from odoo import _, fields, models, api


class PurchaseRequisitionMNC(models.Model):
    _inherit = 'purchase.requisition.line'

    subtotal_price = fields.Float(compute="calculate_subtotal_price", store=True)

    @api.depends('product_qty', 'price_unit')
    def calculate_subtotal_price(self):
        for rec in self:
            rec.subtotal_price = rec.product_qty * rec.price_unit
