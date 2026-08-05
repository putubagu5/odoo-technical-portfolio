import calendar
from dateutil.relativedelta import relativedelta
from math import copysign
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    atis_number = fields.Char('ATIS Number')
    amount_depreciated = fields.Monetary('Depreciated Amount',
                                         compute='_compute_amount_depreciated')

    @api.depends('depreciation_line_ids')
    def _compute_amount_depreciated(self):
        """ compute function to calculate amount_depreciated """
        for rec in self:
            posted = rec.depreciation_line_ids.filtered(lambda x: x.move_id.state == 'posted')
            value = sum(posted[-1].mapped('depreciated_value')) if posted else 0.0
            rec.amount_depreciated = value

    @api.depends('value_residual', 'salvage_value', 'children_ids.book_value',
                 'depreciation_line_ids', 'amount_add', 'amount_depreciated',
                 'already_depreciated_amount_import')
    def _compute_book_value(self):
        """ override function to set book_value """
        for record in self:
            posted = record.depreciation_line_ids.filtered(lambda x: x.move_id.state == 'posted')
            book_value = sum(posted[-1].mapped('remaining_value')) if posted else 0.0

            # NOTE: use original_value if no posted found
            book_value = sum(posted[-1].mapped('remaining_value')) if posted else record.original_value
            # record.book_value = book_value + record.amount_add - record.already_depreciated_amount_import
            # record.gross_increase_value = sum(record.children_ids.mapped('original_value'))

            # Update part
            amt_posted = sum(posted.mapped('amount'))
            record.book_value = record.original_value - record.already_depreciated_amount_import - amt_posted
            record.gross_increase_value = sum(record.children_ids.mapped('original_value'))

    @api.depends(
        'original_value', 'salvage_value', 'already_depreciated_amount_import',
        'depreciation_move_ids.state', 'depreciation_move_ids.amount_untaxed',
        'depreciation_move_ids.reversal_move_id', 'amount_add',
        'depreciation_line_ids'
    )
    def _compute_value_residual(self):
        """ override function to set value_residual """
        for record in self:
            posted = record.depreciation_line_ids.filtered(lambda x: x.move_id.state == 'posted')
            # value_residual = sum(posted[-1].mapped('remaining_value')) if posted else 0.0

            # NOTE: use original_value if no posted found
            value_residual = sum(posted[-1].mapped('remaining_value')) if posted else record.original_value
            record.value_residual = value_residual + record.amount_add
            # posted = record.depreciation_move_ids.filtered(
            #     lambda m: m.state == 'posted' and not m.reversal_move_id
            # )
            # record.value_residual = (
            #     record.original_value
            #     - record.salvage_value
            #     - record.already_depreciated_amount_import
            #     - sum(move._get_depreciation() for move in posted)
            #     + record.amount_add
            # )

    @api.onchange('depreciation_move_ids')
    def _onchange_depreciation_move_ids(self):
        seq = 0
        asset_remaining_value = self.original_value - self.already_depreciated_amount_import
        cumulated_depreciation = 0
        for m in self.depreciation_move_ids.sorted(lambda x: x.date):
            seq += 1
            if not m.reversal_move_id:
                asset_remaining_value -= m.amount_untaxed
                cumulated_depreciation += m.amount_untaxed
            if not m.asset_manually_modified:
                continue
            m.asset_manually_modified = False
            m.asset_remaining_value = asset_remaining_value
            m.asset_depreciated_value = cumulated_depreciation
            for older_move in self.depreciation_move_ids.sorted(lambda x: x.date)[seq:]:
                if not older_move.reversal_move_id:
                    asset_remaining_value -= older_move.amount_untaxed
                    cumulated_depreciation += older_move.amount_untaxed
                older_move.asset_remaining_value = asset_remaining_value
                older_move.asset_depreciated_value = cumulated_depreciation

    def compute_depreciation_board(self):
        self.ensure_one()
        amount_change_ids = self.depreciation_move_ids.filtered(lambda x: x.asset_value_change and not x.reversal_move_id).sorted(key=lambda l: l.date)
        posted_depreciation_move_ids = self.depreciation_move_ids.filtered(lambda x: x.state == 'posted' and not x.asset_value_change and not x.reversal_move_id).sorted(key=lambda l: l.date)
        already_depreciated_amount = sum([m.amount_untaxed for m in posted_depreciation_move_ids])
        depreciation_number = self.method_number
        if self.prorata:
            depreciation_number += 1
        starting_sequence = 0
        amount_to_depreciate = self.value_residual + sum([m.amount_untaxed for m in amount_change_ids])
        depreciation_date = self.first_depreciation_date
        # if we already have some previous validated entries, starting date is last entry + method period
        if posted_depreciation_move_ids and posted_depreciation_move_ids[-1].date:
            last_depreciation_date = fields.Date.from_string(posted_depreciation_move_ids[-1].date)
            if last_depreciation_date > depreciation_date:  # in case we unpause the asset
                depreciation_date = last_depreciation_date + relativedelta(months=+int(self.method_period))
        commands = [(2, line_id.id, False) for line_id in self.depreciation_move_ids.filtered(lambda x: x.state == 'draft')]
        newlines = self._recompute_board(depreciation_number, starting_sequence, amount_to_depreciate, depreciation_date, already_depreciated_amount, amount_change_ids)
        newline_vals_list = []
        for newline_vals in newlines:
            # no need of amount field, as it is computed and we don't want to trigger its inverse function
            del(newline_vals['amount_total'])
            newline_vals_list.append(newline_vals)
        new_moves = self.env['account.move'].create(newline_vals_list)
        for move in new_moves:
            commands.append((4, move.id))
        return self.write({'depreciation_move_ids': commands})

    def _recompute_board(self, depreciation_number, starting_sequence, amount_to_depreciate, depreciation_date, already_depreciated_amount, amount_change_ids):
        self.ensure_one()
        residual_amount = amount_to_depreciate
        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        move_vals = []
        prorata = self.prorata and not self.env.context.get("ignore_prorata")
        if amount_to_depreciate != 0.0:
            for asset_sequence in range(starting_sequence + 1, depreciation_number + 1):
                depreciation_date = self.first_depreciation_date
                while amount_change_ids and amount_change_ids[0].date <= depreciation_date:
                    if not amount_change_ids[0].reversal_move_id:
                        residual_amount -= amount_change_ids[0].amount_untaxed
                        amount_to_depreciate -= amount_change_ids[0].amount_untaxed
                        already_depreciated_amount += amount_change_ids[0].amount_untaxed
                    amount_change_ids[0].write({
                        'asset_remaining_value': float_round(residual_amount, precision_rounding=self.currency_id.rounding),
                        'asset_depreciated_value': amount_to_depreciate - residual_amount + already_depreciated_amount,
                    })
                    amount_change_ids -= amount_change_ids[0]
                amount = self._compute_board_amount(asset_sequence, residual_amount, amount_to_depreciate, depreciation_number, starting_sequence, depreciation_date)
                prorata_factor = 1
                move_ref = self.name + ' (%s/%s)' % (prorata and asset_sequence - 1 or asset_sequence, self.method_number)
                if prorata and asset_sequence == 1:
                    move_ref = self.name + ' ' + _('(prorata entry)')
                    first_date = self.prorata_date
                    if int(self.method_period) % 12 != 0:
                        month_days = calendar.monthrange(first_date.year, first_date.month)[1]
                        days = month_days - first_date.day + 1
                        prorata_factor = days / month_days
                    else:
                        total_days = (depreciation_date.year % 4) and 365 or 366
                        days = (self.company_id.compute_fiscalyear_dates(first_date)['date_to'] - first_date).days + 1
                        prorata_factor = days / total_days
                amount = self.currency_id.round(amount * prorata_factor)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount

                move_vals.append(self.env['account.move']._prepare_move_for_asset_depreciation({
                    'amount': amount,
                    'asset_id': self,
                    'move_ref': move_ref,
                    'date': depreciation_date,
                    'asset_remaining_value': float_round(residual_amount, precision_rounding=self.currency_id.rounding),
                    'asset_depreciated_value': amount_to_depreciate - residual_amount + already_depreciated_amount,
                }))

                depreciation_date = depreciation_date + relativedelta(months=+int(self.method_period))
                # datetime doesn't take into account that the number of days is not the same for each month
                if int(self.method_period) % 12 != 0:
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)
        return move_vals

    def pause(self, pause_date):
        """ Sets an 'open' asset in 'paused' state, generating first a depreciation
        line corresponding to the ratio of time spent within the current depreciation
        period before putting the asset in pause. This line and all the previous
        unposted ones are then posted.
        """
        self.ensure_one()

        all_lines_before_pause = self.depreciation_move_ids.filtered(lambda x: x.date <= pause_date)
        line_before_pause = all_lines_before_pause and max(all_lines_before_pause, key=lambda x: x.date)
        following_lines = self.depreciation_move_ids.filtered(lambda x: x.date > pause_date)
        if following_lines:
            if any(line.state == 'posted' for line in following_lines):
                raise UserError(_("You cannot pause an asset with posted depreciation lines in the future."))

            if self.prorata:
                first_following = min(following_lines, key=lambda x: x.date)
                depreciation_period_start = line_before_pause and line_before_pause.date or self.prorata_date or self.first_depreciation_date
                try:
                    time_ratio = ((pause_date - depreciation_period_start).days) / (first_following.date - depreciation_period_start).days
                    new_line = self._insert_depreciation_line(line_before_pause, first_following.amount_untaxed * time_ratio, _("Asset paused"), pause_date)
                    if pause_date <= fields.Date.today():
                        new_line._post()
                except ZeroDivisionError:
                    pass

            self.write({'state': 'paused'})
            self.depreciation_move_ids.filtered(lambda x: x.state == 'draft').unlink()
            self.message_post(body=_("Asset paused"))
        else:
            raise UserError(_("Trying to pause an asset without any future depreciation line"))

    def _get_disposal_moves(self, invoice_line_ids, disposal_date):
        def get_line(asset, amount, account):
            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'analytic_account_id': account_analytic_id.id if asset.asset_type == 'sale' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type == 'sale' else False,
                'currency_id': current_currency.id,
                'amount_currency': -asset.value_residual,
            })

        move_ids = []
        assert len(self) == len(invoice_line_ids)
        for asset, invoice_line_id in zip(self, invoice_line_ids):
            posted_moves = asset.depreciation_move_ids.filtered(lambda x: (
                not x.reversal_move_id
                and x.state == 'posted'
            ))
            if posted_moves and disposal_date < max(posted_moves.mapped('date')):
                if invoice_line_id:
                    raise UserError('There are depreciation posted after the invoice date (%s).\nPlease revert them or change the date of the invoice.' % disposal_date)
                else:
                    raise UserError('There are depreciation posted in the future, please revert them.')
            account_analytic_id = asset.account_analytic_id
            analytic_tag_ids = asset.analytic_tag_ids
            company_currency = asset.company_id.currency_id
            current_currency = asset.currency_id
            prec = company_currency.decimal_places
            unposted_depreciation_move_ids = asset.depreciation_move_ids.filtered(lambda x: x.state == 'draft')

            old_values = {
                'method_number': asset.method_number,
            }

            # Remove all unposted depr. lines
            commands = [(2, line_id.id, False) for line_id in unposted_depreciation_move_ids]

            # Create a new depr. line with the residual amount and post it
            asset_sequence = len(asset.depreciation_move_ids) - len(unposted_depreciation_move_ids) + 1
            initial_amount = asset.original_value
            initial_account = asset.original_move_line_ids.account_id if len(asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id
            depreciation_moves = asset.depreciation_line_ids.filtered(lambda r:r.move_check == True and r.move_posted_check == True )
            depreciated_amount = -sum(depreciation_moves.mapped('amount'))
            # depreciation_moves = asset.depreciation_move_ids.filtered(lambda r: r.state == 'posted' and not (r.reversal_move_id and r.reversal_move_id[0].state == 'posted'))
            # depreciated_amount = copysign(
            #     sum(depreciation_moves.mapped('amount_untaxed')) + asset.already_depreciated_amount_import,
            #     -initial_amount,
            # )
            depreciation_account = asset.account_depreciation_id
            invoice_amount = copysign(invoice_line_id.price_subtotal, -initial_amount)
            invoice_account = invoice_line_id.account_id
            difference = -initial_amount - depreciated_amount - invoice_amount
            difference_account = asset.company_id.gain_account_id if difference > 0 else asset.company_id.loss_account_id
            line_datas = [(initial_amount, initial_account), (depreciated_amount, depreciation_account), (invoice_amount, invoice_account), (difference, difference_account)]
            if not invoice_line_id:
                del line_datas[2]
            vals = {
                'asset_id': asset.id,
                'ref': asset.name + ': ' + (_('Disposal') if not invoice_line_id else _('Sale')),
                'asset_remaining_value': 0,
                'asset_depreciated_value': max(asset.depreciation_move_ids.filtered(lambda x: x.state == 'posted'), key=lambda x: x.date, default=self.env['account.move']).asset_depreciated_value,
                'date': disposal_date,
                'journal_id': asset.journal_id.id,
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            }
            commands.append((0, 0, vals))
            asset.write({'depreciation_move_ids': commands, 'method_number': asset_sequence})
            tracked_fields = self.env['account.asset'].fields_get(['method_number'])
            changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
            if changes:
                asset.message_post(body=_('Asset sold or disposed. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)
            move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids

        return move_ids
