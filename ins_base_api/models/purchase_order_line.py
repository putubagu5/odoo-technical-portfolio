from odoo import api, fields, models


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    episode_no = fields.Char('Episode No')
