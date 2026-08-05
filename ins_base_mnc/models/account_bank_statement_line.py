from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = ['account.bank.statement.line', 'mail.thread', 'mail.activity.mixin']

    matched_misc_payment_ids = fields.Many2many('miscellaneous.miscellaneous',
                                                relation='bank_statement_line_matched_misc_payment_rel')
    multi_payment_reference = fields.Char('Payment References',
                                          compute='_compute_payment_references', inverse='_inverse_payment_references',
                                          store=True)
    cancel_reversal = fields.Boolean('Is Reversed', default=False)

    # @api.depends('move_id.line_ids', 'move_id.ref')
    # def _compute_reversed(self):
    #     """ compute function to get reversal journal """
    #     for move in self:
    #         reverse_move = self.env["account.move"].search([('reversed_entry_id', '=', move.move_id.id)], limit=1)
    #         if reverse_move:
    #             move.cancel_reversal = True
    #         else:
    #             move.cancel_reversal = False

    @api.depends('payment_ids')
    def _compute_payment_references(self):
        """ compute function to get multi_payment_reference """
        for rec in self:
            rec.multi_payment_reference = ', '.join(x.multi_payment_reference for x in rec.matched_payment_ids)

    def _inverse_payment_references(self):
        """ compute function to get multi_payment_reference """
        for rec in self:
            rec.multi_payment_reference = rec.multi_payment_reference

    def _get_reconcile_lines_vals_list(self):
        self.ensure_one()
        lines_vals_list = []
        # print(lines_vals_list, 'bank statement line oi reconciliation isinya apa')

        for payment in self.matched_payment_ids:
            liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()  # @UnusedVariable
            print(liquidity_lines, counterpart_lines, writeoff_lines)
            for line in liquidity_lines:
                lines_vals_list.append({'id': line._origin.id})

        for line in self.matched_move_line_ids:
            lines_vals_list.append({'id': line._origin.id})

        for line in self.matched_manual_ids:
            vals = {name: line[name] for name in
                    ['account_id', 'name', 'balance', 'partner_id', 'tax_ids', 'analytic_account_id',
                     'analytic_tag_ids', 'tax_repartition_line_id']}
            vals['balance'] = -vals['balance']
            vals = line._convert_to_write(vals)
            lines_vals_list.append(vals)

        for line in self.matched_misc_payment_ids:
            liquidity_lines, counterpart_lines, writeoff_lines = line._seek_for_lines()  # @UnusedVariable
            print(liquidity_lines, counterpart_lines, writeoff_lines)
            for line in liquidity_lines:
                # print (move_line,'move_line')
                lines_vals_list.append({'id': line._origin.id})
            # if line.receipt_type_id.category == 'misc':
            # for move_line in line._origin.move_id.line_ids:
            #     # print (move_line,'move_line')
            #     lines_vals_list.append({'id': move_line._origin.id})
            # for invoice in line._origin.invoice_ids:
            #     print(invoice,'invoice')
            #     if invoice.state == 'posted':
            #         for invoice_line in invoice.line_ids:
            #             # print(invoice_line,'invoice_line')
            #             lines_vals_list.append({'id': invoice_line._origin.id})
            #         # for line_move in invoice._origin.invoice_id.line_ids:
            #         #     print(line_move,'line_move')
            #         #     lines_vals_list.append({'id': line_move._origin.id})
            #     elif invoice.state != 'posted' and invoice.transaction_type == 'apply':
            #         raise UserError(
            #             _(
            #                 "You can only reconcile the miscellaneous with invoice state is posted."
            #             )
            #         )

        # print(lines_vals_list, 'isi line vals list di bank statement line')
        return lines_vals_list

    @api.depends('matched_payment_ids', 'matched_move_line_ids', 'matched_manual_ids', 'matched_misc_payment_ids')
    def _calc_matched_balance(self):
        for record in self:
            if not record.id:
                record.matched_balance = 0
                record.matched_balance_absolute = 0
                continue
            try:
                lines_vals_list = record._get_reconcile_lines_vals_list()
                # print(lines_vals_list, 'line vals list calc match balance')
                _, open_balance_vals = record._prepare_reconciliation(lines_vals_list,
                                                                      create_payment_for_invoice=record.create_payment_for_invoice)
                record.matched_balance = open_balance_vals and -open_balance_vals.get("amount_currency")
            except UserError:
                record.matched_balance = 0
            record.matched_balance_absolute = abs(record.matched_balance)

    def action_reconcile(self):
        self._onchange_matched_manual_ids(force_update=True)

        lines_vals_list = self._get_reconcile_lines_vals_list()
        # print (lines_vals_list,self.create_payment_for_invoice, 'line_vals_list action reconcile')
        self.with_context(create_payment_for_invoice=self.create_payment_for_invoice).reconcile(lines_vals_list)
        # print(lines_vals_list, 'action lines_vals_list bank statement')
        if self._context.get("reconcile_all_line"):
            return self.statement_id.action_reconcile(line_id=self)

        for line in self.matched_misc_payment_ids:
            # print(line, 'action reconcile bank statement')
            if line.invoice_ids:
                for applied in line.invoice_ids:
                    if applied.transaction_type == 'apply':
                        applied.action_reconcile()

    def action_unreconcile(self):
        self._onchange_matched_manual_ids(force_update=True)

    def action_reverse(self, fields=None):
        reverse_move = self.env["account.move"].search([('reversed_entry_id', '=', self.move_id.id)], limit=1)
        action = None
        if reverse_move:
            # self.move_id.mapped("line_ids").filtered(lambda x: x.account_id.reconcile).remove_move_reconcile()
            if not self.cancel_reversal:
                self.cancel_reversal = True
            else:
                raise UserError(_('This statment is reversed'))
        if not reverse_move:
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_view_account_move_reversal")
            reversed = self.env["account.move"].search([('reversed_entry_id', '=', self.move_id.id)], limit=1)
            if reversed and not self.cancel_reversal:
                self.cancel_reversal = True
            # action['default_active_ids'] = self.move_id.id
            # action['default_active_model'] = 'account.move'
            # action['default_move_ids'] = [(6, 0, [self.move_id.id])]

        return action

    def button_unreconcile_reverse(self):
        self.button_undo_reconciliation()
        reverse_move = self.env["account.move"].search([('reversed_entry_id', '=', self.move_id.id)], limit=1)
        action = None
        if not reverse_move:
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_view_account_move_reversal")
            self.move_id.mapped("line_ids").filtered(lambda x: x.account_id.reconcile).remove_move_reconcile()
            self.cancel_reversal = True
            # action['default_active_ids'] = self.move_id.id
            # action['default_active_model'] = 'account.move'
            # action['default_move_ids'] = [(6, 0, [self.move_id.id])]
        elif reverse_move:
            if not self.cancel_reversal:
                self.cancel_reversal = True
            else:
                raise UserError(_('This statment is reversed'))
        return action


    # code to inherit account suspense to outstanding payment account

    # -------------------------------------------------------------------------
    # RECONCILIATION METHODS
    # -------------------------------------------------------------------------

    def _prepare_reconciliation(self, lines_vals_list, create_payment_for_invoice=False):
        ''' Helper for the "reconcile" method used to get a full preview of the reconciliation result. This method is
        quite useful to deal with reconcile models or the reconciliation widget because it ensures the values seen by
        the user are exactly the values you get after reconciling.

        :param lines_vals_list:             See the 'reconcile' method.
        :param create_payment_for_invoice:  A flag indicating the statement line must create payments on the fly during
                                            the reconciliation.
        :return: The diff to be applied on the statement line as a tuple
        (
            lines_to_create:    The values to create the account.move.line on the statement line.
            payments_to_create: The values to create the account.payments.
            open_balance_vals:  A dictionary to create the open-balance line or None if the reconciliation is full.
            existing_lines:     The counterpart lines to which the reconciliation will be done.
        )
        '''

        self.ensure_one()

        liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()
        print(liquidity_lines, suspense_lines, other_lines, 'prepare_reconciliation')
        # Ensure the statement line has not yet been already reconciled.
        # If the move has 'to_check' enabled, it means the statement line has created some lines that
        # need to be checked later and replaced by the real ones.
        if not self.move_id.to_check and other_lines:
            raise UserError(_("The statement line has already been reconciled."))

        # A list of dictionary containing:
        # - line_vals:          The values to create the account.move.line on the statement line.
        # - payment_vals:       The optional values to create a bridge account.payment
        # - counterpart_line:   The optional counterpart line to reconcile with 'line'.
        reconciliation_overview = []

        total_balance = liquidity_lines.balance

        # Step 1: Split 'lines_vals_list' into two batches:
        # - The existing account.move.lines that need to be reconciled with the statement line.
        #       => Will be managed at step 2.
        # - The account.move.lines to be created from scratch.
        #       => Will be managed directly.

        to_browse_ids = []
        to_process_vals = []
        for vals in lines_vals_list:
            # Don't modify the params directly.
            vals = dict(vals)

            if 'id' in vals:
                # Existing account.move.line.
                to_browse_ids.append(vals.pop('id'))
                to_process_vals.append(vals)
            else:
                # Newly created account.move.line from scratch.
                line_vals = self._prepare_counterpart_move_line_vals(vals)
                total_balance += line_vals['debit'] - line_vals['credit']

                reconciliation_overview.append({
                    'line_vals': line_vals,
                })

        # Step 2: Browse counterpart lines all in one and process them.

        existing_lines = self.env['account.move.line'].browse(to_browse_ids)
        for line, counterpart_vals in zip(existing_lines, to_process_vals):
            line_vals = self._prepare_counterpart_move_line_vals(counterpart_vals, move_line=line)
            balance = line_vals['debit'] - line_vals['credit']

            reconciliation_vals = {
                'line_vals': line_vals,
                'counterpart_line': line,
            }

            if create_payment_for_invoice and line.account_internal_type in ('receivable', 'payable'):

                # Prepare values to create a new account.payment.
                payment_vals = self.env['account.payment.register'] \
                    .with_context(active_model='account.move.line', active_ids=line.ids) \
                    .create({
                    'amount': abs(line_vals['amount_currency']) if line_vals['currency_id'] else abs(balance),
                    'payment_date': self.date,
                    'payment_type': 'inbound' if balance < 0.0 else 'outbound',
                    'journal_id': self.journal_id.id,
                    'currency_id': (self.foreign_currency_id or self.currency_id).id,
                }) \
                    ._create_payment_vals_from_wizard()

                if payment_vals['payment_type'] == 'inbound':
                    liquidity_account = self.journal_id.payment_debit_account_id
                else:
                    liquidity_account = self.journal_id.payment_credit_account_id

                # Preserve the rate of the statement line.
                payment_vals['line_ids'] = [
                    # Receivable / Payable line.
                    (0, 0, {
                        **line_vals,
                    }),

                    # Liquidity line.
                    (0, 0, {
                        **line_vals,
                        'amount_currency': -line_vals['amount_currency'],
                        'debit': line_vals['credit'],
                        'credit': line_vals['debit'],
                        'account_id': liquidity_account.id,
                    }),
                ]

                # if payment_vals:
                #     raise Exception("Sorry, masuk di account --> bank statement isinya apa")
                # Prepare the line to be reconciled with the payment.
                if payment_vals['payment_type'] == 'inbound':
                    # Receive money.
                    line_vals['account_id'] = self.journal_id.payment_debit_account_id.id
                elif payment_vals['payment_type'] == 'outbound':
                    # Send money.
                    line_vals['account_id'] = self.journal_id.payment_credit_account_id.id

                reconciliation_vals['payment_vals'] = payment_vals

            reconciliation_overview.append(reconciliation_vals)

            total_balance += balance

        # Step 3: If the journal entry is not yet balanced, create an open balance.

        if self.company_currency_id.round(total_balance):
            if self.amount > 0:
                open_balance_account = self.partner_id.with_company(self.company_id).property_account_receivable_id
            else:
                open_balance_account = self.partner_id.with_company(self.company_id).property_account_payable_id

            open_balance_vals = self._prepare_counterpart_move_line_vals({
                'name': '%s: %s' % (self.payment_ref, _('Open Balance')),
                'account_id': open_balance_account.id,
                'balance': -total_balance,
                'currency_id': self.company_currency_id.id,
            })
        else:
            open_balance_vals = None

        return reconciliation_overview, open_balance_vals

    def reconcile(self, lines_vals_list, to_check=False):
        ''' Perform a reconciliation on the current account.bank.statement.line with some
        counterpart account.move.line.
        If the statement line entry is not fully balanced after the reconciliation, an open balance will be created
        using the partner.

        :param lines_vals_list: A list of python dictionary containing:
            'id':               Optional id of an existing account.move.line.
                                For each line having an 'id', a new line will be created in the current statement line.
            'balance':          Optional amount to consider during the reconciliation. If a foreign currency is set on the
                                counterpart line in the same foreign currency as the statement line, then this amount is
                                considered as the amount in foreign currency. If not specified, the full balance is taken.
                                This value must be provided if 'id' is not.
            **kwargs:           Custom values to be set on the newly created account.move.line.
        :param to_check:        Mark the current statement line as "to_check" (see field for more details).
        '''
        self.ensure_one()
        liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()

        reconciliation_overview, open_balance_vals = self._prepare_reconciliation(lines_vals_list)

        # ==== Manage res.partner.bank ====

        if self.account_number and self.partner_id and not self.partner_bank_id:
            self.partner_bank_id = self._find_or_create_bank_account()

        # ==== Check open balance ====

        if open_balance_vals:
            if not open_balance_vals.get('partner_id'):
                raise UserError(_("Unable to create an open balance for a statement line without a partner set."))
            if not open_balance_vals.get('account_id'):
                raise UserError(_("Unable to create an open balance for a statement line because the receivable "
                                  "/ payable accounts are missing on the partner."))

        # ==== Create & reconcile payments ====
        # When reconciling to a receivable/payable account, create an payment on the fly.

        pay_reconciliation_overview = [reconciliation_vals
                                       for reconciliation_vals in reconciliation_overview
                                       if reconciliation_vals.get('payment_vals')]
        if pay_reconciliation_overview:
            payment_vals_list = [reconciliation_vals['payment_vals'] for reconciliation_vals in
                                 pay_reconciliation_overview]
            payments = self.env['account.payment'].create(payment_vals_list)

            payments.action_post()

            for reconciliation_vals, payment in zip(pay_reconciliation_overview, payments):
                reconciliation_vals['payment'] = payment

                # Reconcile the newly created payment with the counterpart line.
                (reconciliation_vals['counterpart_line'] + payment.line_ids) \
                    .filtered(lambda line: line.account_id == reconciliation_vals['counterpart_line'].account_id) \
                    .reconcile()

        # ==== Create & reconcile lines on the bank statement line ====

        to_create_commands = [(0, 0, open_balance_vals)] if open_balance_vals else []
        to_delete_commands = [(2, line.id) for line in suspense_lines + other_lines]

        # Cleanup previous lines.
        self.move_id.with_context(check_move_validity=False, skip_account_move_synchronization=True,
                                  force_delete=True).write({
            'line_ids': to_delete_commands + to_create_commands,
            'to_check': to_check,
        })

        line_vals_list = [reconciliation_vals['line_vals'] for reconciliation_vals in reconciliation_overview]
        new_lines = self.env['account.move.line'].create(line_vals_list)
        for reconciliation_vals, line in zip(reconciliation_overview, new_lines):
            if reconciliation_vals.get('payment'):
                accounts = (self.journal_id.payment_debit_account_id, self.journal_id.payment_credit_account_id)
                counterpart_line = reconciliation_vals['payment'].line_ids.filtered(
                    lambda line: line.account_id in accounts)
            elif reconciliation_vals.get('counterpart_line'):
                counterpart_line = reconciliation_vals['counterpart_line']
            else:
                continue

            (line + counterpart_line).reconcile()

            # Update the payment date to match the current bank statement line's date.
            if counterpart_line.payment_id:
                counterpart_line.payment_id.reconciliation_date = self.date

    @api.depends('currency_id', 'amount', 'foreign_currency_id', 'amount_currency',
                 'move_id.line_ids', 'move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_is_reconciled(self):
        ''' Compute the field indicating if the statement lines are already reconciled with something.
        This field is used for display purpose (e.g. display the 'cancel' button on the statement lines).
        Also computes the residual amount of the statement line.
        '''
        for st_line in self:
            liquidity_lines, suspense_lines, other_lines = st_line._seek_for_lines()
            # print(liquidity_lines, suspense_lines, other_lines,'isi suspense di computed reconcile bank statment',st_line)
            # Compute is_reconciled
            if not st_line.id:
                # New record: The journal items are not yet there.
                st_line.is_reconciled = False
            elif suspense_lines:
                # In case of the statement line comes from an older version, it could have a residual amount of zero.
                st_line.is_reconciled = all(suspense_line.reconciled for suspense_line in suspense_lines)
            elif st_line.currency_id.is_zero(st_line.amount):
                st_line.is_reconciled = True
            else:
                # The journal entry seems reconciled.
                if self.statement_id.state == 'open':
                    st_line.is_reconciled = False
                elif self.move_id and self.statement_id.state == 'posted':
                    for move_line in self.move_id.line_ids:
                        if move_line.reconciled and move_line.account_id != liquidity_lines:
                            st_line.is_reconciled = True
                elif self.move_id and self.statement_id.state == 'posted':
                    for move_line in self.move_id.line_ids:
                        if not move_line.reconciled and move_line.account_id != liquidity_lines:
                            st_line.is_reconciled = False
                else:
                    print('masuk else paling akhir karena ndak ketemu semua kondisi')
                    # st_line.is_reconciled = True

            # Compute residual amount
            if st_line.to_check:
                st_line.amount_residual = -st_line.amount_currency if st_line.foreign_currency_id else -st_line.amount
            elif suspense_lines.account_id.reconcile:
                st_line.amount_residual = sum(suspense_lines.mapped('amount_residual_currency'))
            else:
                st_line.amount_residual = sum(suspense_lines.mapped('amount_currency'))

    def _seek_for_lines(self):
        # res = super(AccountBankStatementLine, self)._seek_for_lines()

        liquidity_lines = self.env['account.move.line']
        suspense_lines = self.env['account.move.line']
        other_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            print('suspense', line.account_id, self.journal_id.suspense_payment_account_id,
                  self.journal_id.suspense_account_id)
            if line.account_id == self.journal_id.default_account_id:
                liquidity_lines += line
            elif line.account_id == self.journal_id.suspense_payment_account_id \
                    or line.account_id == self.journal_id.suspense_account_id:
                suspense_lines += line
            else:
                other_lines += line
        return liquidity_lines, suspense_lines, other_lines
        # return res

    @api.model
    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        self.ensure_one()
        if not counterpart_account_id:
            if self.payment_ids:
                print(self.payment_ids)
                for payments in self.payment_ids:
                    if payments.payment_type == 'outbound':
                        counterpart_account_id = self.journal_id.suspense_payment_account_id.id
                    elif payments.payment_type == 'inbound':
                        counterpart_account_id = self.journal_id.suspense_account_id.id
            if self.matched_misc_payment_ids:
                for misc in self.matched_misc_payment_ids:
                    if misc.misc_type == 'payment':
                        counterpart_account_id = self.journal_id.suspense_payment_account_id.id
                    elif misc.misc_type == 'receive':
                        counterpart_account_id = self.journal_id.suspense_account_id.id
            else:
                # counterpart_account_id = self.journal_id.suspense_account_id.id
                counterpart_account_id = self.journal_id.suspense_payment_account_id.id \
                    if self.amount < 0 else self.journal_id.suspense_account_id.id

        if not counterpart_account_id:
            raise UserError(_(
                "You can't create a new statement line without a suspense account set on the %s journal."
            ) % self.journal_id.display_name)

        liquidity_line_vals = self._prepare_liquidity_move_line_vals()

        # Ensure the counterpart will have a balance exactly equals to the amount in journal currency.
        # This avoid some rounding issues when the currency rate between two currencies is not symmetrical.
        # E.g:
        # A.convert(amount_a, B) = amount_b
        # B.convert(amount_b, A) = amount_c != amount_a

        counterpart_vals = {
            'name': self.payment_ref,
            'account_id': counterpart_account_id,
            'amount_residual': liquidity_line_vals['debit'] - liquidity_line_vals['credit'],
        }

        if self.foreign_currency_id and self.foreign_currency_id != self.company_currency_id:
            # Ensure the counterpart will have exactly the same amount in foreign currency as the amount set in the
            # statement line to avoid some rounding issues when making a currency conversion.

            counterpart_vals.update({
                'currency_id': self.foreign_currency_id.id,
                'amount_residual_currency': self.amount_currency,
            })
        elif liquidity_line_vals['currency_id']:
            # Ensure the counterpart will have a balance exactly equals to the amount in journal currency.
            # This avoid some rounding issues when the currency rate between two currencies is not symmetrical.
            # E.g:
            # A.convert(amount_a, B) = amount_b
            # B.convert(amount_b, A) = amount_c != amount_a

            counterpart_vals.update({
                'currency_id': liquidity_line_vals['currency_id'],
                'amount_residual_currency': liquidity_line_vals['amount_currency'],
            })

        counterpart_line_vals = self._prepare_counterpart_move_line_vals(counterpart_vals)
        return [liquidity_line_vals, counterpart_line_vals]
        # end of inherit account suspense to account outstanding payment.
