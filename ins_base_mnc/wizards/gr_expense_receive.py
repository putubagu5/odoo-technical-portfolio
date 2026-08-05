# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GRExpenseReceive(models.TransientModel):
    _name = 'gr.expense.receive'

    purchase_order_ids = fields.Many2many('purchase.order', 'gr_exp_po_rel', string="Purchase Order",
                                          domain="[('order_line.product_id.type', '=', 'service')]")
    line_ids = fields.One2many('gr.expense.receive.line', 'gr_expense_receive_id', string="Lines",
                               domain="[('product_id.type', '=', 'service')]")

    @api.onchange('purchase_order_ids')
    def _onchange_purchase_order(self):
        for gr in self:
            gr_lines = []
            for po in gr.purchase_order_ids:
                for line in po.order_line:
                    if line.product_id.type == 'service' and line.qty_received < line.product_qty:
                        gr_lines.append((0, False, {'po_line_id': line._origin.id, 'qty_received': line.qty_received}))

            gr.line_ids = [(5, False, False)]
            gr.line_ids = gr_lines

    def submit(self):
        self.ensure_one()
        for line in self.line_ids:
            line.po_line_id.qty_received = line.po_line_id.qty_received + line.qty_ready


class GRExpenseReceiveLine(models.TransientModel):
    _name = 'gr.expense.receive.line'

    gr_expense_receive_id = fields.Many2one('gr.expense.receive', string="GR Expense", required=True)
    po_line_id = fields.Many2one('purchase.order.line', string="PO Line", required=True)
    product_id = fields.Many2one('product.product', string="Product", related='po_line_id.product_id')
    product_qty = fields.Float(string="Demand", related='po_line_id.product_qty')
    qty_received = fields.Float(string="Received", related='po_line_id.qty_received')
    qty_ready = fields.Float(string="Ready")

    @api.constrains('qty_ready')
    def _constraint_qty_ready(self):
        for record in self:
            if record.qty_ready < 0:
                raise ValidationError(_("Quantity Ready can't be minus."))
