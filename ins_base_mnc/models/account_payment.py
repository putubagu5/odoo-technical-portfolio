from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    valid_partner_ids = fields.Many2many('res.partner', string='Valid Partner',
                                         compute='_compute_valid_partner_ids')
    partner_id = fields.Many2one(domain='[("id", "in", valid_partner_ids)]')
    is_check = fields.Boolean('Is Check', compute='_compute_is_check',
                              store=False)
    site_id = fields.Many2one('vendor.site', 'Vendor Site')  # NOTE: deprecated
    sites_id = fields.Many2one('res.sites', 'Vendor Site')
    journal_id = fields.Many2one(
        'account.journal', string='Bank Account',
        copy=False, check_company=True, index=True)
    check_no = fields.Char('Check Number')
    cf_activity_id = fields.Many2one('cashflow.activity', 'CF Activity')
    is_batch = fields.Boolean('Batch?', default=False)
    assignee_id = fields.Many2one('res.assignee', 'Assignee')
    reconciliation_date = fields.Date(string="Reconciliation Date")
    check_master_id = fields.Many2one('res.check', 'Check Series',
                                      domain='[("journal_id", "=", journal_id)]')
    check_id = fields.Many2one(
        'res.check.line', 'Check No',
        domain='[("check_id", "=", check_master_id), ("is_used", "=", False), ("cancelled", "=", False)]')
    document_ref = fields.Char('Document Ref.')
    acc_name = fields.Char('Acc. Name')
    acc_number = fields.Char('Acc. Number')
    acc_bank = fields.Char('Bank Name')
    date_paid = fields.Date('Paid Date')
    multi_payment_reference = fields.Char('Payment References',
                                          compute='_compute_payment_references',
                                          store=True)
    date_bank_statement = fields.Date('Bank Statement Date',
                                      compute='_compute_date_bank_statement',
                                      store=True)
    bank_statement_name = fields.Char('Bank Statement Name',
                                      compute='_compute_date_bank_statement',
                                      store=True)
    remittance_flag = fields.Boolean('Remitted ?', default=False)
    remittance_date = fields.Date('Remitted Date')
    un_remittance_date = fields.Date('Un-Remitted Date')
    type_payment = fields.Selection([
        ('quick', 'Quick'),
        ('manual', 'Manual'),
    ], 'Payment Type', default='quick')
    match_statement_line_ids = fields.Many2many('account.bank.statement.line',
                                                relation='bank_statement_line_matched_payment_rel',
                                                domain='[("cancel_reversal", "=", False)]')
    series_code = fields.Char('Code', compute='_compute_series_code', store=True)
    company_currency_id = fields.Many2one('res.currency', 'Company Currency',
                                          compute='_compute_amount_move_idr')
    amount_move_idr = fields.Monetary(
        'Amount (IDR)', compute='_compute_amount_move_idr',
        currency_field='company_currency_id')
    bank_address = fields.Char('Bank Address')
    swift_code = fields.Char('Swift Code')
    notes = fields.Char('Berita')
    draft_bank_statement = fields.Boolean('Added to Bank Statement', default=False,
                                          compute='_compute_draft_bank_statement', store=True)
    assignee1_id_slip = fields.Many2one('res.assignee.payment', 'Assignee I')
    assignee2_id_slip = fields.Many2one('res.assignee.payment', 'Assignee II')

    assignee1_id_check = fields.Many2one('res.assignee.payment', 'Assignee I')
    assignee2_id_check = fields.Many2one('res.assignee.payment', 'Assignee II')

    def _default_check_by_id(self):
        """ compute function to get the default assignee per company (only 1) """
        return self.env['res.assignee.payment'].search(
            [('doc_position', '=', 'Check By'), ('company_ids', 'in', self.env.company.id)], limit=1).id

    def _default_assignee_1(self):
        """ compute function to get the default assignee per company (only 1) """
        return self.env['res.assignee.payment'].search(
            [('doc_position', '=', 'Approve I'), ('company_ids', 'in', self.env.company.id)], limit=1).id

    def _default_assignee_2(self):
        """ compute function to get the default assignee per company (only 1) """
        return self.env['res.assignee.payment'].search(
            [('doc_position', '=', 'Approve II'), ('company_ids', 'in', self.env.company.id)], limit=1).id

    def _default_assignee_3(self):
        """ compute function to get the default assignee per company (only 1) """
        return self.env['res.assignee.payment'].search(
            [('doc_position', '=', 'Approve III'), ('company_ids', 'in', self.env.company.id)], limit=1).id

    check_by_id_approve = fields.Many2one('res.assignee.payment', 'Check By', default=_default_check_by_id)
    assignee1_id_approve = fields.Many2one('res.assignee.payment', 'Approve I', default=_default_assignee_1)
    assignee2_id_approve = fields.Many2one('res.assignee.payment', 'Approve II', default=_default_assignee_2)
    assignee3_id_approve = fields.Many2one('res.assignee.payment', 'Approve III', default=_default_assignee_3)

    @api.depends('match_statement_line_ids', 'match_statement_line_ids.cancel_reversal')
    def _compute_draft_bank_statement(self):
        """ compute function to get the draft_bank_statement of bank statement (only 1) """
        reverse_move = self.env["account.bank.statement.line"].search([('matched_payment_ids', '!=', False)])
        self.draft_bank_statement = False
        for rec in reverse_move:
            if rec and rec.cancel_reversal and rec.matched_payment_ids.draft_bank_statement:
                # print(rec.matched_payment_ids.id, rec.cancel_reversal, 'nilai statement1')
                rec.matched_payment_ids.draft_bank_statement = False
            elif rec and not rec.cancel_reversal \
                    and not rec.matched_payment_ids.draft_bank_statement:
                # print(rec.matched_payment_ids.id, rec.cancel_reversal, 'nilai statement2')
                rec.matched_payment_ids.draft_bank_statement = True

        # for rec in self:
        #     stmt = rec.reconciled_statement_ids.line_ids.filtered(lambda x: x.cancel_reversal)
        #     print(stmt[0].cancel_reversal,'nilai statement')
        #     if stmt and stmt[0].cancel_reversal:
        #         rec.draft_bank_statement = False
        #     elif stmt and not stmt[0].cancel_reversal:
        #         rec.draft_bank_statement = True
        #     else:
        #         rec.draft_bank_statement = False

    @api.depends('partner_type')
    def _compute_valid_partner_ids(self):
        """ compute function to get all valid partner based on partner_type """
        for rec in self:
            domain = [
                '|',
                ('parent_id', '=', False),
                ('is_company', '=', True),
            ]
            if rec.partner_type == 'customer':
                domain += [('customer_rank', '>', 0)]
            if rec.partner_type == 'supplier':
                domain += [('supplier_rank', '>', 0)]
            rec.valid_partner_ids = self.env['res.partner'].search(domain)

    @api.depends('move_id', 'company_id')
    def _compute_amount_move_idr(self):
        """ compute function to get Amount in IDR """
        for rec in self:
            amount = 0
            currency_id = rec.company_id.currency_id.id

            if rec.move_id:
                amount = sum(rec.move_id.line_ids.mapped('debit'))

            rec.amount_move_idr = amount
            rec.company_currency_id = currency_id

    @api.depends('check_master_id', 'payment_doc_master_id', 'giro_master_id')
    def _compute_series_code(self):
        """ compute function to get series_code """
        for rec in self:
            series_code = []
            if rec.payment_doc_master_id:
                series_code.append(rec.payment_doc_master_id.code)
            if rec.giro_master_id:
                series_code.append(rec.giro_master_id.code)
            if rec.check_master_id:
                series_code.append(rec.check_master_id.code)
            rec.series_code = ','.join(map(str, series_code))

    @api.depends('move_id.line_ids.amount_residual', 'move_id.line_ids.amount_residual_currency')
    def _compute_reconciliation_status(self):
        ''' Compute the field indicating if the payments are already reconciled with something.
        This field is used for display purpose (e.g. display the 'reconcile' button redirecting to the reconciliation
        widget).
        '''
        for pay in self:
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
            if not pay.currency_id or not pay.id:
                pay.is_reconciled = False
                pay.is_matched = False
            elif pay.currency_id.is_zero(pay.amount):
                pay.is_reconciled = True
                pay.is_matched = True
            else:
                # The journal entry seems reconciled.
                residual_field = 'amount_residual' if pay.currency_id == pay.company_id.currency_id else 'amount_residual_currency'
                reconcile_lines = (counterpart_lines + writeoff_lines).filtered(lambda line: line.account_id.reconcile)
                payment = self.env["account.move"].search([('reversed_entry_id', '=', pay.move_id.id)], limit=1)
                if pay.reverse_date or payment:
                    pay.is_reconciled = False
                    pay.is_matched = False
                    pay.cancel_reversal = True
                else:
                    pay.is_reconciled = pay.currency_id.is_zero(sum(reconcile_lines.mapped(residual_field)))
                    pay.is_matched = pay.currency_id.is_zero(sum(liquidity_lines.mapped(residual_field)))

    @api.depends('reconciled_statement_ids')
    def _compute_date_bank_statement(self):
        """ compute function to get the date of bank statement (only 1) """
        for rec in self:
            stmt = rec.reconciled_statement_ids.filtered(lambda x: x.date)
            if stmt:
                rec.date_bank_statement = stmt[0].date if stmt[0].date else False
                rec.bank_statement_name = stmt[0].name if stmt[0].name else False
            else:
                rec.date_bank_statement = False
                rec.bank_statement_name = False

    @api.depends('journal_id')
    def _compute_operating_unit_id(self):
        """ override compute function to assign Operating Unit from User """
        for payment in self:
            if payment.journal_id:
                payment.operating_unit_id = payment.journal_id.operating_unit_id
            else:
                # take from user the operating unit
                user_ou = self.env.user.operating_unit_ids
                if user_ou:  # get only the first one found
                    payment.operating_unit_id = user_ou[0].id

    @api.onchange('check_master_id')
    def _onchange_check_master(self):
        """ onchange function to set check_id with the first record """
        self.ensure_one()
        if self.check_master_id and self.check_master_id.line_ids:
            first = self.check_master_id.line_ids.sorted(key=lambda x: x.name)
            first = first.filtered(lambda x: not x.is_used and not x.cancelled)
            if first:
                self.check_id = first[0].id
            else:
                raise ValidationError('This series has no usable Check Number')

    # @api.onchange("journal_id")
    # def _onchange_journal_id(self):
    #     res = {
    #         'domain': {
    #             'check_id': [
    #                 ('journal_id', '=', self.journal_id.id)
    #                 ]
    #         }
    #     }
    #     return res

    @api.onchange('check_id')
    def _onchange_check_id(self):
        """ onchange function to set check_no """
        self.ensure_one()
        if self.check_id:
            self.check_no = self.check_id.name

    @api.model_create_multi
    @api.depends('manual_currency_rate_active', 'manual_currency_rate',
                 'amount', 'currency_id','state')
    def _depends_manual_rate(self):
        """ depends function to set rate """
        print('masuk depends sini ?')
        self.ensure_one()
        company = self.env.company
        comp_curr = company.currency_id
        for rec in self:
            if rec.is_internal_transfer:
                rec.amount = comp_curr._convert(rec.amount, rec.currency_id, company, rec.date)

    @api.onchange('manual_currency_rate_active', 'manual_currency_rate',
                  'amount', 'currency_id', 'payment_invoice_ids')
    def _onchange_manual_rate(self):
        """ onchange function to set rate """
        self.ensure_one()

        company = self.env.company
        comp_curr = company.currency_id
        amt = sum(self.payment_invoice_ids.mapped('amount'))
        self.amount = comp_curr._convert(amt, self.currency_id, company, self.date)

    @api.onchange('partner_id')
    def onchange_partner_id_site(self):
        domain = [
            ('partner_id', '=', self.partner_id.id),
        ]
        sites = self.env['res.sites'].search(domain)
        if self.partner_id and sites:
            self.sites_id = sites[0].id

    @api.constrains('check_no', 'batch_payment_id', 'journal_id')
    def _check_number_and_batch(self):
        """ constrains function to check check_no in batch or payment """
        # the context is used to bypass the constrains to check payment
        # due to the mass assignment of check number from batch
        bypass = self._context.get('bypass', False)
        if not bypass:  # only process if not bypass
            for rec in self:
                # check payment records
                domain = [
                    ('id', '!=', rec.id),
                    ('journal_id', '=', rec.journal_id.id),
                    ('check_no', '=', rec.check_no),
                    ('check_no', '!=', False),
                ]
                payment = self.env['account.payment'].search(domain)
                # this is valid for payment only without batch
                if payment and not rec.batch_payment_id:
                    raise ValidationError('Check Number is already used!')

                # forcibly check payment batch
                domain = [
                    ('journal_id', '=', rec.journal_id.id),
                    ('check_no', '=', rec.check_no),
                    ('check_no', '!=', False),
                ]
                batch = self.env['account.batch.payment'].search(domain)
                if batch:
                    raise ValidationError('Check Number is already used!')

    @api.onchange('amount_payment_invoice')
    def _onchange_amount_total(self):
        for rec in self:
            rec.amount = rec.amount_payment_invoice

    @api.constrains('payment_invoice_ids', 'amount')
    def _check_payment_invoice_ids(self):
        """ override function to remove checking """
        # NOTE: this is to remove validation
        for rec in self:
            pass

    @api.depends('payment_method_id', 'document_ref', 'document_no', 'payment_doc_id', 'check_id',
                 'check_no', 'check_number', 'giro_no', 'giro_id')
    def _compute_payment_references(self):
        """ compute function to get payment references from multiple fields """
        for rec in self:
            result = []
            if rec.payment_method_id.name == 'Manual':
                if rec.document_ref:
                    result.append(rec.document_ref)
                if rec.document_no:
                    result.append(rec.document_no)
                if rec.payment_doc_id:
                    result.append(rec.payment_doc_id.name)
            elif rec.payment_method_id.name == 'Checks':
                if rec.check_id:
                    result.append(rec.check_id.name)
                if rec.check_no:
                    result.append(rec.check_no)
                if rec.check_number:
                    result.append(rec.check_number)
            elif rec.payment_method_id.name == 'Giro':
                if rec.giro_no:
                    result.append(rec.giro_no)
                if rec.giro_id:
                    result.append(rec.giro_id.name)
            # else:
            #     record.ref_receipt = ''
            # if rec.document_ref:
            #     result.append(rec.document_ref)
            # if rec.document_no:
            #     result.append(rec.document_no)
            # if rec.payment_doc_id:
            #     result.append(rec.payment_doc_id.name)
            # if rec.check_id:
            #     result.append(rec.check_id.name)
            # if rec.check_no:
            #     result.append(rec.check_no)
            # if rec.check_number:
            #     result.append(rec.check_number)
            # if rec.giro_no:
            #     result.append(rec.giro_no)
            # if rec.giro_id:
            #     result.append(rec.giro_id.name)
            rec.multi_payment_reference = ', '.join(list(set(result)))

    @api.depends('batch_payment_id', 'payment_method_id')
    def _compute_is_check(self):
        """ compute function to check if payment batch is check """
        for rec in self:
            batch = rec.batch_payment_id
            payment = rec.payment_method_id
            rec.is_check = payment.code == 'check_printing' or (batch and batch.is_check)

    def _has_check_no(self):
        """ helper function to check if record has valid check_no already """
        # valid check_no is check connected to this record
        domain = [
            ('check_id.journal_id', '=', self.journal_id.id),
            ('payment_id', '=', self.id),
        ]
        check = self.env['res.check.line'].search_count(domain)
        return check

    def button_check(self):
        """ function to check check_no existence and generate """
        # quit if record has check_no
        if self._has_check_no():
            return True

        # find unused check data with same journal
        domain = [
            ('check_id.journal_id', '=', self.journal_id.id),
            ('is_used', '=', False),
        ]
        check = self.env['res.check.line'].search(domain, limit=1, order='name')

        if check:
            self.check_no = check.name  # assign if found
            check.write({'payment_id': self.id})  # then write to use
        else:  # check runs out of usable number, raise error
            raise ValidationError('There is no more usable Check Number')

        return True

    def button_to_confirm(self):
        """ inherit function to assign payment_id to check record """
        super(AccountPayment, self).button_to_confirm()
        for rec in self:
            if rec.check_no:  # check number exists
                # find check number with journal and update
                domain = [
                    ('check_id.journal_id', '=', rec.journal_id.id),
                    ('name', '=', rec.check_no),
                ]
                check = self.env['res.check.line'].search(domain)
                if check:  # insert the payment_id
                    check.write({'payment_id': rec.id})
        return True

    def action_post(self):
        """ inherit function to assign payment_id to check record """
        super(AccountPayment, self).action_post()
        if self.payment_invoice_ids.filtered(lambda r: r.amount <= 0):
            raise ValidationError('There is negative amount on invoice!')
        for rec in self:
            if rec.check_no:  # check number exists
                # find check number with journal and update
                domain = [
                    ('check_id.journal_id', '=', rec.journal_id.id),
                    ('name', '=', rec.check_no),
                ]
                check = self.env['res.check.line'].search(domain)
                if check:  # insert the payment_id
                    check.write({'payment_id': rec.id})
        return True

    # def _prepare_move_line_default_vals(self, write_off_line_vals=None):
    #     """ inherit function prepare move line to check cash or bank journal """
    #     super(AccountPayment, self)._prepare_move_line_default_vals()

    #     # HEAVY NOTE: this sucks
    #     if self.manual_currency_rate_active:
    #         self = self.with_context(override_currency_rate=self.manual_currency_rate)

    #     self.ensure_one()
    #     write_off_line_vals = write_off_line_vals or {}

    #     # Compute amounts.
    #     write_off_amount = write_off_line_vals.get('amount', 0.0)

    #     if self.payment_type == 'inbound':
    #         # Receive money.
    #         counterpart_amount = -self.amount
    #         write_off_amount *= -1
    #     elif self.payment_type == 'outbound':
    #         # Send money.
    #         counterpart_amount = self.amount
    #     else:
    #         counterpart_amount = 0.0
    #         write_off_amount = 0.0

    #     balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
    #     counterpart_amount_currency = counterpart_amount
    #     write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id, self.company_id,
    #                                                   self.date)
    #     write_off_amount_currency = write_off_amount
    #     currency_id = self.currency_id.id

    #     if self.is_internal_transfer:
    #         if self.payment_type == 'inbound':
    #             liquidity_line_name = _('Transfer to %s', self.journal_id.name)
    #         else:  # payment.payment_type == 'outbound':
    #             liquidity_line_name = _('Transfer from %s', self.journal_id.name)
    #     else:
    #         liquidity_line_name = self.payment_reference

    #     # Compute a default label to set on the journal items.

    #     payment_display_name = {
    #         'outbound-customer': _("Customer Reimbursement"),
    #         'inbound-customer': _("Customer Payment"),
    #         'outbound-supplier': _("Vendor Payment"),
    #         'inbound-supplier': _("Vendor Reimbursement"),
    #     }

    #     default_line_name = self.env['account.move.line']._get_default_line_name(
    #         payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
    #         self.amount,
    #         self.currency_id,
    #         self.date,
    #         partner=self.partner_id,
    #     )

    #     # check journal type to set account id.
    #     acc_id = None
    #     # print(self.journal_id.type, balance)
    #     if self.journal_id.type == 'cash' and balance < 0.0:
    #         acc_id = self.journal_id.default_account_id.id
    #     elif self.journal_id.type == 'cash' and balance >= 0.0:
    #         acc_id = self.journal_id.default_account_id.id

    #     if self.journal_id.type == 'bank' and balance < 0.0:
    #         acc_id = self.journal_id.payment_debit_account_id.id
    #     elif self.journal_id.type == 'bank' and balance >= 0.0:
    #         acc_id = self.journal_id.payment_credit_account_id.id

    #     line_vals_list = [
    #         # Liquidity line.
    #         {
    #             'name': liquidity_line_name or default_line_name,
    #             'date_maturity': self.date,
    #             'amount_currency': -counterpart_amount_currency,
    #             'currency_id': currency_id,
    #             'debit': balance < 0.0 and -balance or 0.0,
    #             'credit': balance > 0.0 and balance or 0.0,
    #             'partner_id': self.partner_id.id,
    #             'account_id': acc_id,
    #         },
    #         # Receivable / Payable.
    #         {
    #             'name': self.payment_reference or default_line_name,
    #             'date_maturity': self.date,
    #             'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
    #             'currency_id': currency_id,
    #             'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
    #             'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
    #             'partner_id': self.partner_id.id,
    #             'account_id': self.destination_account_id.id,
    #         }
    #     ]
    #     return line_vals_list

    # check create jurnal move if not line ids

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE LINE IDS IF NOT FOUND
        if vals_list:
            for vals in vals_list:
                if vals.get('date'):
                    search_period = [
                        ('date_start', '<=', vals['date']),
                        ('date_end', '>=', vals['date']),
                        ('payment_period_id.company_id.id', '=', self.env.company.id)
                    ]
                    receipts = self.env['payment.period.line'].search(search_period)
                    if receipts:
                        for period in receipts:
                            if period.state == 'close':
                                raise ValidationError('Failed, payment period close!')

        res = super(AccountPayment, self).create(vals_list)
        write_off_line_vals = None
        for i, pay in enumerate(res):
            to_write = {'payment_id': pay.id}
            if not pay.move_id.line_ids:
                print('masuk tidak ada move line', pay, self, self.move_id)
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                        res._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]
                print(to_write)
                pay.move_id.write(to_write)
        return res

    def write(self, vals):
        if vals.get('date'):
            search_period = [
                ('date_start', '<=', vals['date']),
                ('date_end', '>=', vals['date']),
                ('payment_period_id.company_id.id', '=', self.env.company.id)
            ]
            receipts = self.env['payment.period.line'].search(search_period)
            if receipts:
                for period in receipts:
                    if period.state == 'close':
                        raise ValidationError('Failed, payment period close!')
        # check value of payment amount, if payment amount is difference with journal amount, the journal amount will updated with payment amount
        # temporary comment --> ini siapa yang suka comment2 codingan tanpa cek impactnya, kalau comment2 codingan orang silahkan tulis apa alasannya dan tulis nama sebagai penanggung jawab, capek aku tiap perbaiki jadi balik2 error terus karena ada yang asal comment codingan orang atau ganti2 malah jadi error lagi.
        total_amount = 0
        for rec in self.payment_invoice_ids:
            if rec.amount:
                total_amount = total_amount + rec.amount
        if vals.get('amount') != total_amount and not vals.get('payment_invoice_ids') and self.state != 'posted':
            vals['amount'] = total_amount
        res = super(AccountPayment, self).write(vals)
        return res

    def _get_custom_report_url(self):
        """ helper function to construct a report url """
        self.ensure_one()
        ctx = self._context
        is_idr = ctx.get('type') == 'idr'
        url = ''
        domain = [
            ('model', '=', 'account.payment'),
            ('journal_id', '=', self.journal_id.id),
            ('company_ids', 'in', self.company_id.id),
            ('report_type', '=', self.payment_method_code),
            ('is_idr', '=', is_idr),
        ]
        config = self.env['report.config'].search(domain, limit=1)
        if config:
            url = '/report/pdf/%s/%s' % (config.report_id.report_name, self.id)
        else:
            code_type = dict(self.env['report.config']._fields['report_type']._description_selection(self.env))
            msg = 'No Config found for %s with type %s (currency %s)' % (
                self.journal_id.name, code_type.get(self.payment_method_code, ''),
                'IDR' if is_idr else 'Valas')
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
