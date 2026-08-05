from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.osv import expression
from json import dumps
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_customer_deposit = fields.Boolean('Subscription Customer Deposit?',
                                         default=False)
    transaction_type_id = fields.Many2one('account.transaction.type',
                                          'Transaction Type', ondelete='restrict', domain=lambda self:[('company_id','=',self.env.company.id)])
    subscription_id = fields.Many2one('sale.subscription', 'Subscription')
    # this field is used to add selection in payment
    state = fields.Selection(selection_add=[
        ('confirm', 'Confirm'), ('posted',)
    ], ondelete={'confirm': 'set default'})

    # add adjustment fields
    adjustment_ids = fields.One2many(
        'ar.adjustment', 'invoice_id',
        string='Adjustment Invoices')
    adjustment_amount = fields.Monetary(
        string='adjustment Amount', store=True,
        readonly=True, tracking=True,
        compute='_compute_adjustment_amount')
    ap_adjustment_ids = fields.One2many(
        'ap.adjustment', 'invoice_id',
        string='AP Adjustment Invoices')
    ap_adjustment_amount = fields.Monetary(
        string='AP adjustment Amount',
        readonly=True, tracking=True)
    voucher_no = fields.Char('Voucher Number', default='/', copy=False)
    account_ap_id = fields.Many2one(
        'account.account',
        string='Account Payable', copy=False)
    # ap_adjustment_amount = fields.Monetary(
    #     string='AP adjustment Amount', store=True,
    #     readonly=True, tracking=True,
    #     compute='_compute_adjustment_amount')

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('invoice_line_ids', []):
            lines = vals.get('invoice_line_ids', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                if vals.get('is_post_gen21', []):
                    line.update({'line_number': idx + 1})
                else:
                    line[2].update({'line_number': idx + 1})
        res = super(AccountMove, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(AccountMove, self).write(vals)
        # find invoice_line_ids, rewrite the line number
        for idx, line in enumerate(self.invoice_line_ids):
            line.line_number = idx + 1
        return res

    @api.constrains('voucher_no')
    def _check_voucher_no(self):
        """ constrains function to check the voucher number uniqueness """
        for rec in self:
            if rec.voucher_no and rec.voucher_no != '/':
                domain = [
                    ('voucher_no', '=ilike', rec.voucher_no),
                    ('id', '!=', rec.id),
                ]
                if self.search(domain):
                    raise ValidationError('Voucher Number already exists!')

    def name_get(self):
        result = []
        if self.env.context.get('show_view_search_invoice_payment_ref'):
            for record in self:
                if record.payment_reference:
                    data = str(record.payment_reference)
                    result.append((record.id, data))
            return result
        else:
            return super(AccountMove, self).name_get()

    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        draft_name = ''
        if self.state == 'draft':
            draft_name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.move_type]
            if not self.name or self.name == '/':
                draft_name += ' (* %s)' % str(self.id)
            else:
                draft_name += ' ' + self.name

        # Add payment_reference value to display name
        if self.payment_reference:
            payment_reference_name = '{} - '.format(self.payment_reference)
            draft_name = payment_reference_name + draft_name

        return (draft_name or self.name or '') + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('payment_reference', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.depends('adjustment_ids.adjustment_amount', 'adjustment_ids.state', 'ap_adjustment_ids.adjustment_amount', 'ap_adjustment_ids.state')
    def _compute_adjustment_amount(self):
        for record in self:
            if record.adjustment_ids:
                for rec in record.adjustment_ids:
                    # print(rec.state, 'isi berapa', record.adjustment_amount)
                    if rec and rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'additional':
                        # print(rec.state, '-', record.adjustment_amount)
                        record.adjustment_amount += rec.total_amount
                    if rec and rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'deduction':
                        record.adjustment_amount += (-1 * rec.total_amount)
                        # print(rec.state, '-', record.adjustment_amount)
                    elif rec and rec.state != 'posted':
                        record.adjustment_amount = 0
            # elif record.ap_adjustment_ids:
            #     for rec in record.ap_adjustment_ids:
            #         # print(rec.state, 'isi berapa', record.adjustment_amount)
            #         if rec and rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'deduction':
            #             # print(rec.state, '-', record.adjustment_amount)
            #             record.ap_adjustment_amount += rec.total_amount
            #         if rec and rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'additional':
            #             record.ap_adjustment_amount += (-1 * rec.total_amount)
            #             # print(rec.state, '-', record.adjustment_amount)
            #         elif rec and rec.state != 'posted':
            #             record.ap_adjustment_amount = 0

    @api.onchange('is_customer_deposit')
    def _onchange_is_customer_deposit(self):
        """ onchange function to add deposit product directly """
        lines = []
        if self.is_customer_deposit:
            param_product_id = self.env['ir.config_parameter'].sudo().get_param(
                'sale.default_deposit_product_id')
            deposit_product = self.env['product.product'].browse(int(param_product_id))
            if deposit_product:
                data = {
                    'product_id': deposit_product.id,
                    'name': deposit_product.name,
                    'account_id': deposit_product._get_product_accounts()['income'],
                    'currency_id': self.currency_id.id,
                }
                lines = [(0, 0, data)]
        else:  # empty the invoice lines
            lines = [(2, x.id) for x in self.invoice_line_ids]
        self.invoice_line_ids = lines
        self._onchange_invoice_line_ids()  # make sure it is called
        self._recompute_dynamic_lines(recompute_all_taxes=True,
                                      recompute_tax_base_amount=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ inherit onchange function to trigger account """
        res = super(AccountMove, self)._onchange_partner_id()
        self._onchange_transaction_type_id()  # call the onchange
        # whatever happens, if partner changes, the account stays the same
        if self.transaction_type_id:
            for line in self.line_ids:
                line.partner_id = self.partner_id.commercial_partner_id
                if line.account_id.user_type_id.type in ('receivable', 'payable'):
                    line.account_id = self.transaction_type_id.account_id
        if self.partner_id.property_account_payable_id:
            self.account_ap_id = self.partner_id.property_account_payable_id.id
        return res

    @api.onchange('transaction_type_id')
    def _onchange_transaction_type_id(self):
        """ onchange function to call _recompute_dynamic_lines() """
        # empty out line_ids having account_id.user_type_id.type = receivable
        self.line_ids = self.line_ids.filtered(
            lambda x: x.account_id.user_type_id.type != 'receivable')
        # force onchange and recompute
        self._onchange_invoice_line_ids()
        self._recompute_dynamic_lines(recompute_all_taxes=True,
                                      recompute_tax_base_amount=True)

    def _recompute_payment_terms_lines(self):
        ''' Compute the dynamic payment term lines of the journal entry.'''
        # HARD OVERRIDE
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    # note: if no transaction type and no account exists, usual
                    if not self.transaction_type_id and not self.transaction_type_id.account_id:
                        return self.partner_id.property_account_receivable_id
                    else:  # use the account from type
                        return self.transaction_type_id.account_id
                else:
                    return self.partner_id.property_account_payable_id
            else:
                # same logic as in the elif
                if not self.transaction_type_id and not self.transaction_type_id.account_id:
                    # Search new account.
                    domain = [
                        ('company_id', '=', self.company_id.id),
                        ('internal_type', '=',
                         'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                    ]
                    return self.env['account.account'].search(domain, limit=1)
                else:
                    return self.transaction_type_id.account_id

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date,
                                                                  currency=self.company_id.currency_id)
                if self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    return [(b[0], b[1], b[1]) for b in to_compute]
                else:
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date,
                                                                               currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                currency = self.journal_id.company_id.currency_id
                if currency and currency.is_zero(balance) and len(to_compute) > 1:
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                        'account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
            return new_terms_lines

        existing_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity

    # compute amount residual invoice when the invoice have adjustment value
    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        super(AccountMove, self)._compute_payments_widget_reconciled_info()
        for moves in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            # if the invoice have payment
            if payments_widget_vals['content']:
                # print(type(payments_widget_vals['content']), 'tipe content')
                # print(payments_widget_vals['content'], 'Isi content')
                moves.invoice_payments_widget = json.dumps(payments_widget_vals, default=date_utils.json_default)
                total_reconcile_amount = 0
                for amount in payments_widget_vals['content']:
                    # print(amount, 'adjustmet_amount')
                    total_reconcile_amount += amount['amount']
                if moves.adjustment_ids:
                    for rec in moves.adjustment_ids:
                        # print(rec, "record move adjustment")
                        if rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'deduction':
                            moves.amount_residual_signed = moves.amount_total_signed - \
                                                           ((-1 * rec.total_amount) + total_reconcile_amount)
                            moves.amount_residual = moves.amount_residual_signed
                        if rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'additional':
                            moves.amount_residual_signed = moves.amount_total_signed + \
                                                           (rec.total_amount + total_reconcile_amount)
                            moves.amount_residual = moves.amount_residual_signed
                        if rec.state == 'cancel' and rec.total_amount > 0 and rec.type_adjustment == 'deduction':
                            moves.amount_residual_signed = moves.amount_total_signed + \
                                                           ((-1 * rec.total_amount) + total_reconcile_amount)
                            moves.amount_residual = moves.amount_residual_signed
                        if rec.state == 'cancel' and rec.total_amount > 0 and rec.type_adjustment == 'additional':
                            moves.amount_residual_signed = moves.amount_total_signed - \
                                                           (rec.total_amount + total_reconcile_amount)
                            moves.amount_residual = moves.amount_residual_signed
            # if the invoice dont have payment
            else:
                moves.invoice_payments_widget = json.dumps(False)
                # print(moves.invoice_payments_widget, 'payment widgets')
                total_reconcile_amount = 0
                for amount in payments_widget_vals['content']:
                    total_reconcile_amount += amount['amount']
                if moves.adjustment_ids:
                    for rec in moves.adjustment_ids:
                        # print(rec, 'masuk perhitungan adjustment')
                        if rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'additional':
                            # print(rec, 'masuk posted additional')
                            moves.amount_residual_signed = moves.amount_total_signed + \
                                                           rec.total_amount - total_reconcile_amount
                            moves.amount_residual = moves.amount_residual_signed
                            for line in moves.line_ids:
                                if line.amount_residual > 0 or line.amount_residual_currency > 0:
                                    reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
                                                         - sum(line.matched_debit_ids.mapped('amount'))
                                    reconciled_amount_currency = sum(
                                        line.matched_credit_ids.mapped('debit_amount_currency')) \
                                                                 - sum(
                                        line.matched_debit_ids.mapped('credit_amount_currency'))
                                    line.amount_residual = line.balance + rec.total_amount - reconciled_balance
                                    if line.currency_id:
                                        line.amount_residual_currency = line.amount_currency + rec.total_amount \
                                                                        - reconciled_amount_currency
                        if rec.state == 'posted' and rec.total_amount > 0 and rec.type_adjustment == 'deduction':
                            # print(rec, 'masuk posted deduction')
                            moves.amount_residual_signed = moves.amount_total_signed + \
                                                           (-1 * rec.total_amount) + total_reconcile_amount
                            moves.amount_residual = moves.amount_residual_signed
                            for line in moves.line_ids:
                                if line.amount_residual > 0 or line.amount_residual_currency > 0:
                                    reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
                                                         - sum(line.matched_debit_ids.mapped('amount'))
                                    reconciled_amount_currency = sum(
                                        line.matched_credit_ids.mapped('debit_amount_currency')) \
                                                                 - sum(
                                        line.matched_debit_ids.mapped('credit_amount_currency'))
                                    line.amount_residual = line.balance - rec.total_amount - reconciled_balance
                                    if line.currency_id:
                                        line.amount_residual_currency = line.amount_currency - rec.total_amount \
                                                                        - reconciled_amount_currency
                        if rec.state in ('cancel', 'draft') \
                                and rec.total_amount > 0 \
                                and rec.type_adjustment == 'additional':
                            # print(rec, 'masuk additional')
                            moves.amount_residual_signed = moves.amount_total_signed + total_reconcile_amount
                            moves.amount_residual = moves.amount_residual_signed
                            for line in moves.line_ids:
                                if line.amount_residual > 0 or line.amount_residual_currency > 0:
                                    reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
                                                         - sum(line.matched_debit_ids.mapped('amount'))
                                    reconciled_amount_currency = sum(
                                        line.matched_credit_ids.mapped('debit_amount_currency')) \
                                                                 - sum(
                                        line.matched_debit_ids.mapped('credit_amount_currency'))
                                    line.amount_residual = line.balance - rec.total_amount - reconciled_balance
                                    if line.currency_id:
                                        line.amount_residual_currency = line.amount_currency - rec.total_amount \
                                                                        - reconciled_amount_currency
                        if rec.state in ('cancel', 'draft') \
                                and rec.total_amount > 0 \
                                and rec.type_adjustment == 'deduction':
                            # print(rec, 'masuk deduction')
                            moves.amount_residual_signed = moves.amount_total_signed + total_reconcile_amount
                            moves.amount_residual = moves.amount_residual_signed
                            for line in moves.line_ids:
                                if line.amount_residual > 0 or line.amount_residual_currency > 0:
                                    reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
                                                         - sum(line.matched_debit_ids.mapped('amount'))
                                    reconciled_amount_currency = sum(
                                        line.matched_credit_ids.mapped('debit_amount_currency')) \
                                                                 - sum(
                                        line.matched_debit_ids.mapped('credit_amount_currency'))
                                    line.amount_residual = line.balance + rec.total_amount - reconciled_balance
                                    if line.currency_id:
                                        line.amount_residual_currency = line.amount_currency + rec.total_amount \
                                                                        - reconciled_amount_currency

    def _compute_payments_widget_to_reconcile_info(self):
        super(AccountMove, self)._compute_payments_widget_to_reconcile_info()
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False
            # print(move.invoice_outstanding_credits_debits_widget, 'masuk payment widget reconcile')

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids \
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}
            # print(payments_widget_vals, 'masuk payment widget vals')

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True
            # print(move.invoice_outstanding_credits_debits_widget, 'masuk payment widget outstanding credit debit')

    # add action reverse invoice without cancel journal
    def action_invoice_reverse(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ins_accounting.action_view_account_invoice_reversal")

        if self.is_invoice():
            action['name'] = _('Reverse Invoice')
            action['refund_method'] = 'cancel'

        return action
