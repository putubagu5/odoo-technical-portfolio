# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, Warning


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    pr_numbers = fields.Char(string="PR Numbers", compute='_compute_pr_numbers')
    exclude_attachment = fields.Boolean('Exclude Attachment', default=False)

    @api.model
    def default_get(self, fields):
        """ inherit function to add access for SUPERUSER_ID """
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self).default_get(fields)
        return res

    @api.depends('item_ids')
    def _compute_pr_numbers(self):
        self = self.with_user(SUPERUSER_ID)
        for record in self:
            pr_number_list = []
            for line in record.item_ids:
                pr_number_list.append(line.request_id.name if line.request_id else '')

            pr_number_list = list(set(pr_number_list))
            pr_number_list.sort()
            pr_numbers = ', '.join(pr_number_list)
            record.pr_numbers = pr_numbers

    @api.model
    def _prepare_item(self, line):
        """ inherit function to add qty """
        # replace product_qty with product_qty - purchased_qty in line
        # NOTE: we want to take only the purchased_lines with state not in ('cancel',)
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_item(line)
        purchased_lines = line.purchase_lines.filtered(lambda x: x.product_id == line.product_id and x.order_id.state not in ('cancel',))
        amt_purchased = sum(purchased_lines.mapped('price_subtotal')) if purchased_lines else 0
        # res['product_qty'] = line.product_qty - line.purchased_qty
        res['product_qty'] = line.pending_qty_to_receive - line.qty_in_progress
        res['qty_remaining'] = line.pending_qty_to_receive - line.qty_in_progress
        res['amount_total'] = line.estimated_cost - amt_purchased
        return res

    @api.model
    def _check_valid_request_line(self, request_line_ids):
        """ inherit function to check currency """
        self = self.with_user(SUPERUSER_ID)
        super(PurchaseRequestLineMakePurchaseOrder, self)._check_valid_request_line(request_line_ids)
        request_line = self.env['purchase.request.line'].browse(request_line_ids)
        # get all currencies from line, make to set, check if len != 1
        currs = set(x.select_currency_id.id for x in request_line)
        if len(currs) != 1:
            raise ValidationError('Cannot create RFQ from different currencies')

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        """ inherit function to add buyer_id """
        # get active purchase request line record and assign buyer_id
        self = self.with_user(SUPERUSER_ID)
        active_id = self._context.get('active_id', False)
        request = self.env['purchase.request.line'].browse(active_id)

        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(
            picking_type, group_id, company, origin)
        res['buyer_id'] = request.buyer_id.id if request.buyer_id else False

        # update origin
        res['origin'] = self.pr_numbers

        # blasphemy. check the user if it is super, replace with the context
        if self.env.user.id == SUPERUSER_ID:
            res['request_user_id'] = self._context.get('user', SUPERUSER_ID)

        return res

    @api.model
    def _get_purchase_line_onchange_fields(self):
        return ["product_uom", "name", "taxes_id"]

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        """ inherit function to change/add values"""
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        # add request_id
        res['request_id'] = item.line_id.request_id.id

        # add account
        res['account_id'] = item.line_id.account_id.id

        # add asset_cost_progress_id
        res['asset_cost_progress_id'] = item.line_id.asset_cost_progress_id.id

        # add price_unit based on original_price
        # res['rfq_price'] = item.line_id.original_price
        res['rfq_price'] = item.line_id.original_price
        res['price_unit'] = item.line_id.original_price

        # add product_qty based on wizard product_qty
        res['product_qty'] = item.product_qty

        # add amount_from_pr
        res['amount_from_pr_line'] = item.amount_total

        # add line_number, pass to request_line_number in PO Line
        res['request_line_number'] = item.line_id.line_number

        # NOTE: if exclude_attachment is checked, then prevent attachment in PO
        # add attachment_line_ids, pass to attachment_line_ids in PO Line
        if not self.exclude_attachment:
            res['attachment_line_ids'] = [(6, 0, item.line_id.attachment_line_ids.ids)]
        return res

    def _check_line_qty(self):
        """ helper function to check line qty """
        # active_ids = self._context.get('active_ids', [])
        # request_lines = self.env['purchase.request.line'].browse(active_ids)
        self = self.with_user(SUPERUSER_ID)
        for item in self.item_ids:
            if item.product_qty > item.qty_remaining:
                raise Warning('Please check qty. Cannot generate PO because it is more than remaining qty')
        # if any([x for x in self.item_ids if x.product_qty > x.qty_remaining]):
        #     raise Warning('Please check qty. Cannot generate PO because it is more than remaining qty')
        if any([x for x in self.item_ids if x.product_qty == 0]):
            raise ValidationError('Please check qty. Cannot generate PO because it is fully created')

    def _check_amount(self):
        """ helper function to check total amount """
        # NOTE: rule for this process is:
        # sum of purchase_lines.mapped('price_subtotal') as amount_purchase_lines
        # sum of item_ids.mapped('amount_total') as amount_lines
        # amount_lines + amount_purchase_lines
        # must be less than or equal to estimated cost
        self = self.with_user(SUPERUSER_ID)
        active_ids = self._context.get('active_ids', [])
        request_lines = self.env['purchase.request.line'].browse(active_ids)

        # we must check one by one
        for line in request_lines.with_user(SUPERUSER_ID):
            estimated_cost = line.estimated_cost
            valid_purchase_lines = line.purchase_lines.filtered(lambda x: x.state != 'cancel')
            amount_purchase_lines = sum(valid_purchase_lines.mapped('price_subtotal'))
            amount_lines = sum(self.item_ids.filtered(lambda x: x.line_id == line).mapped('amount_total'))

            if estimated_cost < amount_purchase_lines + amount_lines:
                product = line.product_id.display_name
                request = line.request_id.name
                msg = f'Purchase Order amount exceeds Estimated Cost! (Product: {product} in {request})'
                raise ValidationError(msg)

        # active_id = self._context.get('active_id', False)
        # request_line = self.env['purchase.request.line'].browse(active_id)
        # estimated_cost = request_line.estimated_cost
        # valid_purchase_lines = request_line.purchase_lines.filtered(lambda x: x.state != 'cancel')
        # amount_purchase_lines = sum(valid_purchase_lines.mapped('price_subtotal'))
        # amount_lines = sum(self.item_ids.mapped('amount_total'))

        # # careful the actual tolerance is from estimated cost
        # amount_tolerance = request_line.product_id.price_tolerance * estimated_cost / 100
        # if estimated_cost + amount_tolerance < amount_purchase_lines + amount_lines:
        #     str_amount_tolerance = '{:,.2f}'.format(amount_tolerance)
        #     msg = f'Purchase Order amount exceeds Estimated Cost! (max tolerance {str_amount_tolerance})'
        #     raise ValidationError(msg)

    def _check_currency(self):
        """ helper function to check same currency """

        self = self.with_user(SUPERUSER_ID)
        active_ids = self._context.get('active_ids', [])
        request_lines = self.env['purchase.request.line'].browse(active_ids)

        for line in request_lines.with_user(SUPERUSER_ID):
            if self.purchase_order_id and line.request_id.currency_id != self.purchase_order_id.currency_id:
                raise UserError(
                    _(
                        "Can't assign PR to PO with difference Currency "
                    )
                )

    def make_purchase_order(self):
        """ inherit function to add checking """
        # check first if any line contains less qty < 1
        # self = self.with_user(SUPERUSER_ID)
        self._check_line_qty()
        self._check_amount()
        self._check_currency()
        context = {'prevent_checking': True}  # add to prevent constrains function from triggering
        res = super(PurchaseRequestLineMakePurchaseOrder, self.with_context(context)).make_purchase_order()
        res['context'] = context
        return res

    @api.model
    def _get_order_line_search_domain(self, order, item):
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._get_order_line_search_domain(order, item)
        return res

    def create_allocation(self, po_line, pr_line, new_qty, alloc_uom):
        self = self.with_user(SUPERUSER_ID)
        res = super(PurchaseRequestLineMakePurchaseOrder, self).create_allocation(
            po_line, pr_line, new_qty, alloc_uom)
        return res


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    keep_description = fields.Boolean(default=True)

    amount_total = fields.Float('Amount')
    qty_remaining = fields.Float('Qty Remaining', digits="Product Unit of Measure")

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        line = self.line_id
        price_each = line.estimated_cost / line.product_qty
        self.product_qty = self.amount_total / price_each

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        """ onchange function to check the product_qty """
        self.ensure_one()

        # product_qty <= than product_qty - purchased_qty in line_id
        line = self.line_id
        # if self.product_qty > line.product_qty - line.purchased_qty or self.product_qty < 0:
        #     # force value to be exactly outstanding_purchase_qty
        #     return {
        #         'value': {
        #             'product_qty': line.product_qty - line.purchased_qty,
        #         }
        #     }
        price_each = line.estimated_cost / line.product_qty
        self.amount_total = price_each * self.product_qty
