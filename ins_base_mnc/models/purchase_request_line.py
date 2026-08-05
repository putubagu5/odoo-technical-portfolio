from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'
    _order = 'line_number asc, id desc'

    # NOTE: make estimated_cost to computed and stored
    estimated_cost = fields.Monetary(compute='_compute_estimated_cost', store=True)
    date_needed = fields.Date('Needed Date')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    buyer_id = fields.Many2one('res.buyer', 'Buyer', check_company=True)
    date_rate = fields.Date('Date', compute='_compute_actual_rate', store=True)
    actual_rate = fields.Float('BI Rate', compute='_compute_actual_rate', store=True)
    line_number = fields.Integer('PR Line')
    product_qty = fields.Float(
        string="Qty", tracking=True, digits="Product Unit of Measure"
    )
    original_price = fields.Float(string='Unit Price')
    is_cost_progress = fields.Boolean('Is CIP', related='product_id.is_cost_progress')
    asset_cost_progress_id = fields.Many2one('cip.configuration', 'CIP', related="cip_id")
    attachment_line_ids = fields.Many2many(
        related='request_id.attachment_form_ids', string="Attachment")
    employee_id = fields.Many2one('hr.employee', 'Employee')
    wilayah_id = fields.Many2one(
        'operating.unit', string="Wilayah",
        store='True'
    )

    def copy(self, default=None):
        """ inherit function to check request_state """
        default = dict(default or {})
        self.ensure_one()
        if self.request_state != 'draft':
            raise ValidationError('Cannot duplicate except draft')
        return super(PurchaseRequestLine, self).copy(default)

    @api.depends('product_qty', 'original_price', 'select_currency_id', 'manual_currency_rate_active')
    def _compute_estimated_cost(self):
        """ compute function to get estimated_cost """
        # estimated_cost = original_price * rate * product_qty
        cmp_currency = self.env.user.company_id.currency_id
        for rec in self:
            if rec.manual_currency_rate_active:
                rec.estimated_cost = (rec.manual_currency_rate * rec.original_price) * rec.product_qty
            else:
                s_currency = rec.select_currency_id
                price = s_currency.compute(rec.original_price, cmp_currency)
                rec.estimated_cost = price * rec.product_qty

    @api.depends('date_start', 'select_currency_id', 'company_id')
    def _compute_actual_rate(self):
        """ compute function to get date of rate and amount of BI Rate """
        for rec in self:
            # based on the select_currency_id and company, find rates earlier
            # than Creation Date
            sql = """
                SELECT name AS date, actual_rate AS rate
                FROM res_currency_rate
                WHERE company_id = %s AND currency_id = %s AND name <= '%s'
                ORDER BY name DESC LIMIT 1
            """ % (rec.company_id.id, rec.select_currency_id.id, rec.date_start)
            self.env.cr.execute(sql)
            currency = self.env.cr.dictfetchone()
            rec.date_rate = currency.get('date', False) if currency else False
            rec.actual_rate = currency.get('rate', 1) if currency else 1

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ inherit onchange function to add variants info """
        super(PurchaseRequestLine, self).onchange_product_id()
        if self.product_id and self.company_id and self.product_id.buyer_ids:
            buyer = self.product_id.buyer_ids.filtered(lambda x: x.company_id == self.company_id)
            self.buyer_id = buyer[-1].id if buyer else False
        if self.product_id and self.product_id.product_template_attribute_value_ids:
            variant = ''
            # name_var = "[{}] {}".format(self.product_id.name, self.product_id.code)
            for line in self.product_id.product_template_attribute_value_ids:
                # variant += (' - ' + str(line.attribute_id.name) + ' : ' + line.name + ';\n')
                variant = line.name
            self.name = variant or ''
            # self.name = variant and "%s :\n%s" % (name_var, variant) or name_var
            self.original_price = self.product_id.standard_price

    @api.depends('request_id', 'purchase_lines', 'is_returned', 'is_rejected')
    def _compute_line_state(self):
        """ override compute function to set request_state """
        for rec in self:
            temp_line_state = False
            if rec.request_id.state == 'draft':
                temp_line_state = 'draft'
            if rec.request_id.state in ['to_approve']:
                temp_line_state = 'to_approve'
            if rec.request_id.state in ['approved']:
                temp_line_state = 'approved'
            if rec.request_id.state == 'rejected' or rec.is_rejected:
                temp_line_state = 'rejected'
            if rec.purchase_lines:
                fullfilled_qty = 0.0
                for po_line in rec.purchase_lines.filtered(lambda x: x.order_id.state == 'done'):
                    fullfilled_qty += po_line.product_qty

                is_fullfilled = True if fullfilled_qty >= rec.product_qty else False
                if is_fullfilled:
                    temp_line_state = 'done'
                else:  # NOTE: if qty done is not same, assume approved
                    temp_line_state = 'approved'
            if rec.is_returned and rec.request_id.state in ['draft', 'returned']:
                temp_line_state = 'returned'
            if rec.request_id.state == 'closed' and rec.request_state != 'done':
                temp_line_state = 'closed'
            if rec.request_state == 'cancel':
                temp_line_state = 'cancel'

            # NOTE: add one last thing, if all purchase_lines state is cancel
            # then force the status of request_state to approved
            # if rec.purchase_lines and rec.outstanding_purchase_qty == 0:
            qty_remaining = rec.pending_qty_to_receive - rec.qty_in_progress
            if rec.purchase_lines and qty_remaining == 0:
                temp_line_state = 'done'
                if all(po_line.state == "cancel" for po_line in rec.purchase_lines):
                    temp_line_state = 'approved'

            # another case might happen, if the total purchase_lines with state
            # is not cancel exceeds estimated_cost, it is considered as done
            if rec.purchase_lines:
                valid_lines = rec.purchase_lines.filtered(lambda x: x.state != 'cancel')
                amount_lines = sum(valid_lines.mapped('price_subtotal'))
                if amount_lines > rec.estimated_cost:
                    temp_line_state = 'done'

            rec.request_state = temp_line_state

    # @api.onchange("product_id")
    # def onchange_product_id(self):
    #     if self.product_id:
    #         name = self.product_id.name + "test"
    #         if self.product_id.code:
    #             name = "[{}] {}".format(name, self.product_id.code)
    #         if self.product_id.description_purchase:
    #             name += "\n" + self.product_id.description_purchase
    #         self.product_uom_id = self.product_id.uom_id.id
    #         self.product_qty = 1
    #         self.name = name
    # @api.onchange('original_price')
    # def convert_currency(self):
    #     """ override onchange function to do nothing """
    #     return
