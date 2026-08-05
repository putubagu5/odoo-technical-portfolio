from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class MiscellaneousMiscellaneous(models.Model):
    _name = 'miscellaneous.miscellaneous'
    _inherits = {'account.move': 'move_id'}
    # _rec_name = 'misc_name'
    _description = 'Miscellaneous Transaction'
    _order = "date desc, name desc"
    _check_company_auto = True

    def _get_default_journal(self):
        ''' Retrieve the default journal for the account.payment.
        /!\ This method will not override the method in 'account.move' because the ORM
        doesn't allow overriding methods using _inherits. Then, this method will be called
        manually in 'create' and 'new'.
        :return: An account.journal record.
        '''
        return self.env['account.move']._search_default_journal(('bank', 'cash'))

    # == Business fields ==
    move_id = fields.Many2one(
        'account.move', string='Journal Entry', copy=False, index=True,
        readonly=True, required=True, ondelete='cascade',
        check_company=True)
    misc_name = fields.Char(
        string="Reference Number", copy=False, index=True,
        readonly=True)
    bukti_potong = fields.Char(string='Bukti Potong PPh', required=False)
    receipt_type_id = fields.Many2one(
        'receipt.type', string='Receipt Type', copy=False)
    receipt_type_category = fields.Selection([
        ('misc', 'Miscellaneous Receipts'), ('rcv', 'Payment Receipt')],
        related='receipt_type_id.category', string='Category Type', copy=False, default=None)
    receivable_activities_id = fields.Many2one(
        'receivable.activities', string='Receivable Activities', copy=False)
    misc_type = fields.Selection(
        selection=[
            ('receive', 'Receipt'),
            ('payment', 'Payment'),
        ], string='Type', default="receive")
    description = fields.Char(
        string="Description", copy=False)
    journal_id = fields.Many2one(
        'account.journal', string='Bank Account',
        copy=False, check_company=True, index=True)
    company_id = fields.Many2one(
        'res.company', string='Company', store=True, readonly=True,
        related='journal_id.company_id', change_default=True,
        default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one(
        'operating.unit', domain="[('user_ids', '=', uid)]"
    )
    transaction_date = fields.Datetime(
        'Transaction Date', required=True, copy=False,
        default=fields.Datetime.now)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id', copy=False,
        help="The payment's currency.")
    misc_partner_id = fields.Many2one(
        'res.partner', string="Customer",
        store=True, readonly=False, ondelete='restrict', copy=False,
        domain="['|', ('parent_id','=', False), ('is_company','=', True), ('customer_rank', '>', 0)]")
    amount = fields.Monetary(
        currency_field='currency_id', string="Amount")
    remaining_amount = fields.Monetary(
        currency_field='currency_id', string="Remaining Amount",
        compute='_compute_reserve_amount', readonly=True, default=0)
    reserve_amount = fields.Monetary(
        currency_field='currency_id', string="Available Amount",
        compute='_compute_reserve_amount', readonly=True, default=0)
    applied_amount = fields.Monetary(
        currency_field='currency_id', string="Total Amount Applied",
        readonly=True, default=0, copy=False)
    partner_bank_id = fields.Many2one(
        'res.partner.bank', string="Recipient Bank Account",
        readonly=False, required=False, store=True)
    destination_account_id = fields.Many2one(
        'account.account', string='Destination Account',
        store=True, readonly=False, required=True,
        help="Account.")
    invoice_ids = fields.One2many(
        'applied.invoices', 'misc_id',
        string='Applied Invoice', copy=False,
        ondelete='cascade',
        help="The Misc has applied to Invoice.")

    # addition journal when applied misc unidentified account to partner account
    applied_customer_journal_id = fields.Many2one(
        'account.journal', string='Partner Clearing Journal',
        domain="[('type','=', 'general')]",
        copy=False, check_company=True, index=True,
        help="The journal for to use applied from unidentified to Customer or vendor partner.")
    # applied_customer_ids = fields.One2many(
    #     'applied.customer', 'misc_id',
    #     string='Applied to Customer', copy=False,
    #     help="The Misc has applied to Customer.")
    applied_customer_move_id = fields.Many2one(
        'account.move', string='Applied to Partner Journal', copy=False,
        ondelete='cascade', check_company=True)
    applied_partner_date = fields.Date(
        'Applied Partner Date', copy=False,
        default=fields.Date.context_today)
    journal_group = fields.Selection(
        selection=[
            ('split', 'Un-Identify'),
            ('merge', 'Un-apply'),
        ], string='Journal Applied Group', default="split")
    applied_partner_account = fields.Many2one(
        'account.account', string='Un-Apply Account',
        store=True, related='misc_partner_id.property_account_receivable_id',
        help="Account Clearing Applied Partner Journal.")
    receipt_number = fields.Char('Receipt Number')

    # ==== Analytic fields ====
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    #
    # @api.constrains('invoice_ids', 'id')
    # def _check_invoice_unique(self):
    #     # invoice_counts = self.search_count([('misc_id', '=', self.id), ('invoice_id', 'in', self.invoice_ids)])
    #     invoices = []
    #     for invoice in self.invoice_ids:
    #         invoices.append(invoice.invoice_id.id)
    #     invoice_counts = self.env['applied.invoices'].search(
    #         [('misc_id', '=', self.id), ('invoice_id', 'in', invoices)])
    #     print(invoice_counts,invoices)
    #     if len(invoice_counts) > 0:
    #         raise ValidationError("Invoice number already exists!")

    @api.constrains('reserve_amount')
    def _check_reserve_amount(self):
        """ constrains function to check if reserve_amount is negative """
        for rec in self:
            if rec.reserve_amount < 0:
                raise ValidationError('Available Amount cannot be negative')

    @api.constrains('receipt_number', 'journal_id', 'amount', 'cancel_reversal')
    def _check_receipt_number(self):
        for rec in self:
            if rec.receipt_number and rec.journal_id:
                check_receipt_number = self.search([
                    ('id', '!=', rec.id),
                    ('receipt_number', '=', rec.receipt_number),
                    ('journal_id', '=', rec.journal_id.id),
                    ('amount', '=', rec.amount),
                    ('cancel_reversal', '!=', True)
                ])
                if check_receipt_number:
                    raise Warning(
                        _(
                            "Receipt number already exists!"
                        )
                    )

    @api.onchange('journal_group')
    def _onchange_journal_group(self):
        if self.journal_group == 'split' and self.state == 'draft':
            self.misc_partner_id = False

    @api.onchange('receipt_type_id')
    def _onchange_receipt_type(self):
        if self.receipt_type_id and self.receipt_type_id.category != 'misc':
            self.destination_account_id = self.receipt_type_id.account_id
        elif self.receipt_type_id and self.receipt_type_id.category == 'misc':
            self.destination_account_id = False

    @api.onchange('receivable_activities_id')
    def _onchange_receivable_activities(self):
        if self.receivable_activities_id and self.receipt_type_id.category == 'misc':
            self.destination_account_id = self.receivable_activities_id.account_id

    @api.depends('applied_amount', 'amount', 'write_date', 'write_uid')
    def _compute_remaining_amount(self):
        self.remaining_amount = 0
        for rec in self:
            if rec.amount > 0:
                rec.remaining_amount = rec.amount
            if rec.amount > 0 and rec.applied_amount > 0:
                rec.remaining_amount = rec.amount - rec.applied_amount

    @api.depends('applied_amount', 'amount', 'invoice_ids')
    def _compute_reserve_amount(self):
        for rec in self:
            total_reserve_amount = 0
            total_amount_applied = 0
            print(total_reserve_amount, rec.applied_amount, rec.amount, rec.reserve_amount)
            if rec.amount > 0:
                rec.remaining_amount = rec.amount
            for line in rec.invoice_ids:
                if line.transaction_type == 'unapply' and line.state == 'draft':
                    total_reserve_amount += line.applied_amount
                reverse = self.env['account.move'].search([('reversed_entry_id', '=', line.move_id.id)])
                if line.move_id.state == 'posted' and line.transaction_type == 'apply' and not reverse:
                    total_amount_applied += line.applied_amount
            print(total_reserve_amount, total_amount_applied)
            rec.applied_amount = total_amount_applied
            rec.remaining_amount = rec.amount - total_amount_applied
            rec.reserve_amount = rec.amount - total_reserve_amount - total_amount_applied
            print(rec.reserve_amount)

    @api.onchange("misc_partner_id")
    def _onchange_misc_partner_id(self):
        if self.misc_partner_id:
            self.partner_id = self.misc_partner_id.id

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            if not pay.currency_id:
                pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id
            if pay.journal_id and pay.journal_id.type == 'bank':
                pay.partner_bank_id = pay.journal_id.bank_account_id
            elif pay.journal_id and pay.journal_id.type == 'cash':
                pay.partner_bank_id = False

    def action_post(self):
        ''' draft -> posted '''
        if self.reserve_amount < 0:
            raise ValidationError('Available Amount cannot be negative')

        self.move_id._post(soft=False)
        if self.misc_type == 'receive' and self.misc_partner_id and self.journal_group == 'split' \
                and self.applied_customer_journal_id and not self.applied_customer_move_id:
            self.action_applied_to_partner()
        elif self.misc_type == 'receive' and self.misc_partner_id \
                and self.applied_customer_journal_id and self.applied_customer_move_id \
                and self.applied_customer_move_id.state == 'draft':
            if self.applied_customer_move_id.amount_total == self.amount:
                self.applied_customer_move_id._post(soft=False)
            elif self.applied_customer_move_id.amount_total != self.amount:
                to_write = []
                for move_line in self.applied_customer_move_id.line_ids:
                    to_write.append((1, move_line.id, {
                        'debit': self.amount if move_line.debit > 0.0 else 0.0,
                        'credit': self.amount if move_line.credit > 0.0 else 0.0,
                    }))
                    self.applied_customer_move_id.with_context(check_move_validity=False).write({'line_ids': to_write})
                self.applied_customer_move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        if self.invoice_ids:
            for rec in self.invoice_ids:
                if rec.state == 'posted':
                    raise UserError(_(
                        "You have payment / Receipt, "
                        "Please cancel Applied Receipt firstly before cancel this Payment / Receipt."))
                if rec.state == 'cancel':
                    # this action in the comment cause need craete journal reverse when cancel (depend account_document_reversal)
                    self.move_id.button_cancel()
                    # self.move_id.button_cancel_reversal()
        elif not self.invoice_ids:
            # this action in the comment cause need craete journal reverse when cancel (depend account_document_reversal)
            self.move_id.button_cancel()
            # self.move_id.button_cancel_reversal()
        # cancel applied to partner journal
        if self.applied_customer_move_id:
            for rec in self.applied_customer_move_id:
                rec.action_cancel()

    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()
        self.applied_customer_move_id.button_draft()

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        self._synchronize_to_moves(set(vals.keys()))
        if self.applied_customer_move_id:
            self.applied_customer_move_id.date = self.applied_partner_date
            self.applied_customer_move_id.reconciliation_date = self.applied_partner_date
        if self.reserve_amount < 0:
            print(self.reserve_amount, 'nilai reserve amount')
            raise UserError(
                _(
                 #  "Your amount applied invoice transaction is over limit (see reserve amount field) "
                 #  " please reduce your amount applied invoice "
                    
                    "Available amount connot negative"
                )
            )
        return res

    def unlink(self):
        # OVERRIDE to unlink the inherited account.move (move_id field) as well.
        moves = self.with_context(force_delete=True).move_id
        res = super().unlink()
        moves.unlink()
        return res

    @api.constrains("operating_unit_id", "company_id")
    def _check_company_operating_unit(self):
        for rec in self:
            if (
                    rec.company_id
                    and rec.operating_unit_id
                    and rec.company_id != rec.operating_unit_id.company_id
            ):
                raise UserError(
                    _(
                        "Configuration error. The Company in the"
                        " Payment / Receipt and in the Operating Unit must "
                        "be the same."
                    )
                )

    @api.onchange("journal_id")
    def _onchange_journal(self):
        if (
                self.journal_id
                and self.journal_id.operating_unit_id
                and self.journal_id.operating_unit_id != self.operating_unit_id
        ):
            self.operating_unit_id = self.journal_id.operating_unit_id
        if self.journal_id and self.journal_id.type == 'bank':
            self.partner_bank_id = self.journal_id.bank_account_id
        elif self.journal_id and self.journal_id.type == 'cash':
            self.partner_bank_id = False
        if self.receipt_type_id.category == 'receive' and not self.partner_id:
            raise UserError(
                _(
                    "Please Set Partner (Customer or Vendor) firstly"
                )
            )

    def _seek_for_lines(self):
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

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal."
                , self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.receipt_type_id:
            # Receive money.
            liquidity_amount_currency = self.amount
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

        if self.receipt_type_id.category == 'misc':
            liquidity_line_name = self.description or '' + _(' Misc Receipt From %s ', self.journal_id.name)
        elif self.receipt_type_id.category == 'rcv':
            liquidity_line_name = self.description or '' + _(' Payment Receipt from %s ', self.journal_id.name)
        else:
            liquidity_line_name = self.name

        debit_receive = credit_receive = []
        if self.misc_type == 'receive' and self.journal_group == 'split':
            debit_receive = self.journal_id.payment_credit_account_id.id \
                                if liquidity_balance < 0.0 \
                                else self.journal_id.payment_debit_account_id.id,
            credit_receive = self.destination_account_id.id,
        elif self.misc_type == 'payment' and self.journal_group == 'split':
            debit_receive = self.destination_account_id.id,
            credit_receive = self.journal_id.payment_credit_account_id.id \
                                 if liquidity_balance > 0.0 \
                                 else self.journal_id.payment_debit_account_id.id,
        elif self.misc_type == 'receive' and self.journal_group == 'merge':
            debit_receive = self.journal_id.payment_credit_account_id.id \
                                if liquidity_balance < 0.0 \
                                else self.journal_id.payment_debit_account_id.id,
            credit_receive = self.misc_partner_id.property_account_receivable_id.id
        elif self.misc_type == 'payment' and self.journal_group == 'merge':
            debit_receive = self.misc_partner_id.property_account_receivable_id.id
            credit_receive = self.journal_id.payment_credit_account_id.id \
                                 if liquidity_balance > 0.0 \
                                 else self.journal_id.payment_debit_account_id.id,

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
                'account_id': debit_receive,
                'ref': self.description,
                'analytic_account_id': self.analytic_account_id.id,
            },
            # Receivable
            {
                'name': self.name,
                'date_maturity': self.transaction_date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'account_id': credit_receive,
                'ref': self.description,
                'analytic_account_id': self.analytic_account_id.id,
            },
        ]
        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name'),
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'account_id': write_off_line_vals.get('account_id'),
                'analytic_account_id': self.analytic_account_id.id,
            })
        return line_vals_list

    @api.model_create_multi
    def create(self, vals):
        # OVERRIDE
        write_off_line_vals_list = []
        for val in vals:
            # print(val, 'masuk', self)
            if val.get('misc_name', 'New') == 'New' and val.get('misc_type') == 'receive':
                val['misc_name'] = self.env['ir.sequence'].next_by_code('miscellaneous.receipt') or '/'
            if val.get('misc_name', 'New') == 'New' and val.get('misc_type') == 'payment':
                val['misc_name'] = self.env['ir.sequence'].next_by_code('miscellaneous.payment') or '/'
            if 'journal_id' not in val:
                val['journal_id'] = self._get_default_journal().id
            if 'currency_id' not in val:
                journal = self.env['account.journal'].browse(val['journal_id'])
                val['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
            if val.get('amount', '0') == 0:
                raise UserError(
                    _(
                        "the Amount Misc must greater than 0"
                    )
                )
            # Hack to add a custom write-off line.
            write_off_line_vals_list.append(val.pop('write_off_line_vals', None))

            # Force the move_type to avoid inconsistency with residual 'default_move_type' inside the context.
            val['move_type'] = 'entry'
            val['name'] = '/'

        misc = super().create(vals)

        for i, pay in enumerate(misc):
            write_off_line_vals = write_off_line_vals_list[i]
            to_write = {'id': pay.id}
            for k, v in vals[i].items():
                if k in self._fields and self._fields[k].store and k in pay.move_id._fields \
                        and pay.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                        pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

            if pay.reserve_amount < 0:
                raise ValidationError('Available Amount cannot be negative')
            pay.move_id.write(to_write)
        return misc

    def _synchronize_to_moves(self, changed_fields):
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in (
                'date', 'amount', 'receipt_type_id', 'currency_id', 'partner_id', 'destination_account_id',
                'partner_bank_id', 'journal_id', 'description', 'journal_group',
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
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })

    def action_misc_receipt_matching_widget(self):
        ''' Open the manual reconciliation widget for the current payment.
        :return: A dictionary representing an action.
        '''
        self.ensure_one()
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.invoices.tree")])
        action = {
            'name': _("Paid Customer Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': True},
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id_form[0].id, 'tree'), (False, 'form')],
            'view_id ref="ins_miscellaneous.applied_invoices_tree_view"': '',
        }
        if len(self.invoice_ids) == 1:
            print(self.invoice_ids.id)
            action.update({
                'view_mode': 'list',
                'domain': [('id', 'in', [self.invoice_ids.id])],
            })
        elif len(self.invoice_ids) >= 1:
            ids = []
            for rec in self.invoice_ids:
                ids.append(rec["id"])
            print(ids)
            action.update({
                'view_mode': 'list',
                'domain': [('id', 'in', ids)],
            })
        else:
            action.update({
                'view_mode': 'list',
                'domain': [('id', 'in', None)],
            })
        return action

    def action_applied_invoice(self):
        if not self.applied_customer_move_id and self.journal_group == 'split':
            raise UserError(
                _(
                    "Can't applied to invoice without applied to customer in Split Journal Type, Please applied to "
                    "customer Firstly "
                )
            )
        elif (self.applied_customer_move_id and self.journal_group == 'split') or (
                not self.applied_customer_move_id and self.journal_group == 'merge'):
            view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.invoices.form")])
            return {
                'name': _('Applied Receipt to Customer Invoice'),
                'res_model': 'applied.invoices',
                'view_mode': 'form',
                'context': {
                    'active_model': 'miscellaneous.miscellaneous',
                    'active_ids': self.ids,
                    'default_misc_id': self.id,
                    'default_misc_type': self.misc_type,
                },
                'views': [(view_id_form[0].id, 'form')],
                'view_id ref="ins_miscellaneous.applied_invoices_tree_view"': '',
                'target': 'new',
                'type': 'ir.actions.act_window',
            }

    def action_unapplied_invoice(self):
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.invoices.form")])
        return {
            'name': _('Unapplied Customer Invoice'),
            'res_model': 'applied.invoices',
            'view_mode': 'form',
            'context': {
                'active_model': 'miscellaneous.miscellaneous',
                'active_ids': self.ids,
            },
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.applied_invoices_tree_view"': '',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_misc_payment_matching_widget(self):
        ''' Open the manual reconciliation widget for the current payment.
        :return: A dictionary representing an action.
        '''
        self.ensure_one()
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.bill.form")])
        action = {
            'name': _("Paid Vendor Bills"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'tree')],
            'view_id ref="ins_miscellaneous.applied_bill_tree_view"': '',
        }
        if len(self.invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            })
        elif len(self.invoice_ids) >= 1:
            ids = []
            for rec in self.invoice_ids:
                ids.append(rec["id"])
            print(ids)
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', ids)],
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.invoice_ids.id)],
            })
        return action

    def action_applied_bill(self):
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.bill.form")])
        return {
            'name': _('Applied Payment to Vendor Bill'),
            'res_model': 'applied.invoices',
            'view_mode': 'form',
            'context': {
                'active_model': 'miscellaneous.miscellaneous',
                'active_ids': self.ids,
                'default_misc_id': self.id,
                'default_misc_type': self.misc_type,
            },
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.applied_bill_tree_view"': '',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_unapplied_bill(self):
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.bill.form")])
        return {
            'name': _('Unapplied Vendor Bill'),
            'res_model': 'applied.invoices',
            'view_mode': 'form',
            'context': {
                'active_model': 'miscellaneous.miscellaneous',
                'active_ids': self.ids,
            },
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.applied_bill_tree_view"': '',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_applied_to_partner(self):
        applied_partner = self.env['applied.customer']
        print(self.misc_partner_id)
        if self.applied_customer_move_id or self.journal_group == 'merge':
            raise UserError(
                _(
                    "the Receipt is already applied to customer"
                )
            )
        if not self.misc_partner_id:
            raise UserError(
                _(
                    "the customer or vendor partner must be fill. please select customer or vendor partner firstly"
                )
            )
        elif self.misc_partner_id and self.journal_group == 'split':
            vals_list = [
                # values applied to customer
                {
                    'misc_id': self.id,
                    'company_id': self.company_id.id,
                    'journal_id': self.applied_customer_journal_id.id,
                    'date': self.applied_partner_date,
                },
            ]
            applied_partner.create(vals_list)
        return applied_partner

    def action_applied_invoice_bulky(self):
        if not self.applied_customer_move_id and self.journal_group == 'split':
            raise UserError(
                _(
                    "Can't applied to invoice without applied to customer in Split Journal Type, Please applied to "
                    "customer Firstly "
                )
            )
        elif (self.applied_customer_move_id and self.journal_group == 'split') or (
                not self.applied_customer_move_id and self.journal_group == 'merge'):
            for line in self.invoice_ids:
                print(line)
                if line.state == 'draft':
                    line.action_applied_invoice()
