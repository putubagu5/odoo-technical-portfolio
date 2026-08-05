# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GRConsumable(models.TransientModel):
    _name = 'gr.consumable.receive'

    purchase_order_ids = fields.Many2many('purchase.order', 'gr_consu_po_rel', string="Purchase Order",
                                          domain="[('order_line.product_id.type', '=', 'consu'), ('state', '=', 'purchase')]")
    line_ids = fields.One2many('gr.consumable.receive.line', 'gr_consu_receive_id', string="Lines",
                               domain="[('product_id.type', '=', 'consu')]")

    @api.onchange('purchase_order_ids')
    def _onchange_purchase_order(self):
        for gr in self:
            gr_lines = []
            for po in gr.purchase_order_ids:
                for line in po.order_line:
                    if line.product_id.type == 'consu' and line.qty_received < line.product_qty:
                        gr_lines.append((0, False, {'po_line_id': line._origin.id, 'qty_received': line.qty_received}))

            gr.line_ids = [(5, False, False)]
            gr.line_ids = gr_lines

    def submit(self):
        self.ensure_one()
        for line in self.line_ids:
            gr_id = line.po_line_id.order_id.picking_ids.filtered(lambda sp: sp.state == 'assigned')
            if not gr_id:
                raise ValidationError(_("There is no Goods Receipt to update with product {}.".format(
                    line.product_id.name
                )))
            gr_id = gr_id[0]
            gr_line_to_update = gr_id.move_ids_without_package.filtered(
                lambda mv: mv.product_id.id == line.product_id.id)
            if not gr_line_to_update:
                raise ValidationError(_("There is no Stock Move to update with product {}.".format(
                    line.product_id.name
                )))
            gr_line_to_update_id = gr_line_to_update[0]
            gr_line_to_update_id.quantity_done = gr_line_to_update_id.quantity_done + line.qty_ready

            # Check if all demand in GR all done
            is_all_demand_done = all([True if gr_line.quantity_done >= gr_line.product_qty else False for gr_line in gr_id.move_ids_without_package])
            if is_all_demand_done:
                gr_id.button_validate()
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking',
                    'res_id': gr_id.id,
                    'target': 'main'
                }


class GRExpenseReceiveLine(models.TransientModel):
    _name = 'gr.consumable.receive.line'

    gr_consu_receive_id = fields.Many2one('gr.consumable.receive', string="GR Consumable", required=True)
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
