from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AppliedInvoices(models.Model):
    _name = 'applied.invoices'
    _description = 'Applied Misc To Invoice'
    _inherits = {'account.move': 'move_id'}
    _order = "date desc, name desc"
    _check_company_auto = True

    def get_misc_id(self):
        active_id = self.env.context.get('active_ids', False)
        if active_id:
            print(active_id, 'active_id')
            return self.env['applied.invoices'].browse(active_id)

    misc_id = fields.Many2one(
        'miscellaneous.miscellaneous',
        string='Receipt', required=True,
        ondelete='cascade',
        domain="[('id', '=', active_id)]")
    misc_type = fields.Selection(selection=[
        ('receive', 'Miscellaneous Receipt'),
        ('payment', 'Miscellaneous Payment')],
        related='misc_id.misc_type',
        string='Receipt Type')
    misc_partner_id = fields.Many2one(
        'res.partner', string="Partner Name",
        related='misc_id.misc_partner_id', copy=False)
    misc_currency_id = fields.Many2one(
        'res.currency', string='Misc Receipt Currency',
        related='misc_id.currency_id')
    misc_remaining_amount = fields.Monetary(
        currency_field='misc_currency_id',
        related='misc_id.remaining_amount',
        readonly=True,
        string='Remaining Amount Applied')
    journal_id = fields.Many2one(
        'account.journal', store=True,
        readonly=False, required=True,
        domain="[('company_id', '=', company_id)]")
    company_id = fields.Many2one(
        string='Company', store=True, readonly=True,
        related='misc_id.company_id', change_default=True,
        default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit", domain="[('user_ids', '=', uid)]",
        related='misc_id.operating_unit_id'
    )
    invoice_id = fields.Many2one(
        comodel_name='account.move', required=True,
        string='Customer Invoice')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='invoice_id.partner_id',
        string='Customer Invoice')
    invoice_currency_id = fields.Many2one(
        'res.currency', string='Invoice Currency',
        readonly=True, related='invoice_id.currency_id')
    invoice_amount = fields.Monetary(
        currency_field='invoice_currency_id',
        related='invoice_id.amount_residual',
        string="Amount Due",
        readonly=True, default=0)
    invoice_amount_residual = fields.Monetary(
        currency_field='invoice_currency_id',
        string="Invoice Amount Due", compute='_compute_amount_remaining', store=True,
        readonly=False, default=0)
    amount_remaining = fields.Monetary(
        'Remaining Amount Due', currency_field='invoice_currency_id',
        compute='_compute_amount_remaining')
    transaction_type = fields.Selection([
        ('apply', 'Applied to Invoice'), ('unapply', 'Un-Apply Invoice')],
        string='Transaction Type',
        copy=False, default='unapply', index=True)
    transaction_date = fields.Datetime(
        'Transaction Date',
        required=True,
        default=fields.Datetime.now)
    applied_amount = fields.Monetary(
        currency_field='misc_currency_id',
        string="Applied Amount",
        required=True, default=0)
    applied_amount_currency = fields.Monetary(
        string="Applied Amount(foreign currency)",
        store=True, copy=False,
        compute='_compute_applied_amount_currency',
        currency_field='invoice_currency_id')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        readonly=True, required=True, ondelete='cascade',
        check_company=True)
    manual_currency_rate_active = fields.Boolean(string='Apply Manual Exchange',
                                                 related='misc_id.manual_currency_rate_active')
    manual_currency_rate = fields.Float('Rate', digits=(12, 4), related='misc_id.manual_currency_rate')

    # == Payment difference fields ==
    payment_difference = fields.Monetary(
        string='Payment Difference', copy=False, default=0.0)
    payment_difference_handling = fields.Selection([
        ('open', 'Keep open'),
        ('reconcile', 'Mark as fully paid'),
    ], default='open', string="Payment Difference Handling")
    writeoff_account_id = fields.Many2one(
        'account.account', string="Difference Account", copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    writeoff_label = fields.Char(
        string='Journal Item Label', default='Write-Off',
        help='Change label of the counterpart that will hold the payment difference')

    _sql_constraints = [
        (
            'unique_applied_invoice', 'unique (misc_id, invoice_id,transaction_type)',
            'Applied Invoice is already exists!')
    ]

    @api.constrains('misc_id', 'invoice_id', 'transaction_type', 'id')
    def _check_invoice_unique(self):
        invoices = []
        for record in self:
            invoice = self.env['applied.invoices'].search([('misc_id', '=', record.misc_id.id),
                                                           ('invoice_id', '=', record.invoice_id.id),
                                                           ('transaction_type', '=', 'unapply'),
                                                           ('state', '=', 'draft')])
            invoices.append(invoice.invoice_id.id)
        for rec in self:
            jumlah = invoices.count(rec.invoice_id.id)
            total_count = self.search_count([('misc_id', '=', rec.misc_id.id), ('invoice_id', '=', rec.invoice_id.id),
                                             ('transaction_type', '=', 'unapply'), ('state', '=', 'draft')])
            total_post_count = self.search_count(
                [('misc_id', '=', rec.misc_id.id), ('invoice_id', '=', rec.invoice_id.id),
                 ('transaction_type', '=', 'apply'), ('state', '=', 'posted')])
            print(jumlah, 'sama', total_count, 'sama', total_post_count, rec.state)
            if total_count > 1 or jumlah > 1 or total_post_count > 1:
                print(rec.invoice_id.id, 'jumlah', total_count)
                raise ValidationError("Invoice number %s already exists!" % rec.invoice_id.payment_reference)

    # calculate difference applied amount with invoice amount
    # @api.depends('applied_amount')
    # def _compute_payment_difference(self):
    #     self.payment_difference = 0
    #     print('masuk payment difference wizard')
    #     for record in self:
    #         if record.applied_amount != record.invoice_amount:
    #             if record.misc_currency_id == record.invoice_currency_id:
    #                 # Same currency.
    #                 record.payment_difference = record.invoice_amount - record.applied_amount
    #             elif record.misc_currency_id == record.company_id.currency_id == record.invoice_currency_id:
    #                 # Payment expressed on the company's currency.
    #                 record.payment_difference = record.invoice_amount - record.applied_amount
    #             else:
    #                 # Foreign currency on payment different than the one set on the journal entries.
    #                 amount_payment_currency = record.company_id.currency_id._convert(record.invoice_amount,
    #                                                                                  record.invoice_currency_id,
    #                                                                                  record.company_id,
    #                                                                                  record.transaction_date)
    #                 record.payment_difference = amount_payment_currency - record.applied_amount

    @api.onchange('applied_amount', 'invoice_amount_residual')
    def _compute_amount_remaining(self):
        """ compute function to calculate amount_remaining """
        for rec in self:
            if rec.move_id and rec.state != 'posted':
                print(rec.invoice_amount_residual, rec.state, )
                rec.amount_remaining = rec.invoice_amount - rec.applied_amount
                rec.invoice_amount_residual = rec.invoice_amount
            elif rec.state == 'posted':
                rec.amount_remaining = rec.invoice_amount_residual - rec.applied_amount

    # calculate difference applied amount with invoice amount
    @api.onchange('applied_amount')
    def compute_payment_difference(self):
        if self.invoice_amount - self.applied_amount < 10000:
            # self.payment_difference_handling = 'reconcile'
            if self.applied_amount != self.invoice_amount:
                if self.misc_currency_id == self.invoice_currency_id:
                    # Same currency.
                    self.payment_difference = self.invoice_amount - self.applied_amount
                    # print(self.payment_difference, 'masuk if')
                elif self.misc_currency_id == self.company_id.currency_id == self.invoice_currency_id:
                    # Payment expressed on the company's currency.
                    self.payment_difference = self.invoice_amount - self.applied_amount
                    # print(self.payment_difference, 'masuk elif')
                else:
                    # Foreign currency on payment different than the one set on the journal entries.
                    amount_payment_currency = self.company_id.currency_id._convert(self.invoice_amount,
                                                                                   self.invoice_currency_id,
                                                                                   self.company_id,
                                                                                   self.transaction_date)
                    self.payment_difference = amount_payment_currency - self.applied_amount
                    # print(self.payment_difference, 'masuk else')

        # check currency

    @api.onchange('applied_amount', 'payment_difference_handling')
    def _onchange_difference_handling(self):
        if self.payment_difference_handling == 'open':
            self.payment_difference = 0
        elif self.payment_difference_handling == 'reconcile':
            if self.applied_amount != self.invoice_amount:
                if self.misc_currency_id == self.invoice_currency_id:
                    # Same currency.
                    self.payment_difference = self.invoice_amount - self.applied_amount
                    # print(self.payment_difference, 'masuk if')
                elif self.misc_currency_id == self.company_id.currency_id == self.invoice_currency_id:
                    # Payment expressed on the company's currency.
                    self.payment_difference = self.invoice_amount - self.applied_amount
                    # print(self.payment_difference, 'masuk elif')
                else:
                    # Foreign currency on payment different than the one set on the journal entries.
                    amount_payment_currency = self.company_id.currency_id._convert(self.invoice_amount,
                                                                                   self.invoice_currency_id,
                                                                                   self.company_id,
                                                                                   self.transaction_date)
                    self.payment_difference = amount_payment_currency - self.applied_amount

    # check currency
    @api.onchange('misc_id', 'invoice_id')
    def _onchange_misc_receipt(self):
        if self.misc_currency_id != self.invoice_currency_id:
            if self.misc_currency_id == self.company_id.currency_id:
                self.applied_amount_currency = self.company_id.currency_id._convert(
                    self.applied_amount, self.invoice_currency_id, self.company_id, self.transaction_date)
            elif self.invoice_currency_id == self.company_id.currency_id:
                self.applied_amount_currency = self.company_id.currency_id._convert(
                    self.applied_amount, self.misc_currency_id, self.company_id, self.transaction_date)
        elif self.misc_currency_id == self.invoice_currency_id:
            if self.misc_currency_id != self.company_id.currency_id:
                self.applied_amount_currency = self.applied_amount
            elif self.invoice_currency_id == self.company_id.currency_id:
                self.applied_amount_currency = self.company_id.currency_id._convert(
                    self.applied_amount, self.misc_currency_id, self.company_id, self.transaction_date)
        else:
            self.applied_amount_currency = self.applied_amount
        if self.invoice_id:
            if self.misc_remaining_amount >= self.invoice_amount:
                self.applied_amount = self.invoice_amount
            elif self.misc_remaining_amount < self.invoice_amount:
                self.applied_amount = self.misc_remaining_amount
            self.company_id = self.invoice_id.company_id.id

    @api.depends('misc_id', 'invoice_id', 'applied_amount')
    def _compute_applied_amount_currency(self):
        for rec in self:
            if rec.misc_currency_id != rec.invoice_currency_id:
                if rec.misc_currency_id == rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.company_id.currency_id._convert(
                        rec.applied_amount, rec.invoice_currency_id, rec.company_id, rec.transaction_date)
                elif rec.invoice_currency_id == rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.company_id.currency_id._convert(
                        rec.applied_amount, rec.misc_currency_id, rec.company_id, rec.transaction_date)
            elif rec.misc_currency_id == rec.invoice_currency_id:
                if rec.misc_currency_id != rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.applied_amount
                elif rec.invoice_currency_id == rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.company_id.currency_id._convert(
                        rec.applied_amount, rec.misc_currency_id, rec.company_id, rec.transaction_date)
            else:
                rec.applied_amount_currency = rec.applied_amount

    @api.onchange('applied_amount')
    def _onchange_applied_amount(self):
        if self.applied_amount > self.invoice_amount:
            raise UserError(_(
                "You can't set applied amount greater than invoice amount."))

    @api.onchange("journal_id")
    def _onchange_journal(self):
        if (
                self.journal_id
                and self.journal_id.operating_unit_id
                and self.journal_id.operating_unit_id != self.operating_unit_id
        ):
            self.operating_unit_id = self.journal_id.operating_unit_id

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in (self.journal_id.payment_debit_account_id, self.journal_id.payment_credit_account_id):
                liquidity_lines += line
            elif line.account_id.internal_type in (
                    'receivable', 'payable') or line.partner_id == line.company_id.partner_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        # if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
        #     raise UserError(_(
        #         "You can't create a new payment without an outstanding payments/receipts account set on the %s journal."
        #         , self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = self.payment_difference
        # write_off_amount_currency = write_off_line_vals.get('payment_difference', 0.0)
        # print(write_off_amount_currency)

        if self.applied_amount > 0:
            liquidity_amount_currency = self.applied_amount
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        write_off_balance = self.misc_currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.misc_currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.misc_currency_id.id
        liquidity_line_name = 'Applied Miscellaneous no ' + self.misc_id.name + ' to invoice no ' + self.invoice_id.name

        if self.manual_currency_rate_active:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)

        debit_account_id = credit_account_id = None
        if self.misc_type == 'receive' and not self.invoice_id.transaction_type_id:
            debit_account_id = self.misc_id.misc_partner_id.property_account_receivable_id.id \
                               or self.misc_id.partner_id.property_account_receivable_id.id
            credit_account_id = self.invoice_id.partner_id.property_account_receivable_id.id
        elif self.misc_type == 'receive' and self.invoice_id.transaction_type_id:
            debit_account_id = self.misc_id.misc_partner_id.property_account_receivable_id.id \
                               or self.misc_id.partner_id.property_account_receivable_id.id
            credit_account_id = self.invoice_id.transaction_type_id.account_id.id
        elif self.misc_type == 'payment':
            debit_account_id = self.invoice_id.partner_id.property_account_payable_id.id
            credit_account_id = self.misc_id.destination_account_id.id

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'account_id': debit_account_id
            },
            # Receivable
            {
                'name': liquidity_line_name,
                'date_maturity': self.transaction_date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'account_id': credit_account_id
            },
        ]
        if self.payment_difference > 0 and self.payment_difference_handling == 'reconcile':
            # Write-off line.
            # print(write_off_balance,'masuk nambah jurnal selisih')
            write_off_name = 'write off ' + self.invoice_id.name
            line_vals_list.append({
                'name': write_off_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'account_id': self.writeoff_account_id.id,
            })

        # print(line_vals_list)
        return line_vals_list

    @api.model_create_multi
    def create(self, vals):
        # OVERRIDE
        write_off_line_vals_list = []
        for val in vals:
            # Hack to add a custom write-off line.
            write_off_line_vals_list.append(val.pop('write_off_line_vals', None))

            # Force the move_type to avoid inconsistency with residual 'default_move_type' inside the context.
            val['move_type'] = 'entry'
            val['name'] = '/'
        applied = super().create(vals)

        for i, pay in enumerate(applied):
            write_off_line_vals = write_off_line_vals_list[i]

            # Write payment_id on the journal entry plus the fields being stored in both models but having the same
            # name, e.g. partner_bank_id. The ORM is currently not able to perform such synchronization and make things
            # more difficult by creating related fields on the fly to handle the _inherits.
            # Then, when partner_bank_id is in vals, the key is consumed by account.payment but is never written on
            # account.move.
            to_write = {'id': pay.id}
            for k, v in vals[i].items():
                if k in self._fields and self._fields[k].store and k in pay.move_id._fields \
                        and pay.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                        pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

            pay.move_id.write(to_write)

        return applied

    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in (
                'date', 'applied_amount', 'currency_id', 'partner_id', 'invoice_id',
                'journal_id',
        )):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.

            if liquidity_lines and counterpart_lines and writeoff_lines:

                counterpart_amount = sum(counterpart_lines.mapped('amount_currency'))
                writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))

                # To be consistent with the payment_difference made in account.payment.register,
                # 'writeoff_amount' needs to be signed regarding the 'amount' field before the write.
                # Since the write is already done at this point, we need to base the computation on accounting values.
                if (counterpart_amount > 0.0) == (writeoff_amount > 0.0):
                    sign = -1
                else:
                    sign = 1
                writeoff_amount = abs(writeoff_amount) * sign

                write_off_line_vals = {
                    'name': writeoff_lines[0].name,
                    'amount': writeoff_amount,
                    'account_id': writeoff_lines[0].account_id.id,
                }
            else:
                write_off_line_vals = {}

            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
            # print(line_vals_list, 'syncronize')
            line_ids_commands = []
            if liquidity_lines:
                line_ids_commands.append((1, liquidity_lines.id, line_vals_list[0]))
            else:
                line_ids_commands.append((0, 0, line_vals_list[0]))
            if counterpart_lines:
                line_ids_commands.append((1, counterpart_lines.id, line_vals_list[1]))
            else:
                line_ids_commands.append((0, 0, line_vals_list[1]))

            for line in writeoff_lines:
                line_ids_commands.append((2, line.id))

            for extra_line_vals in line_vals_list[2:]:
                line_ids_commands.append((0, 0, extra_line_vals))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            pay.move_id.write({
                'partner_id': pay.partner_id.id,
                'currency_id': pay.misc_currency_id.id,
                'partner_bank_id': pay.misc_id.destination_account_id.id,
                'manual_currency_rate_active': pay.manual_currency_rate_active,
                'manual_currency_rate': pay.manual_currency_rate,
                'line_ids': line_ids_commands,
            })

    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()

    def action_applied_invoice(self):
        self.ensure_one()
        reverse = self.env['account.move'].search([('reversed_entry_id', '=', self.move_id.id)])
        if self.move_id.state == 'posted' and reverse:
            raise UserError(_(
                "Your Applied Receipt / Applied Payment Journal is reversed "
                "Please Create New Applied Receipt / Applied Payment Again"))
        if self.misc_remaining_amount == 0:
            raise UserError(_(
                "Your remaining amount is zero (0) "
                "You can't applied any invoice in this transaction"))
        if self.transaction_type == 'unapply':
            self.transaction_type = 'apply'
        if not self.id:
            apply = self.env['applied.invoices'].create({
                'misc_id': self.misc_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'invoice_id': self.invoice_id.id,
                'transaction_type': self.transaction_type if self.transaction_type == 'apply' else 'apply',
                'transaction_date': self.transaction_date,
                'applied_amount': self.applied_amount,
                'applied_amount_currency': self.applied_amount_currency,
                'move_id': self.move_id.id
            })

        if self.invoice_id:
            # print(self.invoice_id.amount_residual_signed, 'disini berapa nilainya', self.applied_amount + self.payment_difference )
            self.invoice_id.amount_residual_signed -= (self.applied_amount + self.payment_difference)
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            # print(self.invoice_id.amount_residual_signed, 'berapa nilainya')
            if self.invoice_id.amount_residual_signed > 0:
                self.invoice_id.payment_state = 'partial'
            elif self.invoice_id.amount_residual_signed == 0:
                self.invoice_id.payment_state = 'in_payment'
        # if self.misc_id:
        # self.partner_id = self.invoice_id.partner_id.id
        # self.misc_id.applied_amount += self.applied_amount
        if self.move_id and self.misc_id and not reverse:
            self.partner_id = self.invoice_id.partner_id.id
            self.misc_id.applied_amount += self.applied_amount
            self.move_id.ref = self.invoice_id.name
            self.move_id.partner_id = self.invoice_id.partner_id.id
            self.move_id.commercial_partner_id = self.invoice_id.partner_id.id
            if self.move_id.state == 'draft':
                self.move_id._post(soft=False)
            self.action_reconcile()

        # debit_move_id = credit_move_id = 0
        # for line in self.move_id.line_ids:
        #     if line and line.move_id.state != 'cancel':
        #         debit_move_id = line.id
        # for line in self.invoice_id.move_id.line_ids:
        #     if line and line.move_id.state != 'cancel':
        #         credit_move_id = line.id
        # account_reconcile = self.env['account.partial.reconcile'].create({
        #         'amount': self.applied_amount,
        #         'debit_amount_currency': self.applied_amount_currency,
        #         'credit_amount_currency': self.applied_amount_currency,
        #         'debit_currency_id': self.invoice_currency_id.id,
        #         'credit_currency_id': self.invoice_id.currency_id.id,
        #         'company_id': self.company_id,
        #         'max_date': self.transaction_date,
        #         'debit_move_id': debit_move_id,
        #         'credit_move_id': credit_move_id,
        #     })
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.invoices.form")])
        action = {
            'name': _("Applied Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.view_applied_invoices_form"': '',
        }
        if len(self.move_id) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

    def action_unapplied_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            self.invoice_id.amount_residual_signed = self.invoice_id.amount_residual_signed + \
                                                     self.applied_amount + \
                                                     self.payment_difference
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            if self.invoice_id.amount_residual_signed == self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'not_paid'
            elif self.invoice_id.amount_residual_signed < self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'partial'
            # elif self.invoice_id.amount_residual_signed > self.invoice_id.amount_total_signed:
            #     raise UserError(_(
            #         "You can't unapplied amount greater than applied amount. please set amount correctly"))
        if self.misc_id:
            # self.misc_id.applied_amount = self.misc_id.applied_amount - self.applied_amount
            total_amount_applied = 0
            for line in self.misc_id.invoice_ids:
                reverse = self.env['account.move'].search([('reversed_entry_id', '=', line.move_id.id)])
                if line.move_id.state == 'posted' and line.transaction_type == 'apply' and not reverse:
                    total_amount_applied += line.applied_amount
            self.misc_id.applied_amount = total_amount_applied
        if self.move_id:
            self.move_id.button_cancel()
        self.transaction_type = 'unapply'
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.invoices.form")])
        action = {
            'name': _("Applied Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.view_applied_invoices_form"': '',
        }
        if self.id:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

    def action_applied_bill(self):
        self.ensure_one()
        if not self.id:
            apply = self.env['applied.invoices'].create({
                'misc_id': self.misc_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'invoice_id': self.invoice_id.id,
                'transaction_type': self.transaction_type,
                'transaction_date': self.transaction_date,
                'applied_amount': self.applied_amount,
                'applied_amount_currency': self.applied_amount_currency,
                'move_id': self.move_id.id
            })

        if self.invoice_id:
            self.invoice_id.amount_residual_signed -= self.applied_amount
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            if self.invoice_id.amount_residual_signed > 0:
                self.invoice_id.payment_state = 'partial'
            elif self.invoice_id.amount_residual_signed == 0:
                self.invoice_id.payment_state = 'in_payment'
        if self.misc_id:
            self.partner_id = self.invoice_id.partner_id.id
            self.misc_id.applied_amount += self.applied_amount
        if self.move_id:
            self.move_id.ref = self.invoice_id.name
            self.move_id.partner_id = self.invoice_id.partner_id.id
            self.move_id.commercial_partner_id = self.invoice_id.partner_id.id
            self.move_id._post(soft=False)
            self.action_reconcile()

        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.bill.form")])
        action = {
            'name': _("Applied Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.view_applied_bill_form"': '',
        }
        if len(self.move_id) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

    def action_unapplied_bill(self):
        self.ensure_one()
        if self.invoice_id:
            self.invoice_id.amount_residual_signed = self.invoice_id.amount_residual_signed + self.applied_amount
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            if self.invoice_id.amount_residual_signed == self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'not_paid'
            elif self.invoice_id.amount_residual_signed < self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'partial'
            # elif self.invoice_id.amount_residual_signed > self.invoice_id.amount_total_signed:
            #     raise UserError(_(
            #         "You can't unapplied amount greater than applied amount. please set amount correctly"))
        if self.misc_id:
            self.misc_id.applied_amount = self.misc_id.applied_amount - self.applied_amount
        if self.move_id:
            self.move_id.button_cancel()
        self.transaction_type = 'unapply'
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.bill.form")])
        action = {
            'name': _("Applied Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.view_applied_bill_form"': '',
        }
        if self.id:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

    def action_reconcile(self):
        self.ensure_one()
        print(self.move_id, 'masuk action reconcile')
        if self.move_id and self.move_id.state == 'posted':
            # Auto reconcile
            # recon miscellaneous journal with applied customer
            recon = []
            receive_account = self.misc_id.partner_id.property_account_receivable_id.id
            payment_account = self.misc_id.destination_account_id.id \
                              or self.invoice_id.partner_id.property_account_payable_id.id
            search = [('account_id', 'in', (receive_account, payment_account)), ('reconciled', '=', False)]
            for misc_lines in self.misc_id.move_id.line_ids:
                print(misc_lines, 'reconcile misc applied customer', payment_account, receive_account)
                for misc in misc_lines.filtered_domain(search):
                    print(misc, 'misc_line')
                    recon.append(misc)
            for lines in recon:
                cust_lines = self.misc_id.applied_customer_move_id.line_ids.filtered_domain(search) \
                    if self.misc_id.applied_customer_move_id else self.invoice_ids.filtered_domain(search)
                print(cust_lines, 'reconcile applied customer')
                for cust in cust_lines.account_id:
                    (cust_lines + lines).filtered_domain([
                        ('account_id', '=', cust.id),
                        ('reconciled', '=', False)
                    ]).reconcile()

            # recon applied customer journal with applied invoice
            domain = [('account_internal_type', 'in', ('receivable', 'payable', receive_account, payment_account)), ('reconciled', '=', False)]
            to_reconcile = []
            for applied_invoice in self.move_id.line_ids:
                print(applied_invoice, 'reconcile debit applied invoice')
                for inv_line in applied_invoice.filtered_domain(domain):
                    print(inv_line, 'inv_line')
                    to_reconcile.append(inv_line)

            for lines in to_reconcile:
                misc_lines = self.misc_id.applied_customer_move_id.line_ids.filtered_domain(domain) \
                    if self.misc_id.applied_customer_move_id else self.misc_id.move_id.line_ids.filtered_domain(domain)
                print(misc_lines, 'reconcile misc customer lines applied invoice')
                for misc in misc_lines.account_id:
                    (misc_lines + lines).filtered_domain([
                        ('account_id', '=', misc.id),
                        ('reconciled', '=', False)
                    ]).reconcile()

            # recon applied invoice journal with invoice
            invoice_recon = []
            invoice_account = self.invoice_id.transaction_type_id.account_id.id \
                if self.invoice_id.move_type == 'out_invoice' and self.invoice_id.transaction_type_id \
                else self.invoice_id.partner_id.property_account_receivable_id.id
            bill_account = self.invoice_id.partner_id.property_account_payable_id.id
            find = [('account_id', 'in', (invoice_account, bill_account)), ('reconciled', '=', False)]
            for invoice_lines in self.invoice_id.line_ids:
                print(invoice_lines, 'reconcile invoice')
                for inv in invoice_lines.filtered_domain(find):
                    print(inv, 'invoice_lines')
                    invoice_recon.append(inv)
            for lines in invoice_recon:
                applied_lines = self.move_id.line_ids.filtered_domain(find)
                print(applied_lines, 'reconcile credit applied invoice',lines)
                for applied in applied_lines.account_id:
                    (applied_lines + lines).filtered_domain([
                        ('account_id', '=', applied.id),
                        ('reconciled', '=', False)
                    ]).reconcile()
