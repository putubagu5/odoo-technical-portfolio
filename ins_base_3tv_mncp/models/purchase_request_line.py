from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.depends(
        "product_id",
        "name",
        "product_uom_id",
        "product_qty",
        "analytic_account_id",
        "date_required",
        "specifications",
        "purchase_lines",
        "request_state",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_state in ("approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False
