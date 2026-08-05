from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import Warning


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        """ inherit function to change/add values"""
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)

        # add project_ids, pass to project_ids in PO Line
        res['project_ids'] = [(6, 0, item.line_id.project_ids.ids)]
        return res


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = {
            'product_id': return_line.product_id.id,
            'product_uom_qty': return_line.quantity,
            'product_uom': return_line.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date': fields.Datetime.now(),
            'location_id': return_line.move_id.location_dest_id.id,
            'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line.move_id.id,
            'procure_method': 'make_to_stock',
            'project_ids': [(6, 0, return_line.move_id.project_ids.ids)],
        }
        return vals
