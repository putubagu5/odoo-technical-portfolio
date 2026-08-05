from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import OrderedSet


class StockMove(models.Model):
    _inherit = 'stock.move'

    valid_location_ids = fields.Many2many(related='picking_id.valid_location_ids')
    amount_total = fields.Float('Amount', compute='_compute_amount_total')
    is_gr_matched = fields.Boolean(string="Is GR Matched?", default=False, compute='_compute_is_gr_matched')
    account_move_line_gr_match_ids = fields.Many2many('account.move.line', 'stock_move_gr_match_rel',
                                                      string="Account Move Line GR Match")
    line_number = fields.Integer('Line No')
    purchase_line_number = fields.Integer('PO Line No')
    purchase_order_number = fields.Char('PO No')
    purchase_request_number = fields.Char('PR No')
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
    )
    quantity_done = fields.Float('Quantity Done', compute='_quantity_done_compute', digits='Product Unit of Measure',
                                 inverse='_quantity_done_set', store=True)
    quantity_return = fields.Float('Quantity Return', default=0.0)
    qty_invoiced = fields.Float('Billed Qty', related='purchase_line_id.qty_invoiced')
    qty_avail_to_bill = fields.Float('Qty Avail to Bill', compute='_compute_qty_avail_to_bill')

    @api.depends('purchase_line_id')
    def _compute_amount_total(self):
        """ compute function to get amount_total from purchase_line_id """
        for rec in self:
            rec.amount_total = sum(rec.purchase_line_id.mapped('price_subtotal'))

    @api.depends('quantity_done', 'qty_invoiced')
    def _compute_qty_avail_to_bill(self):
        """ compute function to get qty_avail_to_bill """
        for rec in self:
            rec.qty_avail_to_bill = rec.quantity_done - rec.qty_invoiced

    @api.depends('account_move_line_gr_match_ids')
    def _compute_is_gr_matched(self):
        for rec in self:
            # aml_ids = self.env['account.move.line'].search([('stock_move_gr_match_ids', 'in', [rec.id])])
            qty_aml = sum([aml_id.quantity for aml_id in rec.account_move_line_gr_match_ids])
            if qty_aml == rec.quantity_done:
                rec.is_gr_matched = True
            else:
                rec.is_gr_matched = False

    def _action_done(self, cancel_backorder=False):
        '''
        Inherit _action_done to creating journal entry for product with type 'consu'
        '''
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        for move in self:
            print(move._is_returned(valued_type='in'), move._is_returned(valued_type='out'))
            if move._is_in() and move.product_id.type == 'consu' and move.product_id.valuation == 'real_time' and not \
                    move._is_returned(valued_type='in'):
                company_to = move._is_in() and move.mapped('move_line_ids.location_dest_id.company_id') or False
                if not move.product_id.categ_id.property_stock_journal:
                    raise UserError(
                        _('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
                if not move.product_id.categ_id.property_stock_account_input_categ_id:
                    raise UserError(
                        _('Cannot find a stock input account for the product %s. You must define one on the product category, before processing this operation.') % (
                            move.product_id.display_name))
                if not move.product_id.property_account_expense_id:
                    raise UserError(
                        _('Cannot find a expense account for the product %s. You must define one on the product, before processing this operation.') % (
                            move.product_id.display_name))

                journal_id = move.product_id.categ_id.property_stock_journal.id
                acc_src = move.product_id.categ_id.property_stock_account_input_categ_id.id
                acc_valuation = move.product_id.property_account_expense_id.id

                # check if move has purchase_line_id, use account_id if exists
                if move.purchase_line_id and move.purchase_line_id.account_id:
                    acc_valuation = move.purchase_line_id.account_id.id

                description = "{} - {}".format(move.picking_id.name, move.product_id.name)
                unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
                if move.product_id.cost_method == 'standard':
                    unit_cost = move.product_id.standard_price
                qty = 0

                res = OrderedSet()
                for move_line in move.move_line_ids:
                    if move_line.owner_id and move_line.owner_id != move_line.company_id.partner_id:
                        continue
                    res.add(move_line.id)

                for ml in self.env['stock.move.line'].browse(res):
                    qty += ml.product_uom_id._compute_quantity(ml.qty_done, move.product_id.uom_id)

                cost = qty * unit_cost
                move.with_company(company_to)._create_account_move_line(acc_src, acc_valuation, journal_id, qty,
                                                                        description, False, cost)
            if move._is_out() and move.product_id.type == 'consu' and move.product_id.valuation == 'real_time' and \
                    move._is_returned(valued_type='out'):
                print('masuk sini ketika return')
                company_from = move.mapped('move_line_ids.location_id.company_id')
                journal_id = move.product_id.categ_id.property_stock_journal.id
                acc_dest = move.product_id.categ_id.property_stock_account_input_categ_id.id
                acc_valuation = move.product_id.property_account_expense_id.id

                # check if move has purchase_line_id, use account_id if exists
                if move.purchase_line_id and move.purchase_line_id.account_id:
                    acc_valuation = move.purchase_line_id.account_id.id
                description = "{} - {}".format(move.picking_id.name, move.product_id.name)
                unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
                if move.product_id.cost_method == 'standard':
                    unit_cost = move.product_id.standard_price
                qty = 0

                res = OrderedSet()
                for move_line in move.move_line_ids:
                    if move_line.owner_id and move_line.owner_id != move_line.company_id.partner_id:
                        continue
                    res.add(move_line.id)

                for ml in self.env['stock.move.line'].browse(res):
                    qty += ml.product_uom_id._compute_quantity(ml.qty_done, move.product_id.uom_id)

                cost = qty * unit_cost
                move.with_company(company_from)._create_account_move_line(acc_valuation, acc_dest, journal_id, qty,
                                                                          description, False, cost)
        return res

    def _get_accounting_data_for_valuation(self):
        """ inherit function to replace account value """
        journal_id, acc_src, acc_dest, acc_valuation = super(StockMove, self)._get_accounting_data_for_valuation()

        # picking operation type is outgoing and use_product_expense
        is_outgoing = self.picking_id.picking_type_code == 'outgoing'
        use_product_expense = self.picking_id.picking_type_id.use_product_expense
        # if picking is outgoing and operation type use expense account
        # bypass the acc_dest
        if is_outgoing and use_product_expense:
            acc_dest = self.product_id.property_account_expense_id.id

        return journal_id, acc_src, acc_dest, acc_valuation

    def _prepare_common_svl_vals(self):
        """ inherit function to change the description field """
        res = super(StockMove, self)._prepare_common_svl_vals()
        if self.stock_valuation_layer_ids:
            description = self.reference and '%s - %s' % (self.reference, self.description_picking)
            res['description'] = description
        return res

    def _generate_valuation_lines_data(
        self, partner_id, qty, debit_value, credit_value, debit_account_id,
            credit_account_id, description):
        """ inherit function to brutally add the name and ref """
        res = super(StockMove, self)._generate_valuation_lines_data(
            partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)

        self.ensure_one()
        if self.stock_valuation_layer_ids:  # if this exists, brutally update the name of lines
            description = self.reference and '%s - %s' % (self.reference, self.description_picking)
            credit_vals = res['credit_line_vals']
            debit_vals = res['debit_line_vals']
            credit_vals['name'] = description
            credit_vals['ref'] = description
            debit_vals['name'] = description
            debit_vals['ref'] = description

        return res

    def _create_account_move_line(
            self, credit_account_id, debit_account_id, journal_id, qty,
            description, svl_id, cost):
        """ inherit function to update account.move with stock_move_id """
        super(StockMove, self)._create_account_move_line(
            credit_account_id, debit_account_id, journal_id, qty,
            description, svl_id, cost)
        # try to find the account.move having stock_move_id = id, if found, update ref
        description = self.reference and '%s - %s' % (self.reference, self.description_picking)
        account_move = self.env['account.move'].search([('stock_move_id', '=', self.id)])
        if account_move:  # F you, the whole of you
            account_move.write({'ref': description})

    # def _account_entry_move(self, qty, description, svl_id, cost):
    #     """ Accounting Valuation Entries """
    #     self.ensure_one()
    #     if self.product_id.type not in ['product', 'consu']:
    #         # keep stock valuation for consumable products
    #         print(self.product_id.type, 'kalau consu harusnya ndak masuk sini')
    #         return False
    #     if self.restrict_partner_id:
    #         # if the move isn't owned by the company, we don't make any valuation
    #         return False
    #
    #     location_from = self.location_id
    #     location_to = self.location_dest_id
    #     company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
    #     company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False
    #
    #     # replace cost return from cost price product with cost from purchase order
    #     if self.purchase_line_id and self.origin_returned_move_id and self.product_id.type == 'consu':
    #         cost = self.purchase_line_id.price_unit
    #         self.price_unit = cost
    #         # create new outstanding receiving after return receive
    #         # self._create_new_picking()
    #
    #     # Create Journal Entry for products arriving in the company; in case of routes making the link between several
    #     # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
    #     if self._is_in():
    #         journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
    #         if location_from and location_from.usage == 'customer':  # goods returned from customer
    #             self.with_company(company_to)._create_account_move_line(acc_dest, acc_valuation, journal_id, qty,
    #                                                                     description, svl_id, cost)
    #         else:
    #             self.with_company(company_to)._create_account_move_line(acc_src, acc_valuation, journal_id, qty,
    #                                                                     description, svl_id, cost)
    #
    #     # Create Journal Entry for products leaving the company
    #     if self._is_out():
    #         cost = -1 * cost
    #         journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
    #         print(self._get_accounting_data_for_valuation())
    #         if location_to and location_to.usage == 'supplier':  # goods returned to supplier
    #             self.with_company(company_from)._create_account_move_line(acc_valuation, acc_src, journal_id, qty,
    #                                                                       description, svl_id, cost)
    #         else:
    #             self.with_company(company_from)._create_account_move_line(acc_valuation, acc_dest, journal_id, qty,
    #                                                                       description, svl_id, cost)
    #
    #     if self.company_id.anglo_saxon_accounting:
    #         # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
    #         journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
    #         if self._is_dropshipped():
    #             if cost > 0:
    #                 self.with_company(self.company_id)._create_account_move_line(acc_src, acc_valuation, journal_id,
    #                                                                              qty, description, svl_id, cost)
    #             else:
    #                 cost = -1 * cost
    #                 self.with_company(self.company_id)._create_account_move_line(acc_valuation, acc_dest, journal_id,
    #                                                                              qty, description, svl_id, cost)
    #         elif self._is_dropshipped_returned():
    #             if cost > 0:
    #                 self.with_company(self.company_id)._create_account_move_line(acc_valuation, acc_src, journal_id,
    #                                                                              qty, description, svl_id, cost)
    #             else:
    #                 cost = -1 * cost
    #                 self.with_company(self.company_id)._create_account_move_line(acc_dest, acc_valuation, journal_id,
    #                                                                              qty, description, svl_id, cost)
    #
    #     if self.company_id.anglo_saxon_accounting:
    #         # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
    #         self._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=self.product_id)

    # def _create_new_picking(self):
    #     backorders = self.env['stock.picking']
    #     for picking in self.origin_returned_move_id.picking_id:
    #         print(picking.move_lines)
    #         moves_to_backorder = picking.move_lines
    #         if moves_to_backorder:
    #             backorder_picking = picking.copy({
    #                 'name': '/',
    #                 'origin': picking.origin,
    #                 'has_deadline_issue': False,
    #                 'state': 'assigned'
    #             })
    #             print(backorder_picking, 'masuk backorder')
    #             picking.message_post(
    #                 body=_(
    #                     'The New Receiving <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
    #                          backorder_picking.id, backorder_picking.name))
    #             backorders |= backorder_picking
    #             backorders.action_assign()
