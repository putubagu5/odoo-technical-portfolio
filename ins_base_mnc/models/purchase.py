import logging
from num2words import num2words
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError, RedirectWarning, Warning
from odoo.osv import expression


_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_id = fields.Many2one(domain='["|", ("company_id", "=", False), ("company_id", "=", company_id), ("is_blacklist", "=", False), ("supplier_rank", ">", 0)]')
    quotation_number = fields.Char('Quotation number', required=True, index=True, copy=False, default='New')
    site_id = fields.Many2one('vendor.site', 'Vendor Site')  # NOTE: deprecated
    sites_id = fields.Many2one('res.sites', 'Vendor Site')
    po_description = fields.Text('Description', copy=True)
    amount_in_words = fields.Char('Amount To Words', compute='amount_to_text')
    amount_in_words_2 = fields.Char('Amount To Words 2', compute='amount_to_text_2')
    is_shipped_new = fields.Boolean('Validated/Received')
    buyer_id = fields.Many2one('res.buyer', 'Buyer')
    assignee_id = fields.Many2one('res.assignee.po', 'Assignee')
    is_fully_matched = fields.Boolean(string="Is GR Matched?", default=False,
                                      compute='_compute_fully_matched', store=True)
    is_service_po = fields.Boolean(string="Is Service PO?", store=False)
    actual_rate = fields.Float('BI Rate', default=1)
    delivery_address_1 = fields.Char('Delivery Address 1')
    delivery_address_2 = fields.Char('Delivery Address 2')
    delivery_address_3 = fields.Char('Delivery Address 3')
    requestor = fields.Char(string="Requestor", compute='_compute_requestor_names', inverse='_edit_requestor', store=True)
    requestor_comp = fields.Char(string="Requestor", compute='_compute_requestor', inverse='_edit_requestor', store=True)
    revision = fields.Integer('Revision', readonly=True, default=0)
    term_of_payment = fields.Text('Term of Payment')
    delivery_term = fields.Char('Delivery Term')
    pr_numbers = fields.Char(string="PR Numbers", compute='_compute_pr_numbers')
    rr_numbers = fields.Text(string="RR Numbers", compute='_compute_rr_numbers')
    other_name = fields.Char(string='Other Name')
    old_value = fields.Monetary('Old')
    new_value = fields.Monetary('New', compute='_compute_amount_untaxed_field')
    create_date = fields.Datetime(string='Created On')
    date_order = fields.Datetime(
        'Order Date', required=True, index=True, copy=False,
        default=fields.Datetime.now,
        help="Depicts the date within which the Quotation should be confirmed and converted into a purchase order.")
    prepayment_move_ids = fields.One2many('account.move', 'prepayment_po_ref_id', 'Prepayment Moves')
    show_prepayment = fields.Boolean('Show Prepayment', compute='_compute_show_prepayment', store=True)
    invoice_address_po = fields.Text('Invoice Address')
    rejected = fields.Boolean('Record Rejected', default=False,
                              help='To show that record is Rejected. For Real')

    @api.depends('prepayment_move_ids', 'amount_untaxed')
    def _compute_show_prepayment(self):
        """  """
        self = self.with_user(SUPERUSER_ID)
        for rec in self:
            rec.show_prepayment = rec.amount_untaxed != sum(rec.prepayment_move_ids.mapped('amount_untaxed'))

    @api.constrains('partner_ref')
    def _check_partner_ref(self):
        """ constrains function to check unique partner_ref """
        for rec in self:
            if rec.partner_ref:
                domain = [
                    ('id', '!=', rec.id),
                    ('partner_ref', '=ilike', rec.partner_ref),
                ]
                found = rec.search(domain)
                if found:
                    raise ValidationError('Vendor Reference must be unique')

    # @api.onchange('partner_id', 'company_id')
    # def onchange_partner_id(self):
    #     """ inherit function to trigger tax removal in order_line """
    #     super(PurchaseOrder, self).onchange_partner_id()
    #     # after calling the base function check if the partner_id has
    #     if not self.partner_id.has_tax:
    #         # re-trigger _compute_tax_id in order_line
    #         self.order_line._compute_tax_id()

    @api.onchange('partner_id')
    def onchange_partner_id_site(self):
        domain = [
            ('partner_id', '=', self.partner_id.id),
        ]
        sites = self.env['res.sites'].search(domain)
        if self.partner_id and sites:
            self.sites_id = sites[0].id

    @api.depends('order_line')
    def _compute_pr_numbers(self):
        self = self.with_user(SUPERUSER_ID)
        for record in self:
            pr_number_list = []
            for line in record.order_line:
                pr_number_list.append(line.request_id.name if line.request_id else '')

            pr_number_list = list(set(pr_number_list))
            pr_number_list.sort()
            pr_numbers = ', '.join(pr_number_list)
            record.pr_numbers = pr_numbers

    @api.depends('order_line')
    def _compute_requestor(self):
        self = self.with_user(SUPERUSER_ID)
        for record in self:
            req_number_list = []
            for line in record.order_line:
                req_number_list.append(line.request_id.requested_by.name if line.request_id.requested_by else '')

            req_number_list = list(set(req_number_list))
            req_number_list.sort()
            requestor_comp = ', '.join(req_number_list)
            record.requestor_comp = requestor_comp

    @api.depends('order_line')
    def _compute_requestor_names(self):
        self = self.with_user(SUPERUSER_ID)
        for record in self:
            req_number_list = []
            for line in record.order_line:
                req_number_list.append(line.request_id.requested_by.name if line.request_id.requested_by else '')

            req_number_list = list(set(req_number_list))
            req_number_list.sort()
            requestor_comp = ', '.join(req_number_list)
            record.requestor = requestor_comp

    def _edit_requestor(self):
        pass

    @api.depends('picking_ids')
    def _compute_rr_numbers(self):
        """ compute function to get rr_numbers """
        for rec in self:
            pickings = list(set(rec.picking_ids.mapped('name')))
            rec.rr_numbers = ', '.join(pickings)

    def emergency_cancel(self):
        # TODO FIXME remove after
        for rec in self:
            rec.write({'state': 'cancel'})

    def button_draft(self):
        for order in self:
            for pickings in order.picking_ids:
                if pickings.state == 'assigned':
                    pickings.write({'state': 'cancel'})
                    # raise UserError(_(
                    #     "Unable to set to draft this purchase order. You must cancel the related receipts first. Status Ready"))
                if pickings.state == 'done' and 'Return of' not in pickings.origin:
                    qty_return = 0
                    for moves in pickings.move_ids_without_package:
                        qty_return += moves.quantity_return
                        if qty_return == 0:
                            raise UserError(_(
                                "Unable to set to draft this purchase order. You must cancel the related receipts first. Status Done"))
            order.revision += 1
            order.old_value = order.amount_untaxed
        # set to draft and rejected to False to reset
        self.write({
            'state': 'draft',
            'rejected': False,
        })
        self._amount_all()

    @api.depends('order_line.is_gr_matched', 'picking_ids.move_ids_without_package.is_gr_matched')
    def _compute_fully_matched(self):
        for order in self:
            gr_match_status = []
            for order_line in order.order_line.filtered(lambda ol: ol.product_id.type == 'service'):
                gr_match_status.append(order_line.is_gr_matched)

            for picking in order.picking_ids:
                for stock_move in picking.move_ids_without_package:
                    gr_match_status.append(stock_move.is_gr_matched)

            order.is_fully_matched = all(gr_match_status)

    # @api.depends('order_line.product_id')
    # def _compute_service_po(self):
    #     for order in self:
    #         for order_line in order:
    #             if all(order_line.product_id.type) == 'service':
    #                 order.is_service_po = True
    #             else:
    #                 order.is_service_po = False

    @api.depends('amount_total', 'currency_id')
    def amount_to_text(self):
        for rec in self:
            # lang = 'id' if self.currency_id.name == 'IDR' else 'en'
            lang = 'en'
            currency_in_words = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount = num2words(int(rec.amount_total), lang=lang)
            rec.amount_in_words = words_amount.title() + " " + currency_in_words

    @api.depends('amount_total', 'currency_id')
    def amount_to_text_2(self):
        for rec in self:
            lang_2 = 'id' if rec.currency_id.name == 'IDR' else 'en'
            currency_in_words_2 = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount_2 = num2words(int(rec.amount_total), lang=lang_2)
            rec.amount_in_words_2 = words_amount_2.title() + " " + currency_in_words_2

    @api.onchange('currency_id', 'manual_currency_rate_active',
                  'manual_currency_rate', 'date_order')
    def _onchange_actual_rate(self):
        """ onchange function to set actual_rate to manual_currency_rate if any """
        self.ensure_one()
        if self.currency_id and self.currency_id.name != 'IDR':
            if not self.manual_currency_rate_active:
                sql = """
                    SELECT actual_rate AS rate
                    FROM res_currency_rate
                    WHERE company_id = %s AND currency_id = %s AND name <= '%s'
                    ORDER BY name DESC LIMIT 1
                """ % (self.company_id.id, self.currency_id.id, self.date_order)
                self.env.cr.execute(sql)
                currency = self.env.cr.dictfetchone()
                self.actual_rate = currency.get('rate', 1) if currency else 1
            else:
                self.actual_rate = self.manual_currency_rate
        else:
            self.actual_rate = 1

    @api.model
    def create(self, vals):
        if vals.get('quotation_number', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            quote_number = self.env['ir.sequence'].next_by_code('purchase.quotation', sequence_date=seq_date) or '/'
            vals.update({
                'quotation_number': quote_number,
                'name': quote_number,
            })

        if vals.get('order_line', []):  # check if order_line exist
            lines = vals.get('order_line', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                line[2]['line_number'] = idx + 1

        return super(PurchaseOrder, self).create(vals)

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(PurchaseOrder, self).write(vals)
        # find order_line, rewrite the line number
        for idx, line in enumerate(self.order_line):
            line.line_number = idx + 1
            # if line.amount_from_pr_line > 0 and line.price_subtotal > line.amount_from_pr_line:
            #     raise Warning(_('The price subtotal is over than the amount from PR Line.'))
        return res

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update({
            'po_description': self.po_description,
        })

        return super(PurchaseOrder, self).copy(default)

    def _prepare_picking(self):
        """ inherit function to add valid_location_ids """
        res = super(PurchaseOrder, self)._prepare_picking()
        user = self.user_id or self.env.user
        locations = user.location_ids
        res['valid_location_ids'] = [(6, 0, locations.ids)]

        # get all users from order_line, find related purchase_request_lines
        allowed_users = [y.requested_by.id for x in self.order_line for y in x.purchase_request_lines]

        # convert to set and list again to make sure uniqueness
        res['allowed_user_ids'] = [(6, 0, list(set(allowed_users)))]

        # update buyer_id
        res['buyer_id'] = self.buyer_id.id

        # change to vendor reference if exists
        if self.partner_ref:
            res['origin'] = self.partner_ref
        if self.date_order:
            res['scheduled_date'] = self.date_order
            res['date_deadline'] = self.date_order

        return res

    def _prepare_invoice(self):
        """ inherit function to add sites_id """
        res = super(PurchaseOrder, self)._prepare_invoice()

        # update sites_id
        if self.sites_id:
            res['sites_id'] = self.sites_id.id
        # update other_reference
        if self.other_name:
            res['other_reference'] = self.other_name

        return res

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            # crete number po when confirm order
            if order.state not in ['purchase', 'done'] \
                    and order.quotation_number not in ['New', '/']:
                if order.name in ['New', '/'] or order.name == order.quotation_number:
                    po_number = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                    order.write({'name': po_number})
            # add validation line order if product_id, episode and partner_id have been created before
            for list_order in order.order_line:
                line_order = self.env['purchase.order.line']
                data = line_order.search([('product_id', '=', list_order.product_id.id),
                                          ('company_id', '=', list_order.company_id.id)])
                if list_order.product_id and list_order.episode and list_order.order_id.partner_id:
                    for line in data:
                        for episode in list_order.episode:
                            value = []
                            for a in line.episode:
                                value.append(a.name)
                            if episode.id in value \
                                    and line.order_id.partner_id.id == list_order.order_id.partner_id.id \
                                    and line.product_id.id == list_order.product_id.id \
                                    and line.order_id.id != list_order.order_id.id \
                                    and line.company_id.id == list_order.company_id.id \
                                    and line.episode \
                                    and line.order_id.state in ['purchase', 'done']:
                                raise UserError(
                                    _('the episode is already exists on order number \'%s\'.') % (line.order_id.name,))
                        # if line.product_id.id == list_order.product_id.id \
                        #         and line.episode == list_order.episode \
                        #         and line.order_id.partner_id.id == list_order.order_id.partner_id.id \
                        #         and line.order_id.id != list_order.order_id.id \
                        #         and line.company_id.id == list_order.company_id.id \
                        #         and line.episode \
                        #         and line.order_id.state in ['purchase', 'done']:
                        #     raise UserError(
                        #         _('the order line is already exists on order number \'%s\'.') % (line.order_id.name,))
                            order._amount_all()

        return res

    def button_to_approve(self):
        self._check_subtotal()
        for order in self:
            if order.new_value < order.old_value and self.revision > 0 and self.state == 'draft':
                self.button_approve()
            else:
                if order.state not in ['purchase', 'done', 'cancel'] \
                        and order.quotation_number not in ['New', '/']:
                    # crete number po when button to approve
                    if order.name in ['New', '/'] or order.name == order.quotation_number:
                        po_number = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                        order.write({'name': po_number})
                    order.write({'state': 'to approve'})

                if order.company_id.purchase_dynamic_approval:
                    if not order.user_id.employee_id:
                        raise ValidationError('Please connect the user with the employee')

                    order._check_alias()
                    order._assign_approval()
                    order._check_limit()
                    order._send_approval_email()
                    order._amount_all()
        return True

    @api.depends('amount_untaxed')
    def _compute_amount_untaxed_field(self):
        for rec in self:
            rec.new_value = rec.amount_untaxed

    @api.depends('price_subtotal')
    def _check_subtotal(self):
        for rec in self:
            lines = rec.order_line
            if lines:
                for items in lines:
                    if items.price_subtotal == 0.0:
                        raise UserError(_('There is a zero subtotal in the order line. Subtotal cannot be zero.'))

    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve()
        for order in self:
            # if order.new_value < order.old_value:
            #     raise UserError(_('No need to approve, new amount untaxed is less than the previous one.'))
            # crete number po when confirm order
            if order.state in ['draft', 'sent'] and order.name in ['New', '/']:
                po_number = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                order.write({'name': po_number})
            # add validation line order if product_id, episode and partner_id have been created before
            for list_order in order.order_line:
                line_order = self.env['purchase.order.line']
                data = line_order.search([('product_id', '=', list_order.product_id.id),
                                          ('company_id', '=', list_order.company_id.id)])
                if list_order.product_id and list_order.episode and list_order.order_id.partner_id:
                    for line in data:
                        for episode in list_order.episode:
                            value = []
                            for a in line.episode:
                                value.append(a.name)
                            if episode.id in value \
                                    and line.order_id.partner_id.id == list_order.order_id.partner_id.id \
                                    and line.product_id.id == list_order.product_id.id \
                                    and line.order_id.id != list_order.order_id.id \
                                    and line.company_id.id == list_order.company_id.id \
                                    and line.episode \
                                    and line.order_id.state in ['purchase', 'done']:
                                raise UserError(
                                    _('the episode is already exists on order number \'%s\'.') % (line.order_id.name,))
                            order._amount_all()
        return res

    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))
            # TODO FIXME HERE we need to check picking, must be returned or picking is draft
            for pickings in order.picking_ids:
                if pickings.state == 'assigned':
                    pickings.write({'state': 'cancel'})
                    # raise UserError(_(
                    #     "Unable to cancel this purchase order. You must cancel the related receipts first. Status Ready"))
                if pickings.state == 'done' and 'Return of' not in pickings.origin:
                    qty_return = 0
                    for moves in pickings.move_ids_without_package:
                        qty_return += moves.quantity_return
                        if qty_return == 0:
                            raise UserError(_(
                                "Unable to cancel this purchase order. You must cancel the related receipts first. Status Done"))
            for line in order.order_line:
                for req_line in line.purchase_request_lines:
                    req_line.request_state = 'approved'

            # for request in order.order_line.mapped('request_id'):
            #     request.button_approved()

        self.write({
            'state': 'cancel',
            'mail_reminder_confirmed': False,
        })
        self._amount_all()

    def _get_attachment_report_id(self):
        """ override function to get attachment report id in string """
        return 'ins_base_mnc.ins_base_mnc_report_purchase_order_portrait'

    def _get_attachment(self):
        """ override function to get attachment from lines """
        attachment = self.env['ir.attachment']
        for line in self.order_line:
            for att in line.attachment_line_ids:
                attachment |= att
        return attachment

    def _get_approval_template(self):
        """ function to return mail template for approval """
        return 'ins_base_mnc.mnc_mail_purchase_order_approval'

    def _get_question_template(self):
        """ function to return mail template for question """
        return 'ins_base_mnc.mnc_mail_purchase_order_question'

    def _get_info_template(self):
        """ function to return mail template for info """
        return 'ins_base_mnc.mnc_mail_purchase_order_info'

    def _get_custom_report_attachment(self):
        """ helper function to get the attachment report name to embed """
        # get the same model and company, then try to get the attachment
        domain = [
            ('model', '=', 'purchase.order'),
            ('company_ids', 'in', self.company_id.id),
        ]
        config = self.env['report.config'].search(domain, limit=1)
        attachment = config.attachment_report_id.report_name if config and config.attachment_report_id else False
        return attachment

    def _get_custom_report_url(self):
        """ helper function to construct a report url """
        self.ensure_one()
        url = ''
        domain = [
            ('model', '=', 'purchase.order'),
            ('company_ids', 'in', self.company_id.id),
        ]
        config = self.env['report.config'].search(domain, limit=1)
        if config:
            url = '/report/pdf/%s/%s' % (config.report_id.report_name, self.id)
        else:
            msg = 'No Config found'
            raise ValidationError(msg)
        return url

    def button_print_report_from_config(self):
        """ function to print report from config """
        self.ensure_one()
        url = self._get_custom_report_url()
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def _get_general_terms_mnc(self):
        url = str('/ins_base_mnc/static/src/general/mnc/General-Terms-and-Conditions - Purchase-Order-MNC-1-halaman.pdf')
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new', 'tag': 'reload'}

    def action_user_approve(self, employee):
        """ inherit function to add rejection process """
        res = super(PurchaseOrder, self).action_user_approve(employee)
        if self._is_reject_found():
            self.rejected = True
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], compute='_compute_state', store=True, related=False)
    is_cancelled = fields.Boolean('Is Cancelled Already?', default=False)
    episode = fields.Many2many('purchase.master.episode', string='episode')
    qty_cancel = fields.Float(string='Qty Cancel', digits='Product Unit of Measure', copy=False, readonly=True)
    is_gr_matched = fields.Boolean(string="Is GR Matched?", default=False, compute='_compute_is_gr_matched')
    account_move_line_gr_match_ids = fields.Many2many('account.move.line', 'po_line_gr_match_rel', string="Account Move Line GR Match")
    account_id = fields.Many2one('account.account', 'Account')
    actual_rate = fields.Float('Rate', related='order_id.actual_rate', store=True)
    rfq_price = fields.Float('RFQ Price')
    asset_cost_progress_id = fields.Many2one('cip.configuration', 'CIP')
    line_number = fields.Integer('Line No')
    request_line_number = fields.Integer('PR Line No')
    attachment_line_ids = fields.Many2many('ir.attachment', string="Attachment")
    request_id = fields.Many2one('purchase.request', string="Purchase Request")
    buyer_id = fields.Many2one('res.buyer',
                               related='order_id.buyer_id', string="Buyer")
    modify = fields.Boolean('Modify', default=False)
    amount_from_pr_line = fields.Float('Amount from PR line')

    @api.depends('is_cancelled', 'order_id.state')
    def _compute_state(self):
        """ compute function to set the state """
        for rec in self:
            state = 'cancel'
            if not rec.is_cancelled:
                state = rec.order_id.state
            rec.state = state

    @api.depends('account_move_line_gr_match_ids')
    def _compute_is_gr_matched(self):
        for rec in self:
            rec.is_gr_matched = False
            # aml_ids = self.env['account.move.line'].search([('po_line_gr_match_ids', 'in', [rec.id])])
            if rec.account_move_line_gr_match_ids:
                qty_aml = sum([aml_id.quantity for aml_id in rec.account_move_line_gr_match_ids])
                if qty_aml == rec.qty_received:
                    rec.is_gr_matched = True
                else:
                    rec.is_gr_matched = False

    # def _get_product_purchase_description(self, product_lang):
    #     self.ensure_one()
    #     name = ''
    #     if product_lang.description_purchase:
    #         name = product_lang.description_purchase

    #     return name

    def unlink(self):
        for line in self:
            if line.order_id.state in ['purchase', 'done'] or line.order_id.state not in ['draft']:
                raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.state,))
        return super(PurchaseOrderLine, self).unlink()

    def cancel_line(self):
        """ function to cancel purchase line """
        for line in self:
            line_move = self.env['stock.move'].search([('purchase_line_id', '=', line.id),
                                                       ('state', '=', 'assigned'),
                                                       ('product_qty', '>', 0)])
            # check qty received
            sql_line = """
                    SELECT  sum(product_qty) as qty
                      FROM	stock_move
                     WHERE  state = 'done'
                       AND  purchase_line_id is not null
                       AND  purchase_line_id = %s
                    """
            param = line.id
            self.env.cr.execute(sql_line, [param])
            res = self.env.cr.dictfetchall()
            a = None
            for qty in res:
                a = qty
            for req_line in line.purchase_request_lines:
                req_line.request_state = 'approved'
            if line.order_id.state in ['purchase', 'done']:
                for move in line.order_id.picking_ids.move_lines:
                    if move.purchase_line_id.id == line.id and move.picking_id.state not in ['done', 'cancel']:
                        move.product_uom_qty = 0
                        if len(move) == 1:
                            move.picking_id.state = 'cancel'
                            move.state = 'cancel'
                        move.purchase_line_id.qty_cancel = \
                            move.purchase_line_id.product_qty - move.purchase_line_id.qty_received
                        # move.purchase_line_id.product_qty - a["qty"]
                        move.purchase_line_id.state = 'cancel'
                        # line.write({'product_qty': 0})
                    # NOTE: we don't want to change the state of the purchase, instead only the line
                    # the line's state is stored, so we guess it is safe
                    if len(line) == 1 and move.purchase_line_id.qty_received == 0 and move.picking_id.state == 'cancel':
                        line.state = 'cancel'
            if line.state not in ['purchase', 'done']:
                for moves in line_move:
                    if moves.state != 'assigned' and moves.product_qty > 0 and moves.purchase_line_id:
                        raise UserError(_('Cannot Cancel a purchase order line which is in state \'%s\'.') % (line.state,))
            # if line.state not in ['purchase', 'done'] \
            #         and line_move.state != 'assigned' \
            #         and line_move.product_qty > 0 \
            #         and line_move.purchase_line_id:
            #     raise UserError(_('Cannot Cancel a purchase order line which is in state \'%s\'.') % (line.state,))
            line.state = 'cancel'  # write state
            line.is_cancelled = True
            line.order_id._amount_all()
        return True

    # @api.constrains('price_subtotal', 'purchase_request_lines', 'product_id')
    # def _check_product_unit_price_with_request(self):
    #     """ constrains function to check if product price exceeds PR Lines """
    #     for rec in self:
    #         # find same product in PR Lines, and if any, get the first one then
    #         # compare the price_subtotal with the original_price
    #         request_lines = rec.purchase_request_lines.filtered(lambda x: x.product_id == rec.product_id)
    #         if request_lines:
    #             line = request_lines[0]
    #             if line and line.estimated_cost < rec.price_subtotal:
    #                 raise UserError('The Subtotal of the line exceeds the PR Line')

    # @api.onchange('price_unit')
    # def onchange_po_price(self):
    #     for line in self.purchase_request_lines:
    #         print(line)
    #         max_po_price = (100 + line.product_id.price_tolerance) * line.estimated_cost / 100
    #         print(max_po_price)
    #         if self.price_unit > max_po_price:
    #             raise UserError(_('Your price unit is over than the maximum price tolerance \'%s\'.') % (max_po_price,))

    @api.constrains('price_subtotal', 'rfq_price', 'price_unit', 'amount_from_pr_line')
    def compare_po_price_subtotal(self):
        """ constrains function to check price tolerance of a product """
        # NOTE: check context, if there is prevent_checking, just proceed
        context = self._context
        prevent_checking = context.get('prevent_checking', False)
        if prevent_checking:
            return
        for rec in self:
            if rec.amount_from_pr_line > 0 and not prevent_checking:
                # tolerance is based on price_unit
                price_unit = rec.rfq_price or rec.price_unit
                tolerance = rec.product_id.price_tolerance / 100 * price_unit

                # _logger.info('PR Line %s' % rec.request_line_number)
                # _logger.info('Tolerance %s' % tolerance)
                # _logger.info('Unit Price %s' % price_unit)
                # _logger.info('Amount PR %s' % rec.amount_from_pr_line)
                # _logger.info('Subtotal %s' % (rec.price_subtotal / rec.product_qty))
                # _logger.info('Block? %s' % (rec.price_subtotal / rec.product_qty > (rec.amount_from_pr_line + tolerance)))

                # actual subtotal must be divided with the product_qty
                actual_subtotal = rec.price_subtotal / rec.product_qty

                # must check qty also
                amount_pr = rec.amount_from_pr_line / rec.product_qty

                if actual_subtotal > (amount_pr + tolerance):
                    msg = """The price subtotal is over than the amount from PR Line.\nCheck line number %s from PR %s"""
                    raise Warning(msg % (rec.request_line_number, rec.request_id.name))

    @api.onchange('product_id', 'rfq_price', 'product_qty')
    def _onchange_rfq_price(self):
        """ onchange function to set price_unit to rfq_price """
        if self.rfq_price:
            self.price_unit = self.rfq_price

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        """ inherit function to force onchange on price_unit """
        super(PurchaseOrderLine, self)._onchange_quantity()
        self._onchange_rfq_price()

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ inherit function to force onchange on price_unit """
        super(PurchaseOrderLine, self).onchange_product_id()
        self._onchange_rfq_price()

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        """ inherit function to assign purchase_line_number to stock move """
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom)
        res['purchase_line_number'] = self.line_number
        res['purchase_order_number'] = self.order_id.name
        res['purchase_request_number'] = self.request_id.name
        res['requested_by'] = self.request_id.requested_by.id
        res['amount_total'] = self.price_subtotal
        return res

    def _prepare_account_move_line(self, move=False):
        """ inherit function to add line_number and move line_number"""
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        res['purchase_line_number'] = self.line_number
        if move:  # move exists, add picking_line_number
            res['picking_line_number'] = move.line_number
        return res

    # def _compute_tax_id(self):
    #     """ inherit function to check has_tax """
    #     super(PurchaseOrderLine, self)._compute_tax_id()
    #     for rec in self:
    #         if not rec.partner_id.has_tax:
    #             rec.taxes_id = [(5, 0, 0)]  # remove but not delete

    # @api.constrains('purchase_request_lines', 'state', 'price_subtotal')
    # def _check_pr_lines_and_state(self):
    #     """ """
    #     for rec in self:
    #         if rec.purchase_request_lines and rec.state != 'cancel':
    #             # filter out the purchase_request_lines with different purchase_lines
    #             valid_lines = rec.purchase_request_lines.filtered(
    #                 lambda x: rec not in x.purchase_lines.filtered(lambda y: y.state != 'cancel'))

    #             # then sum the price_subtotal of the purchase_lines in valid_lines
    #             amt_purchase = sum(valid_lines.mapped('purchase_lines.price_subtotal'))

    #             estimated_cost = sum(rec.purchase_request_lines.mapped('estimated_cost'))
    #             # if price_subtotal > (estimated_cost - amt_purchase), block
    #             if rec.price_subtotal > (estimated_cost - amt_purchase):
    #                 raise ValidationError('Cannot have subtotal more than PR Line')
