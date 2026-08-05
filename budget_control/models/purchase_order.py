# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from dateutil.relativedelta import relativedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_approve(self, force=False):
        result = super(PurchaseOrder, self).button_approve()

        for line in self.order_line:
            if line.product_id.type == 'service':
                line.qty_received = line.product_qty

        return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        # NOTE: this method is overriden to include Analytic Account from PO to Receipt
        self.ensure_one()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        # description_picking = product._get_description(self.order_id.picking_type_id)
        description_picking = self.name if self.name else product.description_pickingin
        if self.product_description_variants:
            description_picking += "\n" + self.product_description_variants
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'analytic_account_id': self.account_analytic_id.id if self.account_analytic_id else False,
        }
