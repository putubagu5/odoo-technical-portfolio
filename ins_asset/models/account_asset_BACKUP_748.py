from datetime import date
from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    # depreciation_entries_count = fields.Integer(compute='_entry_count', string='Depreciation Entries')
    asset_no = fields.Char('Asset Number', default='/')
    segment_id = fields.Many2one('asset.segment', 'Segment', ondelete='restrict')
    qty = fields.Float('Quantity')
    last_location_id = fields.Many2one('asset.location', 'Last Location')
    # TODO warehouse
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    date_received = fields.Date('Received Date')
    specification = fields.Char('Specification')
    country_id = fields.Many2one('res.country', 'Made in Country')
    brand = fields.Char('Brand')
    serial_number = fields.Char('Serial Number')
    tag_number = fields.Char('Tag Number')
    asset_condition_id = fields.Many2one('asset.condition', 'Condition')
    date_write_off = fields.Date('Write Off Date')
    date_transfer = fields.Date('Transfer Date')
    assignee_id = fields.Many2one('hr.employee', 'Assignee')
    origin_ids = fields.Many2many('account.move.line', 'generate_asset_move_rel',
                                  'asset_id', 'move_line_id', string='Origin')
    is_accumulated = fields.Boolean('Accumulated', default=False, copy=False)
    total_duration_disposal = fields.Integer('Total Duration Disposal')

    product_tmpl_ids = fields.One2many('product.template', 'asset_model_id',
                                       string='Product Template')

    source_line_ids = fields.One2many('asset.source.line', 'asset_id',
                                      string='Source')

    depreciation_line_ids = fields.One2many('account.asset.depreciation.line', 'asset_id',
                                            string='Depreciation Lines', readonly=True,
                                            states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    amount_add = fields.Monetary('Amount Add', help='Add Amount from Mass Addition')
    value_residual = fields.Monetary(string='Depreciable Value', compute='_compute_value_residual')
    period_line_id = fields.Many2one('asset.period.line', 'Period Line')
    invoice_id = fields.Many2one('account.move','Invoice')

    @api.depends(
        'original_value', 'salvage_value', 'already_depreciated_amount_import',
        'depreciation_move_ids.state', 'depreciation_move_ids.amount_total',
        'depreciation_move_ids.reversal_move_id', 'amount_add'
    )
    def _compute_value_residual(self):
        """ override function to calculate residual based on values """
        for record in self:
            posted = record.depreciation_move_ids.filtered(
                lambda m: m.state == 'posted' and not m.reversal_move_id
            )
            record.value_residual = (
                record.original_value
                - record.salvage_value
                - record.already_depreciated_amount_import
                - sum(move._get_depreciation() for move in posted)
                + record.amount_add
            )

    def _assign_period(self):
        """ helper function to assign period_line_id """
        domain = [
            ('date_start', '<=', self.acquisition_date),
            ('date_end', '>=', self.acquisition_date),
        ]
        period_line = self.env['asset.period.line'].search(domain, limit=1)
        if period_line:
            if period_line.state == 'open':
                self.period_line_id = period_line.id
            else:
                raise ValidationError('Asset Period is closed')

    def validate(self):
        # self.compute_depreciation_board()

        # check period first
        self._assign_period()

        if self.asset_no == '/':
            self.asset_no = self.env['ir.sequence'].next_by_code('asset.number')
        fields = [
            'method',
            'method_number',
            'method_period',
            'method_progress_factor',
            'salvage_value',
            'original_move_line_ids',
        ]
        ref_tracked_fields = self.env['account.asset'].fields_get(fields)
        for asset in self:
            for source in asset.source_line_ids:
                if source.invoice_date:
                    if asset.acquisition_date < source.invoice_date:
                        raise ValidationError('Acquisition date cannot less than invoice date.')
            tracked_fields = ref_tracked_fields.copy()
            if asset.method == 'linear':
                del(tracked_fields['method_progress_factor'])
            dummy, tracking_value_ids = asset._message_track(tracked_fields, dict.fromkeys(fields))
            asset_name = {
                'purchase': (_('Asset created'), _('An asset has been created for this move:')),
                'sale': (_('Deferred revenue created'), _('A deferred revenue has been created for this move:')),
                'expense': (_('Deferred expense created'), _('A deferred expense has been created for this move:')),
            }[asset.asset_type]
            msg = asset_name[1] + ' <a href=# data-oe-model=account.asset data-oe-id=%d>%s</a>' % (asset.id, asset.name)
            asset.message_post(body=asset_name[0], tracking_value_ids=tracking_value_ids)
            for move_id in asset.original_move_line_ids.mapped('move_id'):
                move_id.message_post(body=msg)
            # if not asset.depreciation_move_ids:
            if not asset.depreciation_line_ids:
                asset.compute_depreciation_list()
            asset._check_depreciations()
            asset.write({'state': 'open'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['asset_no'] = self.env['ir.sequence'].next_by_code('asset.number')
        new_recs = super(AccountAsset, self.with_context(mail_create_nolog=True)).create(vals_list)
        return new_recs

    def write(self, vals):
        """ inherit function to force assign asset analytic """
        analytic = vals.get('account_analytic_id', False)
        res = super(AccountAsset, self).write(vals)
        if self.depreciation_move_ids:
            lines = self.depreciation_move_ids.filtered(
                lambda x: x.state == 'draft')
            for line in lines:
                for mline in line.line_ids:
                    mline.asset_analytic_account_id = analytic
        return res

    def _create_move_lines(self, name, partner, debit_account, credit_account):
        """ function to generate move lines """
        # generate debit and credit dict
        journal = self._context.get('journal_id', False)
        if not journal:
            journal = self.model_id.journal_id.id

        amount = self._context.get('amount', 0)
        if not self._context.get('amount'):
            amount = self.original_value

        debit = {
            'name': name,
            'partner_id': partner.id if partner else False,
            'account_id': debit_account,
            'journal_id': journal,
            'date': date.today(),
            'debit': amount,
            'credit': 0,
        }
        credit = {
            'name': name,
            'partner_id': partner.id if partner else False,
            'account_id': credit_account,
            'journal_id': journal,
            'date': date.today(),
            'debit': 0,
            'credit': amount,
        }
        return [(0, 0, debit), (0, 0, credit)]

    def _get_credit_account(self):
        """ helper function to get credit account """
        context = self._context
        account = context.get('credit_account_id', False)
        product = self._context.get('product_id', False)
        if product:
            # move will be created using journal from asset model, credit account
            # taken from the stock journal of each asset detail, debit account from
            # asset model expense account, value from assset detail amount
            # to get the valuation journal from picking
            # clue: loop picking.move_lines.filtered with no reversed_entry_id
            # then line_ids filtered with debit value and product is same as product_id
            picking = self.picking_id
            move = picking.move_lines.filtered(lambda x: x.product_id == product)[:1]
            receipt = move.account_move_ids.filtered(
                lambda x: not x.reversed_entry_id).line_ids.filtered(lambda x: x.debit)

            if not receipt:
                return account
            else:
                account = receipt.account_id[0].id
        return account

    def _get_debit_account(self):
        """ helper function to get debit account """
        context = self._context
        account = context.get('debit_account_id', False)
        if not account:
            account = self.model_id.account_asset_id.id
        return account

    def _get_journal(self):
        """ helper function to get journal """
        context = self._context
        journal = context.get('journal_id', False)
        if not journal:
            journal = self.model_id.journal_id.id
        return journal

    def _get_asset_name(self):
        """ helper function to get asset name """
        context = self._context
        name = context.get('name', '')
        picking = self.picking_id if self.picking_id else False
        product = context.get('product_id', False)
        if not name and picking and product:
            pc_name = picking.name if picking else ''
            name = '%s - %s' % (pc_name, product.name)
        return name

    def action_move_create(self, partner_id=False):
        """ function to create and post journal entry """
        context = self._context
        credit_account = self.with_context(context)._get_credit_account()
        debit_account = self.with_context(context)._get_debit_account()
        journal = self.with_context(context)._get_journal()
        name = self.with_context(context)._get_asset_name()
        move_date = date.today()
        move_lines = self.with_context(context)._create_move_lines(
            name, partner_id, debit_account, credit_account)
        move_dict = {
            'narration': 'Asset %s' % name,
            'ref': move_date.strftime('%B %Y'),
            'journal_id': journal,
            'date': move_date,
            'line_ids': move_lines,
        }
        move = self.env['account.move'].create(move_dict)
        move._post()  # direclty post
        return True

    def button_accumulate(self):
        """ function to accumulate past amount of asset journals """
        lines = self.depreciation_move_ids

        # sum all value before acquisition_date
        amount = sum(x.amount_total for x in lines if x.date <= self.acquisition_date)

        # find the first line with date after acquisition_date, update amount_total
        current_lines = lines.filtered(lambda x: x.date > self.acquisition_date)
        if current_lines:
            # sort by date first then add
            current_lines = current_lines.sorted(key=lambda x: x.date)
            first_line = current_lines[0]
            first_line_amount = first_line.amount_total
            first_line.write({'amount_total': amount + first_line_amount})

        # cancel all journals before acquisition_date and empty out the values
        previous_lines = lines.filtered(lambda x: x.date <= self.acquisition_date)
        for ln in previous_lines:
            ln.button_cancel()
            ln.write({'amount_total': 0, 'asset_depreciated_value': 0})

        self.is_accumulated = True
        return True

    def set_to_close(self, invoice_line_id, date=None):
        """ inherit function to check all draft lines in depreciation board """
        # find draft state in depreciation_move_ids, assign to total_duration_disposal
        print(self,invoice_line_id,'ketika sell masuk sini dulu harusnya')
        len_disposal = len(self.depreciation_move_ids.filtered(lambda x: x.state == 'draft'))
<<<<<<< HEAD
        print(len_disposal, 'len_disposal')

=======
        self.total_duration_disposal = len_disposal
        self.invoice_id = invoice_line_id.move_id.id
>>>>>>> d9c7251d618f5bd9b45a90189fd188183344c4bb
        res = super(AccountAsset, self).set_to_close(invoice_line_id, date)
        print(res,'isi res kapan')
        self.write({'total_duration_disposal': len_disposal})
        # self.total_duration_disposal = len_disposal
        print(self.total_duration_disposal,'total_duration_disposal')
        return res

    def action_validate_assets(self):
        """ function to validate all selected assets """
        for rec in self:
            rec.validate()

    def action_sell_assets(self):
        """ function to open wizard to sell multi assets """
        asset_ids = self._context.get('active_ids', [])

        # check if there are selected records
        if not asset_ids:
            raise ValidationError('Please select records')

        wizard = self.env['wizard.sell.asset'].create({
            'asset_ids': asset_ids,
        })
        return {
            'name': 'Sell or Dispose Assets',
            'res_model': 'wizard.sell.asset',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard.id,
        }

    def _post(self, soft=True):
        """ inherit function to change deprecated to True """
        res = super(AccountAsset, self)._post(soft=soft)
        # if and only if asset_id exists and depreciated is False
        for rec in self:
            if rec.asset_id and not rec.depreciated:
                rec.depreciated = True
        return res

    def _compute_board_undone_dotation_nb(self, depreciation_date, total_days):
        undone_dotation_number = self.method_number
        # if self.method_time == 'end':
        #     end_date = self.method_end
        #     undone_dotation_number = 0
        #     while depreciation_date <= end_date:
        #         depreciation_date = date(depreciation_date.year, depreciation_date.month,
        #                                  depreciation_date.day) + relativedelta(months=+self.method_period)
        #         undone_dotation_number += 1
        if self.prorata:
            undone_dotation_number += 1
        return undone_dotation_number

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr,
                              undone_dotation_number, posted_depreciation_line_ids,
                              total_days, depreciation_date):
        amount = 0
        if sequence == undone_dotation_number:
            amount = residual_amount
        else:
            if self.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if self.prorata:
                    amount = amount_to_depr / self.method_number
                    if sequence == 1:
                        date = self.acquisition_date
                        if self.method_period % 12 != 0:
                            month_days = calendar.monthrange(date.year, date.month)[1]
                            days = month_days - date.day + 1
                            amount = (amount_to_depr / self.method_number) / month_days * days
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(date)['date_to'] - date).days + 1
                            amount = (amount_to_depr / self.method_number) / total_days * days
            elif self.method == 'degressive':
                amount = residual_amount * self.method_progress_factor
                if self.prorata:
                    if sequence == 1:
                        date = self.acquisition_date
                        if self.method_period % 12 != 0:
                            month_days = calendar.monthrange(date.year, date.month)[1]
                            days = month_days - date.day + 1
                            amount = (residual_amount * self.method_progress_factor) / month_days * days
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(date)['date_to'] - date).days + 1
                            amount = (residual_amount * self.method_progress_factor) / total_days * days
        return amount

    def compute_depreciation_list(self):
        self.ensure_one()

        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            amount_to_depr = residual_amount = self.value_residual

            # if we already have some previous validated entries, starting date is last entry + method period
            if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
                depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
            else:
                # depreciation_date computed from the purchase date
                depreciation_date = self.acquisition_date
                if self.first_depreciation_date and self.first_depreciation_date != self.acquisition_date:
                    depreciation_date = self.first_depreciation_date
                    # depreciation_date set manually from the 'first_depreciation_manual_date' field

            total_days = (depreciation_date.year % 4) and 365 or 366
            month_day = depreciation_date.day
            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)

            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr,
                                                    undone_dotation_number, posted_depreciation_line_ids,
                                                    total_days, depreciation_date)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': self.model_id.display_name,
                    'remaining_value': residual_amount,
                    'depreciated_value': self.book_value - (self.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date,
                }
                commands.append((0, False, vals))

                depreciation_date = depreciation_date + relativedelta(months=+int(self.method_period))

                # if month_day > 28 and self.date_first_depreciation == 'manual':
                #     max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                #     depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))

                # # datetime doesn't take into account that the number of days is not the same for each month
                # if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
                #     max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                #     depreciation_date = depreciation_date.replace(day=max_day_in_month)

        self.write({'depreciation_line_ids': commands})
        return True

    # @api.depends('depreciation_line_ids.move_id')
    # def _journal_entry_count(self):
    #     for asset in self:
    #         res = self.env['account.asset.depreciation.line'].search_count([('asset_id', '=', asset.id), ('move_id', '!=', False)])
    #         asset.entry_count = res or 0

    @api.depends('depreciation_line_ids.move_id', 'parent_id')
    def _entry_count(self):
        for asset in self:
            res = self.env['account.asset.depreciation.line'].search_count([('asset_id', '=', asset.id), ('move_id', '!=', False)])
            # res = self.env['account.move'].search_count([('asset_id', '=', asset.id), ('reversal_move_id', '=', False)])
            asset.depreciation_entries_count = res or 0
            asset.total_depreciation_entries_count = res or 0
            asset.gross_increase_count = len(asset.children_ids)

    def open_entries(self):
        move_ids = []
        for asset in self:
            for depreciation_line in asset.depreciation_line_ids:
                if depreciation_line.move_id:
                    move_ids.append(depreciation_line.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }
