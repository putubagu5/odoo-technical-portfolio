from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def _prepare_item(self, line):
        """ inherit function to add qty """
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_item(line)
        # res['product_qty'] = line.product_qty - line.purchased_qty
        res['episode_no'] = line.header_attribute4
        return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        """ inherit function to change/add values"""
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        res['episode_no'] = item.line_id.header_attribute4
        return res
