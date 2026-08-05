# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class GRMatchingWizard(models.TransientModel):
    _name = 'gr.matching.wizard'

    bill_id = fields.Many2one('account.move', string="Bill", required=True, ondelete='CASCADE')
    currency_id = fields.Many2one(related='bill_id.currency_id')
    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)
    purchase_order_ids = fields.Many2many('purchase.order', 'po_gr_match_rel', string="Purchase Order")
    picking_ids = fields.Many2many('stock.picking', 'picking_gr_match_rel', string="Goods Receipt",
                                   context={'is_return': True})
    total = fields.Monetary(string="Total", compute='_compute_total', store=True)
    stock_move_line_ids = fields.One2many('gr.matching.wizard.stock.move', 'gr_matching_id', string="Operations")
    select_all = fields.Boolean('Select All', default=False)

    @api.onchange('select_all')
    def _onchange_select_all(self):
        """ onchange function to select all lines """
        for rec in self:
            rec.stock_move_line_ids.write({'select': rec.select_all})

    @api.onchange('purchase_order_ids')
    def _onchange_purchase_order_ids(self):
        """ onchange function to set picking_ids based on every pickings in purchase_order_ids """
        for rec in self:
            if rec.purchase_order_ids:
                pickings = rec.purchase_order_ids.mapped('picking_ids')
                rec.picking_ids = pickings.filtered(lambda x: x.picking_type_code == 'incoming' and x.state == 'done' and 'Return of' not in x.origin and x.is_returned is False)

    @api.onchange('purchase_order_ids', 'picking_ids')
    def _onchange_picking_set_lines(self):
        for record in self:
            new_lines = []

            for po in record.purchase_order_ids:
                for order_line in po.order_line.filtered(lambda ol: ol.product_id.type == 'service' and not ol.is_gr_matched):
                    purchase_order_line_id = self.env['purchase.order.line'].browse(order_line._origin.id)

                    # Compute billed quantity
                    aml_pol_ids = self.env['account.move.line'].search([
                        ('move_id.cancel_reversal', '!=', True),
                        ('po_line_gr_match_ids', 'in', [order_line._origin.id])
                    ])

                    quantity_billed = sum([aml_pol.quantity for aml_pol in aml_pol_ids])
                    # amount_billed = sum([aml_pol.price_subtotal for aml_pol in aml_pol_ids])
                    amount_billed = purchase_order_line_id.price_unit * quantity_billed
                    quantity_to_billed = purchase_order_line_id.qty_received - quantity_billed
                    price_subtotal = purchase_order_line_id.price_unit * quantity_to_billed

                    po_line_values = {
                        'purchase_order_line_id': order_line._origin.id,
                        'product_id': purchase_order_line_id.product_id.id,
                        'description_picking': purchase_order_line_id.name,
                        'price_unit': purchase_order_line_id.price_unit,
                        'price_subtotal': price_subtotal,
                        'amount_billed': amount_billed,
                        'amount_remaining': price_subtotal,
                        'product_uom_qty': purchase_order_line_id.product_qty,
                        'quantity_done': purchase_order_line_id.qty_received,
                        'quantity_billed': quantity_billed,
                        'quantity_to_billed': quantity_to_billed,
                    }
                    new_line = (0, False, po_line_values)
                    new_lines.append(new_line)

            for picking in record.picking_ids:
                for picking_line in picking.move_ids_without_package.filtered(lambda pl: pl.is_gr_matched is False):
                    stock_move_id = self.env['stock.move'].browse(picking_line._origin.id)

                    # Compute billed quantity
                    aml_sm_ids = self.env['account.move.line'].search([
                        ('move_id.cancel_reversal', '!=', True),
                        ('stock_move_gr_match_ids', 'in', [stock_move_id._origin.id])
                    ])

                    quantity_billed = sum([aml_sm.quantity for aml_sm in aml_sm_ids])
                    amount_billed = sum([aml_sm.price_subtotal for aml_sm in aml_sm_ids])
                    quantity_to_billed = stock_move_id.quantity_done - quantity_billed
                    price_subtotal = 0.0
                    if stock_move_id.purchase_line_id:
                        price_subtotal = stock_move_id.purchase_line_id.price_unit * quantity_to_billed

                    picking_line_values = {
                        'stock_move_id': picking_line._origin.id,
                        'product_id': stock_move_id.product_id.id,
                        'description_picking': stock_move_id.description_picking,
                        'price_unit': stock_move_id.purchase_line_id.price_unit if stock_move_id.purchase_line_id else 0.0,
                        'price_subtotal': price_subtotal,
                        'amount_billed': amount_billed,
                        'amount_remaining': price_subtotal,
                        'product_uom_qty': stock_move_id.product_uom_qty,
                        # 'quantity_done': stock_move_id.quantity_done - stock_move_id.quantity_return,
                        'quantity_done': stock_move_id.quantity_done,
                        'quantity_billed': quantity_billed,
                        'quantity_to_billed': quantity_to_billed - stock_move_id.quantity_return,
                    }
                    new_line = (0, False, picking_line_values)
                    new_lines.append(new_line)

            record.stock_move_line_ids = [(5, False, False)]
            record.stock_move_line_ids = new_lines

    @api.depends(
        'stock_move_line_ids', 'stock_move_line_ids.select',
        'stock_move_line_ids.price_unit',
        'stock_move_line_ids.quantity_to_billed')
    def _compute_total(self):
        for rec in self:
            total = 0.0
            moves = rec.stock_move_line_ids.filtered(lambda sm: sm.select)
            for line in moves:
                total += (line.price_unit * line.quantity_to_billed)
            rec.update({'total': total})

    def submit(self):
        self.ensure_one()
        gr_product_type = ['consu', 'product']
        bill_id = self.env['account.move'].browse(self.bill_id._origin.id)

        for service_move in self.stock_move_line_ids.filtered(lambda sm: sm.select and sm.product_id.type == 'service'):
            # qty_to_billed = service_move.quantity_done - service_move.quantity_billed
            # if service_move.quantity_to_billed > qty_to_billed:
            #     raise UserError("The quantity to be billed is greater than the remaining quantity to be billed.")
            if service_move.price_subtotal > service_move.amount_remaining:
                raise UserError("The amount to be billed is greater than the remaining amount.")
            else:
                purchase_order_line_id = self.env['purchase.order.line'].browse(
                    service_move.purchase_order_line_id._origin.id)
                bill_id.set_account_move_line_from_po(purchase_order_line_id, service_move)

        for picking_move in self.stock_move_line_ids.filtered(
                lambda sm: sm.select and sm.product_id.type in gr_product_type):
            # qty_to_billed = picking_move.quantity_done - picking_move.quantity_billed
            # if picking_move.quantity_to_billed > qty_to_billed:
            #     raise UserError("The quantity to be billed is greater than the remaining quantity to be billed.")
            if picking_move.price_subtotal > picking_move.amount_remaining:
                raise UserError("The amount to be billed is greater than the remaining amount.")
            else:
                stock_move_id = self.env['stock.move'].browse(picking_move.stock_move_id._origin.id)
                bill_id.set_account_move_line_from_gr_line(stock_move_id, picking_move)

        return True


class GRMatchingWizardStockMove(models.TransientModel):
    _name = 'gr.matching.wizard.stock.move'

    gr_matching_id = fields.Many2one('gr.matching.wizard', string="GR Matching", required=True, ondelete='CASCADE')
    purchase_order_line_id = fields.Many2one('purchase.order.line', string="Purchase Order Line", ondelete='CASCADE')
    stock_move_id = fields.Many2one('stock.move', string="Operation", ondelete='CASCADE')
    product_id = fields.Many2one('product.product', string="Product")
    description_picking = fields.Text(string="Description")
    price_unit = fields.Monetary(string="Unit Price")
    price_subtotal = fields.Monetary(string="Subtotal")
    amount_billed = fields.Monetary(string="Amount Billed")
    amount_remaining = fields.Monetary(string="Amount Remaining")
    product_uom_qty = fields.Float(string="Demand")
    quantity_done = fields.Float(string="Done", digits='gr.matching.decimal.precision')
    quantity_billed = fields.Float(string="Billed", digits='gr.matching.decimal.precision')
    quantity_to_billed = fields.Float(string="To Billed", digits='gr.matching.decimal.precision')
    select = fields.Boolean(string="Select", default=False)
    currency_id = fields.Many2one('res.currency', string="Currency", related='gr_matching_id.currency_id')

    @api.onchange('price_subtotal')
    def _onchange_compute_quantity_to_billed(self):
        for rec in self:
            if rec.price_subtotal > 0.0:
                quantity_to_billed = rec.price_subtotal / rec.price_unit
                rec.quantity_to_billed = quantity_to_billed

    # @api.onchange('select')
    # def _onchange_select(self):
    #     for rec in self:
    #         if rec.select is True:
    #             rec.quantity_to_billed = rec.quantity_done - rec.quantity_billed

    @api.onchange('quantity_to_billed')
    def _onchange_compute_price_subtotal(self):
        for rec in self:
            if rec.quantity_to_billed > 0.0:
                price_subtotal = rec.quantity_to_billed * rec.price_unit
                rec.price_subtotal = price_subtotal

    @api.constrains('quantity_to_billed')
    def _constraint_quantity_to_billed(self):
        for record in self:
            if record.select:
                if record.quantity_to_billed <= 0.0:
                    raise UserError("The quantity to be billed is 0.")
