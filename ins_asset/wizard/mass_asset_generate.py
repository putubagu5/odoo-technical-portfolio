from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WizardMassAssetGenerate(models.TransientModel):
    _name = 'wizard.mass.asset.generate'
    _description = 'Mass Asset Generate'

    model_id = fields.Many2one('account.asset', 'Asset Model')
    company_id = fields.Many2one('res.company', 'Company',
                                 related='model_id.company_id')
    journal_id = fields.Many2one('account.journal', 'Journal')
    type = fields.Selection([
        ('merge', 'Merge'),
        ('split', 'Split'),
        ('add', 'Add to Asset'),
    ], 'Transaction Type')
    add_type = fields.Selection([
        ('age', 'Umur Aset'),
        ('value', 'Nilai Buku'),
    ], 'Add to Type')
    amount_add = fields.Float('Amount to Add', compute='_compute_amount_add')
    age_add = fields.Integer('Umur Asset')
    age_type = fields.Selection([
        ('month', 'Month'),
        ('year', 'Year'),
    ], 'Duration to Add', default='month')
    selected_asset_id = fields.Many2one('account.asset', 'Selected Asset')
    asset_name = fields.Char('Asset Name')
    date_acquisition = fields.Date('Acquisition Date')
    amount_total = fields.Float('Total', default=0.0)
    is_selected_all = fields.Boolean('Select All Lines', default=False)
    line_ids = fields.One2many('wizard.mass.asset.detail', 'generate_id',
                               'Details')
    purchase_domain_ids = fields.Many2many('purchase.order', compute='_compute_purchase_domain_ids')
    purchase_ids = fields.Many2many('purchase.order', 'wiz_mass_asset_po_rel', string='Purchase Order',
                                    domain="[('id', 'in', purchase_domain_ids)]"
                                    )


    def account_move_line_domain(self):
        domain = [
            ('move_id.company_id', '=', self.env.company.id),
            ('move_id.state', '=', 'posted'),
            ('asset_cost_progress_id', '=', False),
            ('created_asset_ids', '=', False),
            ('product_id.type', '=', 'consu'),
            ('product_id.is_asset', '=', True),
            ('purchase_line_id', '!=', False),
            ('purchase_line_id.move_ids', '!=', False),
        ]
        return domain

    @api.depends('line_ids')
    def _compute_purchase_domain_ids(self):
        for rec in self:
            domain = self.account_move_line_domain()
            if self.type == 'split':
                domain += [('quantity', '>', 1)]

            move_lines = self.env['account.move.line'].sudo().search(domain)
            rec.purchase_domain_ids = move_lines.mapped('purchase_line_id.order_id')

    @api.onchange('purchase_ids')
    def _onchange_purchase_ids(self):
        if self.purchase_ids:
            line_ids = [(5, 0, 0)]
            domain = self.account_move_line_domain()
            if self.type == 'split':
                domain += [('quantity', '>', 1)]

            domain += [('purchase_line_id.order_id', 'in', self.purchase_ids.ids)]
            move_lines = self.env['account.move.line'].sudo().search(domain)
            for ln in move_lines:
                picking = False
                move = ln.purchase_line_id.move_ids
                if move:
                    picking = move[0].picking_id.id
                data = {
                    'selected': True,
                    'product_id': ln.product_id.id,
                    'purchase_id': ln.purchase_line_id.order_id.id,
                    'picking_id': picking,
                    'invoice_id': ln.move_id.id,
                    'invoice_line_id': ln.id,
                    'qty': ln.quantity,
                    'price_unit': ln.price_unit,
                    'amount': ln.price_subtotal,
                    'purchase_line_number': ln.purchase_line_number,
                }
                line_ids.append((0, 0, data))

            self.line_ids = line_ids

    @api.onchange('is_selected_all')
    def _onchange_is_selected_all(self):
        if self.is_selected_all:
            for line in self.line_ids:
                line.selected = True
        else:
            for line in self.line_ids:
                line.selected = False

    @api.depends('line_ids', 'type', 'add_type')
    def _compute_amount_add(self):
        """ compute function to calculated selected lines """
        # NOTE: calculates if and only if the type is add and add_type is value
        for rec in self:
            amount = 0
            if rec.type == 'add' and rec.add_type == 'value':
                amount = sum(rec.line_ids.filtered(lambda x: x.selected).mapped('amount'))
            rec.amount_add = amount

    @api.model
    def default_get(self, fields):
        """ inherit function to set line_ids """
        res = super(WizardMassAssetGenerate, self).default_get(fields)

        # find all invoice line -> invoice -> purchase -> picking -> stock move
        # filter: posted invoice, invoice line with product type consumable,
        # product with same asset model, invoice line with no created_asset_ids
        # and if type is SPLIT, find invoice line with quantity > 1
        # get invoice line price total, sum qty_done of stock move line
        # to check if invoice line has no asset, check from related table
        # find NULL
        lines = []

        domain = self.account_move_line_domain()
        if self.type == 'split':
            domain += [('quantity', '>', 1)]

        # get account.move.line, traceback to account.move, purchase.order
        # stock.picking
        move_lines = self.env['account.move.line'].sudo().search(domain)
        for ln in move_lines:
            picking = False
            move = ln.purchase_line_id.move_ids
            if move:
                picking = move[0].picking_id.id
            data = {
                'selected': True,
                'product_id': ln.product_id.id,
                'purchase_id': ln.purchase_line_id.order_id.id,
                'picking_id': picking,
                'invoice_id': ln.move_id.id,
                'invoice_line_id': ln.id,
                'qty': ln.quantity,
                'price_unit': ln.price_unit,
                'amount': ln.price_subtotal,
                'purchase_line_number': ln.purchase_line_number,
            }
            lines.append((0, 0, data))

        res['line_ids'] = lines

        # get account.journal default
        journal_id = self.env['account.journal'].search([
            ('type', '=', 'general'),
        ], limit=1)
        res['journal_id'] = journal_id.id

        return res

    def _check_lines(self):
        """ helper function to check if the lines could be processed """
        # rules:
        # 1. regardless of the type, check the line if any line is selected
        # 2. type == split, ONLY ONE item in lines is allowed
        # NOTE: account is same
        msg = ''
        if not any([x.selected for x in self.line_ids]):
            msg = 'Please select item in lines'
            raise ValidationError(msg)

        if self.type == 'split' and len(self.line_ids.filtered(lambda x: x.selected)) > 1:
            msg = 'Split transaction could only process 1 selected line!'
            raise ValidationError(msg)

        if self.date_acquisition < max(self.line_ids.filtered(lambda x: x.selected).mapped('invoice_id.date')):
            msg = 'Acquisition Date is earlier than latest Date in line!'
            raise ValidationError(msg)

    def button_generate(self):
        """ function to generate assets """
        self._check_lines()  # check first
        details = self.line_ids.filtered(lambda x: x.selected)
        journal = self.journal_id.id  # always use the journal
        if not self.type:  # nothing, proceed
            for line in details:
                # name comes from purchase, product code and name
                name = '%s %s %s' % (
                    line.purchase_id.name, line.product_id.default_code,
                    line.product_id.name)
                source_line = []
                vals = {
                    # 'invoice_id': line.invoice_id.id,
                    'invoice_name': line.invoice_id.name,
                    'invoice_date': line.invoice_id.date,
                    'invoice_line_number': line.line_number,
                    # 'purchase_id': line.purchase_id.id,
                    'purchase_name': line.purchase_id.name,
                    'purchase_line_number': line.purchase_line_number,
                    'description': line.product_id.display_name,
                    'amount': line.amount,
                    'product_id': line.product_id.id,
                }
                source_line.append((0, 0, vals))
                data = {
                    'name': name,
                    'qty': line.qty,
                    'purchase_id': line.purchase_id.id,
                    'picking_id': line.picking_id.id,
                    'model_id': line.model_id.id,
                    'original_value': line.amount,
                    'acquisition_date': self.date_acquisition,
                    'date_received': line.date_acquisition,
                    'state': 'draft',
                    'asset_type': 'purchase',
                    'origin_ids': [(4, line.invoice_line_id.id)],
                    'source_line_ids': source_line,
                }

                # create data, call _onchange_model_id, then write cache
                new_asset = self.env['account.asset'].new(data)
                new_asset._onchange_model_id()  # to assign journal and accounts
                vals = new_asset._convert_to_write(new_asset._cache)
                asset = self.env['account.asset'].create(vals)
                asset.with_context({
                    'product_id': line.product_id,
                    'journal_id': journal,
                }).action_move_create(partner_id=line.partner_id)

        elif self.type == 'merge':  # merge create 1 asset and 1 journal
            name = self.asset_name
            product = details[0].product_id
            picking = details[0].picking_id
            source_line = []
            for detail in details:
                vals = {
                    # 'invoice_id': detail.invoice_id.id,
                    # 'purchase_id': detail.purchase_id.id,
                    'invoice_name': detail.invoice_id.name,
                    'purchase_name': detail.purchase_id.name,
                    'invoice_line_number': detail.line_number,
                    'purchase_line_number': detail.purchase_line_number,
                    'description': detail.product_id.display_name,
                    'amount': detail.amount,
                    'product_id': detail.product_id.id,
                }
                source_line.append((0, 0, vals))
            total = sum(x.amount for x in details)
            data = {
                'name': name,
                'qty': 1,
                'picking_id': picking.id,
                'model_id': self.model_id.id,
                'original_value': total,
                'acquisition_date': self.date_acquisition,
                'date_received': self.date_acquisition,
                'state': 'draft',
                'asset_type': 'purchase',
                'origin_ids': [(4, x.invoice_line_id.id) for x in details],
                'source_line_ids': source_line,
            }

            # create data, call _onchange_model_id, then write cache
            new_asset = self.env['account.asset'].new(data)
            new_asset._onchange_model_id()  # to assign journal and accounts
            vals = new_asset._convert_to_write(new_asset._cache)
            asset = self.env['account.asset'].create(vals)
            asset.with_context({
                'product_id': product,
                'journal_id': journal,
            }).action_move_create()

        elif self.type == 'split':  # based on selected line, loop qty
            # NOTE: for split, take the price_unit instead of amount
            line = details
            for x in range(int(line.qty)):
                # name comes from purchase, product code and name
                name = '%s %s %s (%s)' % (
                    line.purchase_id.name, line.product_id.default_code,
                    line.product_id.name, x + 1)
                source_line = []
                vals = {
                    # 'invoice_id': line.invoice_id.id,
                    'invoice_name': line.invoice_id.name,
                    'invoice_line_number': line.line_number,
                    # 'purchase_id': line.purchase_id.id,
                    'purchase_name': line.purchase_id.name,
                    'purchase_line_number': line.purchase_line_number,
                    'description': line.product_id.display_name,
                    'amount': line.amount,
                    'product_id': line.product_id.id,
                }
                source_line.append((0, 0, vals))
                data = {
                    'name': name,
                    'qty': 1,
                    'purchase_id': line.purchase_id.id,
                    'picking_id': line.picking_id.id,
                    'model_id': line.model_id.id,
                    'original_value': line.price_unit,
                    'acquisition_date': self.date_acquisition,
                    'date_received': line.date_acquisition,
                    'state': 'draft',
                    'asset_type': 'purchase',
                    'origin_ids': [(4, line.invoice_line_id.id)],
                    'source_line_ids': source_line,
                }

                # create data, call _onchange_model_id, then write cache
                new_asset = self.env['account.asset'].new(data)
                new_asset._onchange_model_id()  # to assign journal and accounts
                vals = new_asset._convert_to_write(new_asset._cache)
                asset = self.env['account.asset'].create(vals)
                asset.with_context({
                    'product_id': line.product_id,
                    'journal_id': journal,
                }).action_move_create(partner_id=line.partner_id)

        elif self.type == 'add':
            # NOTE: if add_type == 'age', remaining depreciation age is added
            # to the selected asset and last book value will be added with the
            # amount_add
            # if add_type == 'value', depreciable value of selected asset is added
            # with amount_add and recalculated but only for the following month

            # NOTE: every process will recalculate

            # regardless of the type, will add the amount_add
            self.selected_asset_id.write({'amount_add': self.amount_add})

            # type is age
            if self.add_type == 'age' and self.selected_asset_id:
                # check the age_type, if month to year (12) then divide by 12
                add = 0
                if self.age_type == 'month':
                    add = self.age_add
                    if self.selected_asset_id.method_period == '12':
                        add = self.age_add / 12

                # check if year, multiply by 12
                if self.age_type == 'year':
                    add = self.age_add
                    if self.selected_asset_id.method_period == 1:
                        add = self.age_add * 12

                self.selected_asset_id.method_number += add

            # always recompute depreciation
            self.selected_asset_id.compute_depreciation_board()

        return True
