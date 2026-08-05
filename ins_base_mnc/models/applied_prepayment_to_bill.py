from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AppliedPrepaymentToBill(models.Model):
    _name = 'applied.prepayment.to.bill'
    _description = 'Applied Prepayment To Bill'
    _inherits = {'account.move': 'move_id'}

    def get_move_id(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            print(active_id, 'active_id')
            return self.env['applied.prepayment.to.bill'].browse(active_id)

    invoice_id = fields.Many2one(
        'account.move',
        string='Bill', required=True,
        ondelete='cascade',
        domain="[('id', '=', active_id)]")
    bill_type = fields.Selection(selection=[
        ('standard', "Standard"),
        ('prepayment', "Prepayment"),
        ('settlement', "Settlement")],
        string="Bill Type", related='invoice_id.bill_type',)
    partner_id = fields.Many2one(
        'res.partner', string="Partner Name",
        related='invoice_id.partner_id', copy=False)
    invoice_account_id = fields.Many2one(
        'account.account', string="Account",
        compute='_compute_invoice_account_id', copy=False)
    currency_id = fields.Many2one(
        'res.currency', string='Invoice Currency',
        related='invoice_id.currency_id')
    invoice_amount = fields.Monetary(
        currency_field='currency_id',
        related='invoice_id.amount_residual',
        string="Amount Due",
        readonly=True)
    journal_id = fields.Many2one(
        'account.journal', store=True,
        readonly=False, required=True, default=lambda self: self.env['account.journal'].search([('is_applied_prepayment', '=', True)]),
        domain="[('company_id', '=', company_id)]")
    company_id = fields.Many2one(
        string='Company', store=True, readonly=True,
        related='move_id.company_id', change_default=True,
        default=lambda self: self.env.company)
    prepayment_id = fields.Many2one(
        comodel_name='account.move', required=True,
        domain="[('company_id', '=', company_id),('bill_type','=','prepayment'),('is_full_applied_prepayment','=',False)]",
        string='Prepayment Invoice')
    prepayment_currency_id = fields.Many2one(
        'res.currency', string='Invoice Currency',
        readonly=True, related='prepayment_id.currency_id')
    prepayment_amount = fields.Monetary(
        currency_field='prepayment_currency_id',
        related='prepayment_id.amount_total',
        string="Amount Prepayment",
        readonly=True, default=0)
    amount_prepayment_applied_for_settlement = fields.Float(
        related='prepayment_id.amount_prepayment_applied_for_settlement',
        string="Amount Prepayment Applied to bill",
        readonly=True, default=0)
    prepayment_amount_remaining = fields.Monetary(
        'Prepayment Remaining Amount',
        currency_field='prepayment_currency_id',
        compute='_compute_prepayment_amount_remaining')
    transaction_type = fields.Selection([
        ('apply', 'Applied prepayment to bill Invoice'), ('unapply', 'Un-Apply bill Invoice')],
        string='Transaction Type',
        copy=False, default='unapply', index=True)
    transaction_date = fields.Datetime(
        'Transaction Date',
        required=True,
        default=fields.Datetime.now)
    applied_amount = fields.Monetary(
        currency_field='currency_id',
        string="Applied Amount",
        required=True, default=0)
    applied_amount_currency = fields.Monetary(
        string="Applied Amount(foreign currency)",
        store=True, copy=False,
        compute='_compute_applied_amount_currency',
        currency_field='prepayment_currency_id')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        readonly=True, required=True, ondelete='cascade',
        check_company=True)

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

    # _sql_constraints = [
    #     (
    #     'unique_applied_invoice', 'unique (prepayment_id, invoice_id,transaction_type)', 'Applied Invoice is already exists!')
    # ]
    _sql_constraints = [
        (
        'unique_applied_invoice', 'Check(1 = 1)', 'Applied Invoice is already exists!')
    ]

    @api.onchange('prepayment_id', 'invoice_id', 'applied_amount', 'journal_id')
    def _compute_invoice_account_id(self):
        for invoice in self:
            invoice.invoice_account_id = invoice.invoice_id.partner_id.property_account_payable_id.id
            for rec in invoice.invoice_id.line_ids:
                if rec and rec.exclude_from_invoice_tab:
                    invoice.invoice_account_id = rec.account_id.id

    @api.onchange('prepayment_id', 'invoice_id', 'journal_id')
    def _onchange_prepayment_amount_remaining(self):
        for rec in self:
            rec.prepayment_amount_remaining = rec.prepayment_amount - rec.amount_prepayment_applied_for_settlement
            rec.applied_amount = rec.prepayment_amount - rec.amount_prepayment_applied_for_settlement

    @api.depends('prepayment_id', 'invoice_id', 'applied_amount', 'journal_id')
    def _compute_prepayment_amount_remaining(self):
        for rec in self:
            rec.prepayment_amount_remaining = rec.prepayment_id.amount_total - rec.prepayment_id.amount_prepayment_applied_for_settlement

    @api.depends('prepayment_id', 'invoice_id', 'applied_amount')
    def _compute_applied_amount_currency(self):
        for rec in self:
            if rec.prepayment_currency_id != rec.currency_id:
                if rec.prepayment_currency_id == rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.company_id.currency_id._convert(
                        rec.applied_amount, rec.currency_id, rec.company_id, rec.transaction_date)
                elif rec.currency_id == rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.company_id.currency_id._convert(
                        rec.applied_amount, rec.prepayment_currency_id, rec.company_id, rec.transaction_date)
            elif rec.prepayment_currency_id == rec.currency_id:
                if rec.prepayment_currency_id != rec.company_id.currency_id:
                    rec.applied_amount_currency = rec.applied_amount
                else:
                    rec.applied_amount_currency = rec.applied_amount

    # @api.onchange('applied_amount')
    # def _onchange_applied_amount(self):
    #     if self.applied_amount > (self.prepayment_amount - self.amount_prepayment_applied_for_settlement):
    #         raise UserError(_(
    #             "You can't set applied amount greater than prepayment amount remaining ."))
    #     if self.applied_amount > self.invoice_amount:
    #         raise UserError(_(
    #             "You can't set applied amount greater than invoice amount remaining ."))


    @api.onchange("journal_id")
    def _onchange_journal(self):
        if (
                self.journal_id
                and self.journal_id.operating_unit_id
                and self.journal_id.operating_unit_id != self.operating_unit_id
        ):
            self.operating_unit_id = self.journal_id.operating_unit_id
        if not self.invoice_account_id:
            self.invoice_account_id = self.invoice_id.partner_id.property_account_payable_id.id

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

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id
        liquidity_line_name = 'Applied Prepayment no ' + self.prepayment_id.name + ' to invoice no ' + self.invoice_id.name

        debit_account_id = credit_account_id = None
        for invoice in self.invoice_id.line_ids:
            if invoice and invoice.exclude_from_invoice_tab:
                debit_account_id = invoice.account_id.id or self.invoice_id.partner_id.property_account_payable_id.id
        for prepay in self.prepayment_id.line_ids:
            if prepay and not prepay.exclude_from_invoice_tab:
                credit_account_id = prepay.account_id.id
                # debit_account_id = self.invoice_account_id.id or self.invoice_id.partner_id.property_account_payable_id.id
                # print(debit_account_id, 'vs',credit_account_id)

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
                'currency_id': pay.invoice_currency_id.id,
                'partner_bank_id': pay.misc_id.destination_account_id.id,
                'line_ids': line_ids_commands,
            })

    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()

    def action_applied_bill(self):
        self.ensure_one()
        if self.invoice_amount == 0:
            raise UserError(_(
                "Your remaining amount is zero (0) "
                "You can't applied any prepayment to this bill transaction"))
        if self.applied_amount > (self.prepayment_amount - self.amount_prepayment_applied_for_settlement):
            print("applied_amount", self.applied_amount, "vs remaining_amount", (self.prepayment_amount - self.amount_prepayment_applied_for_settlement))
            raise UserError(_(
                "You can't set applied amount greater than prepayment amount remaining ."))
        if self.applied_amount > self.invoice_amount:
            print("applied_amount", self.applied_amount, "vs invoice_amount", self.invoice_amount)
            raise UserError(_(
                "You can't set applied amount greater than invoice amount remaining ."))
        if not self.id:
            apply = self.env['applied.prepayment.to.bill'].create({
                'invoice_id': self.invoice_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'prepayment_id': self.prepayment_id.id,
                'transaction_type': self.transaction_type,
                'transaction_date': self.transaction_date,
                'applied_amount': self.applied_amount,
                'applied_amount_currency': self.applied_amount_currency,
                'move_id': self.move_id.id
            })

        if self.invoice_id:
            print("menghitung pemotongan nilai invoice")
            self.invoice_id.amount_residual_signed -= self.applied_amount
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            print(self.invoice_id.amount_residual,"sisa", self.invoice_id.amount_residual_signed)
            if self.invoice_id.amount_residual_signed > 0:
                self.invoice_id.payment_state = 'partial'
            elif self.invoice_id.amount_residual_signed == 0:
                self.invoice_id.payment_state = 'in_payment'
        if self.prepayment_id:
            self.prepayment_id.amount_prepayment_applied_for_settlement += self.applied_amount
            self.prepayment_id.settlement_invoice = self.prepayment_id.settlement_invoice + self.invoice_id.payment_reference
        if self.transaction_type == 'unapply':
            self.transaction_type = 'apply'
        if self.move_id:
            self.move_id.ref = self.invoice_id.name
            self.move_id.partner_id = self.invoice_id.partner_id.id
            self.move_id.commercial_partner_id = self.invoice_id.partner_id.id
            if self.move_id.state != 'posted':
                self.move_id._post(soft=False)
            self.action_reconcile()

        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.prepayment.to.bill.form")])
        action = {
            'name': _("Applied Prepayment to Bill"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.prepayment.to.bill',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_base_mnc.view_applied_prepayment_to_bill_form"': '',
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
        if self.prepayment_id:
            self.prepayment_id.amount_prepayment_applied_for_settlement = self.prepayment_id.amount_prepayment_applied_for_settlement - self.applied_amount
            self.transaction_type = 'unapply'
        if self.move_id:
            # self.move_id.button_cancel_reversal()
            self.action_unreconcile()

        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.prepayment.to.bill.form")])
        action = {
            'name': _("Applied Prepayment Vendor Bill"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.prepayment.to.bill',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_base_mnc.view_applied_prepayment_to_bill_form"': '',
        }
        if self.id:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

    def action_reconcile(self):
        self.ensure_one()
        if self.move_id and self.move_id.state == 'posted':
            # Auto reconcile
            # recon applied invoice journal with invoice
            invoice_recon = []
            invoice_account = self.invoice_account_id.id
            bill_account = self.invoice_id.partner_id.property_account_payable_id.id
            find = [('account_id', 'in', (invoice_account, bill_account)), ('reconciled', '=', False)]
            for invoice_lines in self.invoice_id.line_ids:
                print(invoice_lines, 'reconcile applied invoice')
                for inv in invoice_lines.filtered_domain(find):
                    print(inv, 'invoice_lines')
                    invoice_recon.append(inv)
            for lines in invoice_recon:
                applied_lines = self.move_id.line_ids.filtered_domain(find)
                print(applied_lines, 'reconcile applied bill')
                for applied in applied_lines.account_id:
                    (applied_lines + lines).filtered_domain([
                        ('account_id', '=', applied.id),
                        ('reconciled', '=', False)
                    ]).reconcile()

    def action_unreconcile(self):
        self.ensure_one()
        if self.move_id and self.move_id.state == 'posted':
            # Auto reconcile
            # recon applied invoice journal with invoice
            invoice_recon = []
            invoice_account = self.invoice_account_id.id
            bill_account = self.invoice_id.partner_id.property_account_payable_id.id
            print(invoice_account,'invoice_account',bill_account,'bill_account')
            find = [('account_id', 'in', (invoice_account, bill_account)), ('reconciled', '=', True)]
            for invoice_lines in self.invoice_id.line_ids:
                print(invoice_lines, 'unreconcile applied invoice')
                for inv in invoice_lines.filtered_domain(find):
                    print(inv, 'invoice_lines')
                    invoice_recon.append(inv)
            for lines in invoice_recon:
                applied_lines = self.move_id.line_ids.filtered_domain(find)
                print(applied_lines, 'unreconcile applied bill', lines)
                for applied in applied_lines.account_id:
                    (applied_lines + lines).filtered_domain([
                        ('account_id', '=', applied.id),
                        ('reconciled', '=', True)
                    ]).remove_move_reconcile()


