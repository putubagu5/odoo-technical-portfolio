from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class Miscellaneous(models.Model):
    _inherit = 'miscellaneous.miscellaneous'

    cf_activity_id = fields.Many2one('cashflow.activity', 'CF Activity')
    assignee_id = fields.Many2one('res.assignee', 'Assignee')
    receipt_number = fields.Char('Receipt Number')
    doc_reference = fields.Text('Doc Reference')
    # remittance_flag = fields.Boolean('Remitted ?', default=False)
    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate', digits=(12, 4))
    journal_group = fields.Selection(
        selection=[
            ('split', 'Un-Indentify'),
            ('merge', 'Un-apply'),
        ], string='Journal Applied Group', default="split")
    applied_partner_account = fields.Many2one(
        'account.account', string='Un-Apply Account',
        store=True, related='misc_partner_id.property_account_receivable_id',
        help="Account Clearing Applied Partner Journal.")
    is_reconciled = fields.Boolean(string="Is Reconciled", store=True,
                                   compute='_compute_reconciliation_status',
                                   help="Technical field indicating if the Miscellaneous is already reconciled.")
    is_matched = fields.Boolean(string="Is Matched With a Bank Statement", store=True,
                                compute='_compute_reconciliation_status',
                                help="Technical field indicating if the Miscellaneous has been matched with a "
                                     "statement line.")
    match_statement_line_ids = fields.Many2many('account.bank.statement.line',
                                                relation='bank_statement_line_matched_misc_payment_rel',
                                                domain='[("cancel_reversal", "=", False)]')
    draft_bank_statement = fields.Boolean('Added to Bank Statement', default=False,
                                          compute='_compute_draft_bank_statement', store=True)
    remittance_flag = fields.Boolean('Remitted ?', default=False)
    remittance_date = fields.Date('Remitted Date')
    un_remittance_date = fields.Date('Un-Remitted Date')
    bank_address = fields.Char('Bank Address')
    swift_code = fields.Char('Swift Code')
    notes = fields.Char('Berita')

    @api.depends('match_statement_line_ids', 'match_statement_line_ids.cancel_reversal')
    def _compute_draft_bank_statement(self):
        """ compute function to get the draft_bank_statement of bank statement (only 1) """
        reverse_move = self.env["account.bank.statement.line"].search([('matched_misc_payment_ids', '!=', False)])
        self.draft_bank_statement = False
        for rec in reverse_move:
            if rec and rec.cancel_reversal and rec.matched_misc_payment_ids.draft_bank_statement:
                # print(rec.matched_misc_payment_ids.id, rec.cancel_reversal, 'nilai statement1')
                rec.matched_misc_payment_ids.draft_bank_statement = False
            elif rec and not rec.cancel_reversal \
                    and not rec.matched_misc_payment_ids.draft_bank_statement:
                # print(rec.matched_misc_payment_ids.id, rec.cancel_reversal, 'nilai statement2')
                rec.matched_misc_payment_ids.draft_bank_statement = True

    @api.onchange('journal_group')
    def _onchange_journal_group(self):
        if self.journal_group == 'split' and self.state == 'draft':
            self.misc_partner_id = False

    @api.onchange('misc_partner_id')
    def _onchange_misc_partner_id(self):
        default_journal = self.env['account.journal'].search([('is_applied_customer', '=', True)])
        if default_journal:
            self.applied_customer_journal_id = default_journal

    def _synchronize_to_moves(self, changed_fields):
        for pay in self:
            pay.move_id.write({
                'manual_currency_rate_active': pay.manual_currency_rate_active,
                'manual_currency_rate': pay.manual_currency_rate,
            })
        super(Miscellaneous, self)._synchronize_to_moves(changed_fields)

    def action_post(self):
        if self.manual_currency_rate_active:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)
        if self.invoice_ids.filtered(lambda r: r.invoice_amount_residual <= 0):
            raise ValidationError('There is negative amount on invoice!')
        return super(Miscellaneous, self).action_post()

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        if self.manual_currency_rate_active:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)
        return super(Miscellaneous, self)._prepare_move_line_default_vals(write_off_line_vals)

    @api.depends('move_id.line_ids.amount_residual', 'move_id.line_ids.amount_residual_currency', 'draft_bank_statement', 'match_statement_line_ids')
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
                if pay.draft_bank_statement:
                    for rec in pay.match_statement_line_ids:
                        if rec.move_id.state == 'posted' and not rec.cancel_reversal:
                            pay.is_matched = True
                else:
                    pay.is_matched = False
            else:
                # The journal entry seems reconciled.
                # liquidity_lines.filtered(lambda x: x.account_id.reconcile).remove_move_reconcile()
                residual_field = 'amount_residual' if pay.currency_id == pay.company_id.currency_id else 'amount_residual_currency'
                reconcile_lines = (counterpart_lines + writeoff_lines).filtered(lambda line: line.account_id.reconcile)
                # print(pay.currency_id.is_zero(sum(liquidity_lines.mapped(residual_field))), pay.draft_bank_statement, 'gara2 ini', pay.match_statement_line_ids.move_id.state == 'posted')
                pay.is_reconciled = pay.currency_id.is_zero(sum(reconcile_lines.mapped(residual_field)))
                if pay.draft_bank_statement:
                    for rec in pay.match_statement_line_ids:
                        if rec.move_id.state == 'posted' and not rec.cancel_reversal:
                            pay.is_matched = pay.currency_id.is_zero(sum(liquidity_lines.mapped(residual_field)))
                else:
                    pay.is_matched = False


    @api.constrains("bukti_potong", "misc_partner_id")
    def _check_bukti_potong(self):
        for rec in self:
            if rec.bukti_potong and rec.misc_partner_id:
                check_bukti_potong = self.search([
                    ('id', '!=', rec.id),
                    ('bukti_potong', '=', rec.bukti_potong),
                    ('misc_partner_id', '=', rec.misc_partner_id.id)
                ])
                if check_bukti_potong:
                    raise UserError(
                        _(
                            "Number bukti potong already exists in partner"
                        )
                    )

    def action_applied_invoice(self):
        if self.invoice_ids.filtered(lambda r: r.invoice_amount_residual <= 0):
            raise ValidationError('There is negative amount on invoice!')
        return super(Miscellaneous, self).action_applied_invoice()

    def action_applied_invoice_bulky(self):
        if self.invoice_ids.filtered(lambda r: r.invoice_amount_residual <= 0):
            raise ValidationError('There is negative amount on invoice!')
        return super(Miscellaneous, self).action_applied_invoice_bulky()

    @api.model
    def create(self, vals):
        if vals.get('date'):
            search_period = [
                ('date_start', '<=', vals['date']),
                ('date_end', '>=', vals['date']),
                ('receipt_period_id.company_id.id', '=', self.env.company.id)
            ]
            receipts = self.env['receipt.period.line'].search(search_period)
            if receipts:
                for period in receipts:
                    if period.state == 'close':
                        raise ValidationError('Failed, receipt period close!')
        return super(Miscellaneous, self).create(vals)
    
    def write(self, vals):
        if vals.get('date'):
            search_period = [
                ('date_start', '<=', vals['date']),
                ('date_end', '>=', vals['date']),
                ('receipt_period_id.company_id.id', '=', self.env.company.id)
            ]
            receipts = self.env['receipt.period.line'].search(search_period)
            if receipts:
                for period in receipts:
                    if period.state == 'close':
                        raise ValidationError('Failed, receipt period close!')
        return super(Miscellaneous, self).write(vals)
