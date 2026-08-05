from odoo import api, fields, models, SUPERUSER_ID


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    project_ids = fields.One2many(
        comodel_name="project.pr.line",
        inverse_name="po_line_id",
        string="Project Details",
    )

    def _prepare_account_move_line(self, move=False):
        """ inherit function to add project_ids and move project_ids"""
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        # add project_ids, pass to project_ids in account move Line
        res['project_ids'] = [(6, 0, self.project_ids.ids)]
        return res

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        """ inherit function to assign purchase_line_number to stock move """
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom)
        # add project_ids, pass to project_ids in move Line
        res['project_ids'] = [(6, 0, self.project_ids.ids)]
        return res
