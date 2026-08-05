# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PRMakePa(models.TransientModel):
    _name = 'purchase.request.line.make.purchase.agreement'

    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user.id)
    item_ids = fields.One2many('purchase.request.line.make.purchase.agreement.item', 'wiz_id', string="Items")

    @api.model
    def _check_valid_request_line(self, request_line_ids):
        company_id = False

        for line in self.env["purchase.request.line"].browse(request_line_ids):
            if line.request_id.state == "done":
                raise UserError(_("The purchase has already been completed."))
            if line.request_id.state != "approved":
                raise UserError(
                    _("Purchase Request %s is not approved") % line.request_id.name
                )

            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines from the same company."))
            else:
                company_id = line_company_id

    @api.model
    def _prepare_item(self, line):
        return {
            "line_id": line.id,
            "request_id": line.request_id.id,
            "product_id": line.product_id.id,
            "name": line.name or line.product_id.name,
            "product_qty": line.pending_qty_to_receive,
            "product_uom_id": line.product_uom_id.id,
        }

    @api.model
    def get_items(self, request_line_ids):
        request_line_obj = self.env["purchase.request.line"]
        items = []
        request_lines = request_line_obj.browse(request_line_ids)
        self._check_valid_request_line(request_line_ids)
        for line in request_lines:
            items.append([0, 0, self._prepare_item(line)])
        return items

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        request_line_ids = []
        if active_model == "purchase.request.line":
            request_line_ids += self.env.context.get("active_ids", [])
        elif active_model == "purchase.request":
            request_ids = self.env.context.get("active_ids", False)
            request_line_ids += (
                self.env[active_model].browse(request_ids).mapped("line_ids.id")
            )
        if not request_line_ids:
            return res
        res["item_ids"] = self.get_items(request_line_ids)
        return res

    def _prepare_purchase_agreement(self, purchase_agreement_lines, origin):
        type_id = self.env['purchase.requisition.type'].search([], limit=1)
        if not type_id:
            raise UserError(_("Agreement Type not found."))

        purchase_agreement_values = {
            'company_id': self.env.company.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'state': 'draft',
            'type_id': type_id.id,
            'origin': origin,
            'line_ids': purchase_agreement_lines,
        }
        return purchase_agreement_values

    def _prepare_purchase_agreement_lines(self):
        line_ids = []
        for line in self.item_ids:
            line_ids.append((0, False, {
                'product_id': line.product_id.id,
                'product_description_variants': line.name,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
            }))

        return line_ids

    def make_purchase_agreement(self):
        purchase_agreement_obj = self.env['purchase.requisition']
        origin = self.item_ids[0].request_id.name
        pr_obj = self.env["purchase.request"].search(
                [('name', '=', origin)])
        line_ids = self._prepare_purchase_agreement_lines()
        purchase_agreement_values = self._prepare_purchase_agreement(line_ids, origin)

        purchase_agreement_id = purchase_agreement_obj.create(purchase_agreement_values)
        pr_obj.write({'rfq_is_created': True})
        return {
            "name": _("Purchase Agreement"),
            "view_mode": "form",
            "res_model": "purchase.requisition",
            "res_id": purchase_agreement_id.id,
            "type": "ir.actions.act_window",
        }


class PurchaseRequestLineMakePurchaseAgreementItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.agreement.item"
    _description = "Purchase Request Line Make Purchase Agreement Item"

    wiz_id = fields.Many2one('purchase.request.line.make.purchase.agreement', string="Wizard", required=True,
                             ondelete="cascade", readonly=True)
    line_id = fields.Many2one('purchase.request.line', string="Purchase Request Line")
    request_id = fields.Many2one('purchase.request', related="line_id.request_id", string="Purchase Request")
    product_id = fields.Many2one('product.product', string="Product", related="line_id.product_id")
    name = fields.Text(string="Description", related="line_id.name")
    product_qty = fields.Float(string="Quantity", digits="Product Unit of Measure", related="line_id.product_qty")
    product_uom_id = fields.Many2one('uom.uom', string="UoM", related="line_id.product_uom_id")
