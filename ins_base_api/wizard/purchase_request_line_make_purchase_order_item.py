from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    episode_no = fields.Char(string="Episode No")
