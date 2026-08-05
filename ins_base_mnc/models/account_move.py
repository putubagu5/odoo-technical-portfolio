import json
from num2words import num2words
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning
from odoo.tools.misc import format_date


class AccountMove(models.Model):
    _inherit = "account.move"
    _order = 'date desc, name desc, id asc'  # NOTE: change order

    def _default_assignee_invoice(self):
        assignee = False
        assignee_default = self.env['res.assignee.invoice'].search([('is_default', '=', True), ('company_id.id', '=', self.env.user.company_id.id)], limit=1).id
        if assignee_default:
            assignee = assignee_default
        return assignee

    payment_reference = fields.Char('Bill/Invoice Ref.')
    other_reference = fields.Char(
        'Other Name', compute='_compute_other_reference',
        inverse='_inverse_other_reference')
    other_reference_manual = fields.Char('Other Name (Manual)', copy=False)
    full_apply_reference = fields.Char('Apply remarks', compute='compute_full_apply')
    amount_in_words = fields.Char('Amount To Words', compute='amount_to_text')
    amount_in_words_2 = fields.Char('Amount To Words 2', compute='amount_to_text_2')
    amount_due_in_words = fields.Char('Amount Due To Words', compute='amount_due_to_text')
    amount_due_in_words_2 = fields.Char('Amount Due To Words 2', compute='amount_due_to_text_2')
    purchase_vendor_bill_ids = fields.Many2many('purchase.order', 'bill_po_rel', string="Purchase Orders")
    purchase_picking_ids = fields.Many2many('stock.picking', 'bill_picking_rel', string="Receipts")
    account_move_prepayment_match_ids = fields.Many2many('account.move', copy=False,
                                                         string='Applied Invoices',
                                                         domain="[('bill_type', '=', 'prepayment')]",
                                                         compute='_get_applied_invoice_id')
    bill_type = fields.Selection([
        ('standard', "Standard"), ('prepayment', "Prepayment"), ('settlement', "Settlement")
    ], string="Bill Type", default='standard')
    prepayment_po_ref_id = fields.Many2one('purchase.order', string="PO Number", store=True)
    amount_outstanding_purchase = fields.Float(
        'Amount Outstanding PO', compute='_compute_amount_outstanding_purchase')
    apply_prepayment_id = fields.Many2one(
        'account.move', string="Apply",
        domain="[('bill_type', '=', 'prepayment'), ('id', 'not in', apply_prepayment_ids)]")
    apply_prepayment_ids = fields.Many2many(
        'account.move', 'rel_prepayment_saved', 'move_id', 'saved_id',
        string="Apply", domain="[('bill_type', '=', 'prepayment')]")  # NOTE: store the selected prepayment
    amount_prepayment_applied_for_settlement = fields.Float(default=0, string="Amount of Prepayment Applied for Settlement")
    is_full_applied_prepayment = fields.Boolean(default=False, string="Full Applied Prepayment", compute='_compute_applied_prepayment', store=True)
    rate = fields.Float('Rate', compute='_compute_rate')
    ref = fields.Char('Description', copy=True, required=False)
    ref_desc = fields.Text('Description', compute='_compute_description', store=True)
    assignee_id_invoice = fields.Many2one('res.assignee.invoice', 'Assignee (invoice)', default=_default_assignee_invoice)
    assignee_id_bill = fields.Many2one('res.assignee.bill', 'Assignee (bill)')
    po_numbers = fields.Char(string="PO Numbers", compute='_compute_po_numbers')
    rr_numbers = fields.Char(string="RR Numbers", compute='_compute_rr_numbers')
    prepayment_refs = fields.Char(string="Applied Invoices", compute='_compute_prepayments')
    # po_numbers_store = fields.Char(string="PO Numbers", compute='_compute_po_numbers_store', store=True)
    employee = fields.Many2one('hr.employee', string="Employee")
    employee_text = fields.Char(string='Employee')
    journal_reverse_id = fields.Many2one('account.move', compute='_compute_journal_reverse',
                                         string="Journal Reverse No")
    reconciliation_date = fields.Date(string="Reconciliation Date")
    ref_receipt = fields.Text('Receipt', compute='_compute_receipt_ref')
    ref_misc_receipt = fields.Text('Misc Receipt', compute='_compute_misc_receipt_ref')
    ref_payment = fields.Text('Payment', compute='_compute_payment_ref')
    ref_misc_payment = fields.Text('Misc Payment', compute='_compute_misc_payment_ref')
    amount_compare = fields.Float('Amount Compare')
    site_id = fields.Many2one('vendor.site', 'Vendor Site')  # NOTE: deprecated
    sites_id = fields.Many2one('res.sites', 'Vendor Site')
    invoice_payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms',
        check_company=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.ref('account.account_payment_term_immediate').id)
    mnc_payment_state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], 'Payment State', compute='_compute_mnc_payment_state', tracking=True)
    bills_date = fields.Date('Bill Date', compute='_compute_bill_invoice_date')
    invoices_date = fields.Date('Invoice Date', compute='_compute_bill_invoice_date')
    settlement_invoice = fields.Char('Settlement Invoice', compute='_compute_settlement_invoice')
    apply_prepayment_to_bill_ids = fields.One2many(
        'applied.prepayment.to.bill', 'invoice_id', string="Apply")
    settlement_to_bill_ids = fields.One2many(
        'applied.prepayment.to.bill', 'prepayment_id', string="Settle")

    def copy(self, default=None):
        self.ensure_one()

        # NOTE: disable duplicate if type is Vendor Bills and if record has
        # stock_move_gr_match_ids
        gr_match = self.invoice_line_ids.mapped('stock_move_gr_match_ids')
        if gr_match and self.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
            raise ValidationError('Cannot duplicate Vendor Bills that have GR Matching')

        default = dict(default or {})
        default.update({'ref': self.ref})

        return super(AccountMove, self).copy(default)

    @api.depends('bill_type', 'payment_reference','amount_prepayment_applied_for_settlement')
    def _compute_settlement_invoice(self):
        invoice_line = self.env['account.move.line']
        applied_ids = self.env['applied.prepayment.to.bill']
        for rec in self:
            settlement_invoice = ''
            settlement_invoice2 = ''
            record = invoice_line.search([('account_move_prepayment_match_id', '=', rec.id)])
            rec_invoice = applied_ids.search([('prepayment_id', '=', rec.id)])
            print(rec_invoice, 'settlement', self.settlement_to_bill_ids, ', '.join(self.settlement_to_bill_ids.invoice_id.mapped('payment_reference')))
            if rec.bill_type == 'prepayment' and record:
                settlement_invoice = ', '.join(record.mapped('move_id').mapped('payment_reference'))
                settlement_invoice2 = ', '.join(self.settlement_to_bill_ids.invoice_id.mapped('payment_reference'))
            rec.settlement_invoice = settlement_invoice + " " + settlement_invoice2

    @api.depends('prepayment_po_ref_id')
    def _compute_amount_outstanding_purchase(self):
        """ compute function to get outstanding amount """
        # rules:
        # from the prepayment_po_ref_id get all prepayment_move_ids, excluding
        # "this" record
        for rec in self:
            moves = (rec.prepayment_po_ref_id.prepayment_move_ids)
            amt_moves = sum(moves.mapped('amount_untaxed'))
            amt_purchase = rec.prepayment_po_ref_id.amount_untaxed
            rec.amount_outstanding_purchase = amt_purchase - amt_moves

    @api.depends('name', 'state')
    def name_get(self):
        result = []
        for move in self:
            if self._context.get('name_groupby'):
                name = '**%s**, %s' % (format_date(self.env, move.date), move._get_move_display_name())
                if move.ref:
                    name += '     (%s)' % move.ref
                if move.partner_id.name:
                    name += ' - %s' % move.partner_id.name
            else:
                name = move._get_move_display_name(show_ref=True)
            result.append((move.id, name + ' - %s' % move.full_apply_reference))
        return result

    @api.constrains('prepayment_po_ref_id', 'amount_untaxed', 'bill_type')
    def _check_purchase_amount_untaxed(self):
        """ constrains function to check if amount_untaxed < PO amount """
        for rec in self:
            if rec.prepayment_po_ref_id and rec.bill_type == 'prepayment':
                # we also need to find the same move with same prepayment
                domain = [
                    ('prepayment_po_ref_id', '=', rec.prepayment_po_ref_id.id),
                    ('bill_type', '=', 'prepayment'),
                    ('id', '!=', rec.id),
                ]
                other_moves = self.env['account.move'].search(domain)
                total = rec.amount_untaxed + sum(other_moves.mapped('amount_untaxed'))
                if rec.prepayment_po_ref_id.amount_untaxed < total:
                    raise ValidationError('Amount Bill must be less than PO')

    @api.constrains('invoice_date_due', 'invoice_date')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.invoice_date_due and self.invoice_date:
            if self.invoice_date > self.invoice_date_due:
                raise Warning('Invoice Date must be earlier or same than Due Date')

    @api.constrains('amount_total', 'prepayment_po_ref_id')
    def _check_prepayment(self):
        """ constrains function to check amount validity """
        for rec in self:
            if rec.amount_total > 0 and rec.prepayment_po_ref_id:
                if rec.amount_total > rec.prepayment_po_ref_id.amount_total:
                    raise Warning('Amount in invoice is more than amount prepayment.')

    @api.constrains('invoice_line_ids')
    def _check_exist_matched_prepayment_id(self):
        for rec in self:
            exist_matched_prepayment_id = []
            for line in rec.invoice_line_ids:
                if line.account_move_prepayment_match_id.id in exist_matched_prepayment_id:
                    raise ValidationError(_('Matched prepayment must be unique.'))
                exist_matched_prepayment_id.append(line.account_move_prepayment_match_id.id)

    @api.constrains('payment_reference', 'partner_id')
    def _check_duplicate_bill_invoice_ref(self):
        """ constrains to check duplicate of record with same name & journal """
        for rec in self:
            domain = [
                ('id', '!=', self.id),
                ('move_type', '!=', 'out_refund'),
                ('payment_reference', '=ilike', self.payment_reference),
                ('partner_id', '=', self.partner_id.id),
            ]
            line = rec.search(domain)
            if line:
                raise Warning('Bill/Invoice Ref already exist with same partner!')

    @api.model
    def _default_operating_unit_id(self):
        """ override function to set to False """
        return False

    @api.onchange('journal_id')
    def _onchange_journal(self):
        """ override onchange function to prevent OU setup """
        self.operating_unit_id = False

    @api.onchange('partner_id')
    def onchange_partner_id_site(self):
        domain = [
            ('partner_id', '=', self.partner_id.id),
        ]
        sites = self.env['res.sites'].search(domain)
        if self.partner_id and sites:
            self.sites_id = sites[0].id
        if self.partner_id:
            return {
                'domain': {
                    'prepayment_po_ref_id': [('partner_id', '=', self.partner_id.id), ('state', '=', 'purchase'), ('company_id', '=', self.company_id.id), ('show_prepayment', '=', True), ('state', '=', 'purchase'), ('amount_total', '!=', 0)],
                }
            }

    @api.depends('invoice_line_ids', 'invoice_line_ids.account_move_prepayment_match_id')
    def _get_applied_invoice_id(self):
        for rec in self:
            invoices = [(5, 0, 0)]
            invoices += [(4, x.account_move_prepayment_match_id.id) for x in rec.invoice_line_ids if x.account_move_prepayment_match_id]
            rec.account_move_prepayment_match_ids = invoices

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_mnc_payment_state(self):
        """ compute function to get mnc_payment_state """
        # rules:
        # 1. draft if no payment found (default)
        # 2. open if confirmed (posted) but no payment OR payment is void OR
        # cancelled payment
        # 3. in_payment if payment exists but no bank statement
        # 4. partial if payment exists and partially paid
        # 5. paid if all payments are paid
        for rec in self:
            total_to_pay = 0.0
            total_residual = 0.0
            currencies = rec._get_lines_onchange_currency().currency_id
            currency = len(currencies) == 1 and currencies or rec.company_id.currency_id

            for line in rec.line_ids:
                if rec.is_invoice(include_receipts=True):
                    if line.account_id.user_type_id.type in ('receivable', 'payable'):
                        total_to_pay += line.balance
                        total_residual += line.amount_residual

            # if move_type is not entry, set draft else False
            state = 'draft' if rec.move_type != 'entry' else False

            # record is invoice and posted, set to open, but check for payment
            if rec.is_invoice(include_receipts=True) and rec.state == 'posted':
                state = 'open'

                if currency.is_zero(rec.amount_residual):
                    reconciled_payments = rec._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        state = 'paid'
                    else:
                        state = 'in_payment'
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    state = 'partial'

            rec.mnc_payment_state = state
            # rec.payment_state = state

    @api.depends('ref')
    def _compute_description(self):
        for record in self:
            text = str(record.ref)
            record.ref_desc = text

    @api.depends('invoice_date')
    def _compute_bill_invoice_date(self):
        for record in self:
            record.bills_date = record.invoice_date
            record.invoices_date = record.invoice_date

    @api.depends('is_full_applied_prepayment')
    def compute_full_apply(self):
        for record in self:
            record.full_apply_reference = 'FULL APPLY' if record.is_full_applied_prepayment is True else ''

    @api.depends('payment_state', 'state')
    def _compute_journal_reverse(self):
        for record in self:
            record.journal_reverse_id = False
            moves = self.env["account.move"].search([("reversed_entry_id", "!=", False)])
            for rec in moves:
                if rec.reversed_entry_id.id == record.id:
                    record.journal_reverse_id = rec.id

    def _compute_misc_receipt_ref(self):
        for record in self:
            record.ref_misc_receipt = ''
            receipts = self.env["miscellaneous.miscellaneous"].search([
                ("move_id", "=", record.id),
                ("move_id.state", "=", "posted")])
            applied_receipts = self.env["miscellaneous.miscellaneous"].search([
                ("applied_customer_move_id", "=", record.id),
                ("applied_customer_move_id.state", "=", "posted")])
            rec_text = str(receipts.doc_reference)
            app_text = str(applied_receipts.doc_reference)
            if applied_receipts:
                record.ref_misc_receipt = app_text
            if receipts:
                if receipts.receipt_type_id.type == 'receive':
                    record.ref_misc_receipt = rec_text
                elif receipts.receipt_type_id.type == 'payment':
                    record.ref_misc_receipt = ''

    def _compute_misc_payment_ref(self):
        for record in self:
            record.ref_misc_payment = ''
            payment = self.env["miscellaneous.miscellaneous"].search([
                ("move_id", "=", record.id),
                ("move_id.state", "=", "posted")])
            pay_text = str(payment.doc_reference)
            if payment.receipt_type_id.type == 'receive':
                record.ref_misc_payment = ''
            elif payment.receipt_type_id.type == 'payment':
                record.ref_misc_payment = pay_text

    def _compute_receipt_ref(self):
        for record in self:
            record.ref_receipt = ''
            receipts = self.env["account.payment"].search([
                ("move_id", "=", record.id),
                ("move_id.state", "=", "posted")])
            man_text = str(receipts.payment_doc_id.name)
            cek_text = str(receipts.check_id.name)
            gro_text = str(receipts.giro_id.name)
            if receipts.partner_type == 'customer':
                if receipts.payment_method_id.name == 'Manual':
                    record.ref_receipt = man_text
                elif receipts.payment_method_id.name == 'Checks':
                    record.ref_receipt = cek_text
                elif receipts.payment_method_id.name == 'Giro':
                    record.ref_receipt = gro_text
                else:
                    record.ref_receipt = ''
            elif receipts.partner_type == 'supplier':
                record.ref_receipt = ''

    def _compute_payment_ref(self):
        for record in self:
            record.ref_payment = ''
            payment = self.env["account.payment"].search([
                ("move_id", "=", record.id),
                ("move_id.state", "=", "posted")])
            man_text = str(payment.payment_doc_id.name)
            cek_text = str(payment.check_id.name)
            gro_text = str(payment.giro_id.name)
            if payment.partner_type == 'customer':
                record.ref_payment = ''
            elif payment.partner_type == 'supplier':
                if payment.payment_method_id.name == 'Manual':
                    record.ref_payment = man_text
                elif payment.payment_method_id.name == 'Checks':
                    record.ref_payment = cek_text
                elif payment.payment_method_id.name == 'Giro':
                    record.ref_payment = gro_text
                else:
                    record.ref_payment = ''

    # @api.constrains('payment_reference')
    # def _check_payment_reference(self):
    #     """ constrains function to check payment reference """
    #     self.ensure_one()
    #     domain = [
    #         ('payment_reference', '=ilike', self.payment_reference),
    #         ('id', '!=', self.id),
    #     ]
    #     moves = self.env['account.move'].sudo().search(domain)
    #     if moves:  # other moves exist, join the name and show as error
    #         move_name_list = []
    #         for move in moves:
    #             if move.name:
    #                 move_name_list.append(move.name)
    #
    #         move_names = ', '.join(move_name_list)
    #         raise ValidationError('Payment Reference already exists in %s' % move_names)

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """ inherit function to add empty analytic assignment """
        res = super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount)
        # find line_ids with empty analytic_account_id
        # find analytic with is_default true and in the same company
        domain = [('is_default', '=', True), ('company_id', '=', self.company_id.id)]
        analytic = self.env['account.analytic.account'].search(domain, limit=1)
        for x in self.line_ids.filtered(lambda x: not x.analytic_account_id):
            x.analytic_account_id = analytic.id
        return res

    @api.constrains('payment_reference', 'move_type', 'partner_id', 'journal_id', 'invoice_date', 'state')
    def _check_duplicate_supplier_reference(self):
        """ override function to use payment_reference instead of ref """
        moves = self.filtered(
            lambda move: move.state == 'posted' and move.is_purchase_document() and move.payment_reference)
        if not moves:
            return

        self.env["account.move"].flush([
            "payment_reference", "move_type", "invoice_date", "journal_id",
            "company_id", "partner_id", "commercial_partner_id",
        ])
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
            SELECT move2.id
            FROM account_move move
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_partner partner ON partner.id = move.partner_id
            INNER JOIN account_move move2 ON
                move2.payment_reference = move.payment_reference
                AND move2.company_id = journal.company_id
                AND move2.commercial_partner_id = partner.commercial_partner_id
                AND move2.move_type = move.move_type
                AND (move.invoice_date is NULL OR move2.invoice_date = move.invoice_date)
                AND move2.id != move.id
            WHERE move.id IN %s
        ''', [tuple(moves.ids)])
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        if duplicated_moves:
            raise ValidationError(
                _('Duplicated vendor reference detected. You probably encoded twice the same vendor bill/credit note:\n%s') % "\n".join(
                    duplicated_moves.mapped(lambda m: "%(partner)s - %(payment_reference)s - %(date)s" % {
                        'payment_reference': m.payment_reference,
                        'partner': m.partner_id.display_name,
                        'date': format_date(self.env, m.invoice_date),
                    })
                ))

    @api.depends('invoice_line_ids', 'prepayment_po_ref_id', 'bill_type')
    def _compute_po_numbers(self):
        for record in self:
            po_number_list = []
            for line in record.invoice_line_ids:
                if line.purchase_order_id:
                    po_number_list.append(line.purchase_order_id.name)

            po_number_list = list(set(po_number_list))
            if record.prepayment_po_ref_id and record.bill_type == 'prepayment':
                po_number_list.append(record.prepayment_po_ref_id.name)
            po_number_list.sort()
            po_numbers = ', '.join(po_number_list)
            record.po_numbers = po_numbers

    @api.depends('invoice_line_ids', 'prepayment_po_ref_id', 'bill_type', 'other_reference_manual')
    def _compute_other_reference(self):
        for record in self:
            po_number_list = [x.purchase_order_id.other_name for x in record.invoice_line_ids if x.purchase_order_id and x.purchase_order_id.other_name]

            # make unique
            po_number_list = list(set(po_number_list))
            if record.prepayment_po_ref_id and record.bill_type == 'prepayment':
                po_number_list.append(record.prepayment_po_ref_id.other_name)

            po_number_list.sort()

            if po_number_list:
                po_numbers = ', '.join(map(str, po_number_list))
                record.other_reference = po_numbers if po_numbers else record.other_reference_manual
            else:
                record.other_reference = '' or record.other_reference_manual

    @api.onchange('other_reference')
    def _inverse_other_reference(self):
        """ inverse function to set other_reference """
        for rec in self:
            rec.other_reference_manual = rec.other_reference

    @api.depends('invoice_line_ids')
    def _compute_rr_numbers(self):
        for record in self:
            rr = ''
            rr_numbers = record.invoice_line_ids.mapped('purchase_order_id.picking_ids.name')
            rr = ', '.join(rr_numbers)
            record.rr_numbers = rr

    @api.depends('invoice_line_ids')
    def _compute_prepayments(self):
        for record in self:
            prep = ''
            prep_numbers = record.invoice_line_ids.mapped('account_move_prepayment_match_id.payment_reference')
            prep = ', '.join(prep_numbers)
            record.prepayment_refs = prep

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'cancel_reversal',
        'journal_reverse_id')
    def _compute_amount(self):
        """ inherit function to check is_reconciled and cancel_reversal """
        super(AccountMove, self)._compute_amount()
        for rec in self:
            currencies = rec._get_lines_onchange_currency().currency_id
            currency = len(currencies) == 1 and currencies or rec.company_id.currency_id
            if rec.is_invoice(include_receipts=True) and rec.state == 'posted':

                if currency.is_zero(rec.amount_residual):
                    reconciled_payments = rec._get_reconciled_payments()
                    if reconciled_payments and (all(reconciled_payments.mapped('is_reconciled')) or all(
                            reconciled_payments.mapped('is_matched'))):
                        new_pmt_state = 'paid'
                        rec.payment_state = new_pmt_state
            if rec.cancel_reversal or rec.journal_reverse_id:
                rec.payment_state = 'reversed'

    # @api.depends('po_numbers')
    # def _compute_po_numbers_store(self):
    #     for record in self:
    #         record.po_numbers_store = record.po_numbers

    @api.depends('invoice_date', 'manual_currency_rate_active', 'manual_currency_rate')
    def _compute_rate(self):
        """ compute function to calculate rate based on date or manual """
        for rec in self:
            if rec.manual_currency_rate_active:
                rec.rate = rec.manual_currency_rate
            else:
                lines = rec.currency_id.rate_ids.filtered(
                    lambda x: x.name <= (rec.invoice_date or rec.date))
                rec.rate = lines[0].actual_rate if lines else 0

    @api.depends('amount_total', 'currency_id')
    def amount_to_text(self):
        for rec in self:
            # lang = 'id' if self.currency_id.name == 'IDR' else 'en'
            lang = 'en'
            currency_in_words = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount = num2words(int(rec.amount_total), lang=lang)
            rec.amount_in_words = words_amount.title() + " " + currency_in_words

    @api.depends('amount_total', 'currency_id')
    def amount_to_text_2(self):
        for rec in self:
            lang_2 = 'id' if rec.currency_id.name == 'IDR' else 'en'
            currency_in_words_2 = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount_2 = num2words(int(rec.amount_total), lang=lang_2)
            rec.amount_in_words_2 = words_amount_2.title() + " " + currency_in_words_2

    @api.depends('amount_residual', 'currency_id')
    def amount_due_to_text_2(self):
        for rec in self:
            lang = 'id' if rec.currency_id.name == 'IDR' else 'en'
            currency_in_words = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount = num2words(int(rec.amount_residual), lang=lang)
            rec.amount_due_in_words_2 = words_amount.title() + " " + currency_in_words

    @api.depends('amount_residual', 'currency_id')
    def amount_due_to_text(self):
        for rec in self:
            lang = 'id' if rec.currency_id.name == 'IDR' else 'en'
            currency_in_words = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount = num2words(int(rec.amount_residual), lang=lang)
            rec.amount_due_in_words = words_amount.title() + " " + currency_in_words

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        """ inherit onchange function to set manual currency information """
        # purchase order found, set info
        if self.purchase_vendor_bill_id.purchase_order_id:
            po = self.purchase_vendor_bill_id.purchase_order_id
            self.manual_currency_rate_active = po.manual_currency_rate_active
            self.manual_currency_rate = po.manual_currency_rate

        # bypass self record to use context
        if self.manual_currency_rate_active:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)

        res = super(AccountMove, self)._onchange_purchase_auto_complete()
        return res

    def _get_move_line_price_unit(self, line_id):
        """ helper function to get price_unit of a line in _onchange_apply_prepayment """
        sql = """
            SELECT SUM(price_unit) AS price_unit
            FROM account_move_line
            WHERE account_move_line_prepayment_match_id = %s
        """ % (line_id)
        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchone()
        result = res and res.get('price_unit', 0) or 0
        return result

    @api.onchange('apply_prepayment_id')
    def _onchange_apply_prepayment(self):
        """ onchange function to set the invoice lines based on prepayment lines """
        for record in self:
            if record.apply_prepayment_id:
                for line in record.apply_prepayment_id.invoice_line_ids:
                    # copy data and set all necessary fields
                    copied_vals = line.copy_data()[0]
                    price_unit = copied_vals['price_unit']

                    # need to find the price_unit of the lines with same line.id
                    found_lines_price_unit = record._get_move_line_price_unit(line.id)
                    if found_lines_price_unit:  # found, subtract from price_unit
                        price_unit -= found_lines_price_unit

                    copied_vals['quantity'] = -copied_vals['quantity']
                    copied_vals['price_unit'] = price_unit
                    copied_vals['account_move_prepayment_match_id'] = line.move_id.id
                    copied_vals['account_move_line_prepayment_match_id'] = line.id
                    copied_vals['move_id'] = self.id

                    # create a new line based on this data
                    new_line = self.env['account.move.line'].sudo().new(copied_vals)
                    # new_line.write({'account_move_prepayment_match_id': line.move_id.id})
                    new_line._onchange_price_subtotal()
                    new_line.recompute_tax_line = True
                    new_line.account_move_prepayment_match_id = line.move_id.id

                record._onchange_recompute_dynamic_lines()

                # NOTE: add to apply_prepayment_ids to prevent selecting same record
                record.apply_prepayment_ids = [(4, record.apply_prepayment_id.id)]
                record.apply_prepayment_id = False  # empty the field

    @api.depends('amount_prepayment_applied_for_settlement')
    def _compute_applied_prepayment(self):
        """ compute function to calculate amount prepayment applied for settlement """
        for rec in self:
            if rec.amount_total_signed <= rec.amount_prepayment_applied_for_settlement:
                rec.is_full_applied_prepayment = True

    def _check_amount_compare(self):
        """ function to check amount_compare before posting """
        self.ensure_one()
        # rules: if amount != 0, then block
        if self.amount_compare != 0 and self.amount_compare != self.amount_total:
            raise ValidationError('Amount Compare is not same with Amount Total')

    def action_post(self):
        """ inherit function to check amount_compare before posting """
        self._check_amount_compare()

        super(AccountMove, self).action_post()
        available, rem_budget = True, 0.0
        if self.move_type == 'in_invoice':
            for line in self.invoice_line_ids:
                if self.env.company.budget_check_account_move and line.account_id and line.analytic_account_id:
                    budget_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
                        line.account_id, line.analytic_account_id.id, self.invoice_date)
                    if budget_id:
                        available, rem_budget = budget_id.check_budget_availability(line.price_subtotal)
                        if not available and not line.account_id.is_none_budget or not line.analytic_account_id.is_none_budget:
                            raise ValidationError(_("Budget is insuficcient."))
                    else:
                        if not line.account_id.is_none_budget or not line.analytic_account_id.is_none_budget:
                            raise ValidationError(_("There is no budget."))
        elif self.move_type == 'entry':
            for line in self.line_ids:
                if self.env.company.budget_check_account_move and line.account_id and line.analytic_account_id:
                    budget_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
                        line.account_id.id, line.analytic_account_id.id, self.invoice_date)
                    if budget_id and line.debit > 0.0:
                        available, rem_budget = budget_id.check_budget_availability(line.price_subtotal)
                        if not available and not line.account_id.is_none_budget or not line.analytic_account_id.is_none_budget:
                            raise ValidationError(_("Budget is insuficcient."))
                    else:
                        if not line.account_id.is_none_budget or not line.analytic_account_id.is_none_budget:
                            raise ValidationError(_("There is no budget."))
        for rec in self:
            if rec.state == 'posted':
                for line in rec.invoice_line_ids:
                    if line.account_move_prepayment_match_id:
                        if line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement >= line.account_move_line_prepayment_match_id.move_id.amount_total_signed:
                            raise ValidationError(_("Your Prepayment is Used, Please Change Prepayment with another prepayment."))
                        elif line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement < line.account_move_line_prepayment_match_id.move_id.amount_total_signed:
                            line.account_move_prepayment_match_id.amount_prepayment_applied_for_settlement += line.price_unit
                            line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement += line.price_unit

    def button_cancel(self):
        super(AccountMove, self).button_cancel()
        for rec in self:
            if rec.state == 'cancel':
                for line in rec.invoice_line_ids:
                    if line.account_move_prepayment_match_id:
                        line.account_move_prepayment_match_id.amount_prepayment_applied_for_settlement -= line.price_unit
                        line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement -= line.price_unit

    def button_draft(self):
        super(AccountMove, self).button_draft()
        for rec in self:
            if rec.state == 'draft':
                for line in rec.invoice_line_ids:
                    if line.account_move_prepayment_match_id:
                        line.account_move_prepayment_match_id.amount_prepayment_applied_for_settlement -= line.price_unit
                        line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement -= line.price_unit

    @api.onchange('bill_type')
    def _onchange_bill_type(self):
        for record in self:
            if record.move_type == 'in_invoice':
                if record.bill_type == 'standard':
                    journal_id = self.env['account.journal'].search([
                        ('type', '=', 'purchase'), ('purchase_type', '=', 'purchase')], limit=1)
                    if journal_id:
                        record.journal_id = journal_id.id
                        record.name = False
                    else:
                        raise ValidationError(_("Vendor Bill Journal not found."))
                elif record.bill_type == 'prepayment':
                    journal_id = self.env['account.journal'].search([
                        ('type', '=', 'purchase'), ('purchase_type', '=', 'prepayment')], limit=1)
                    if journal_id:
                        record.journal_id = journal_id.id
                    else:
                        raise ValidationError(_("Prepayment Journal not found."))
                elif record.bill_type == 'settlement':
                    journal_id = self.env['account.journal'].search([
                        ('type', '=', 'purchase'), ('purchase_type', '=', 'settlement')], limit=1)
                    if journal_id:
                        record.journal_id = journal_id.id
                    else:
                        raise ValidationError(_("Settlement Journal not found."))

    @api.onchange('prepayment_po_ref_id')
    def _onchange_prepayment_po_ref(self):
        for record in self:
            if record.prepayment_po_ref_id:
                # record.ref = record.prepayment_po_ref_id.name
                record.partner_id = record.prepayment_po_ref_id.partner_id
                record.sites_id = record.prepayment_po_ref_id.sites_id
            else:
                record.ref = False
            # record.prepayment_po_ref_id = False

    def _has_different_currency(self):
        """ helper function to check if any different currency in line """
        curr_lines = [x.currency_id.id for x in self.invoice_line_ids if x.currency_id]
        curr_invoice = self.currency_id.id
        return curr_invoice not in curr_lines and len(curr_lines) != 0

    @api.onchange('date', 'currency_id')
    def _onchange_currency(self):
        """ override function to show warning if user changes currency """
        # check if there is any different currency in line, empty if yes
        if self._has_different_currency():
            self.invoice_line_ids = [(2, x.id) for x in self.invoice_line_ids]
            self.line_ids = [(2, x.id) for x in self.line_ids]
        else:  # do as usual
            super(AccountMove, self)._onchange_currency()

    def gr_matching(self):
        self.ensure_one()
        return {
            'name': _("GR Matching"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'gr.matching.wizard',
            'target': 'new',
            'context': {
                'default_bill_id': self.id,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_company_id': self.company_id.id if self.company_id else False,
            },
        }

    def set_account_move_line_from_po(self, purchase_line_id, service_move):
        self.ensure_one()
        # find move_ids from purchase line and get the first number
        pmoves = purchase_line_id.move_ids
        pmoves = pmoves.filtered(lambda x: x.line_number)
        pmoves = pmoves[0].line_number if pmoves and pmoves[0] else ''
        tax_ids = [(6, False, purchase_line_id.product_id.supplier_taxes_id.ids)] if \
            purchase_line_id.product_id.supplier_taxes_id else False
        move_line = {
            'sequence': purchase_line_id.sequence,
            'name': '%s: %s' % (
                purchase_line_id.order_id.name, purchase_line_id.name),
            'product_id': purchase_line_id.product_id.id,
            'product_uom_id': purchase_line_id.product_uom.id,
            'quantity': service_move.quantity_to_billed,
            'price_unit': purchase_line_id.price_unit,
            'analytic_account_id': purchase_line_id.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, purchase_line_id.analytic_tag_ids.ids)],
            'purchase_line_id': purchase_line_id.id,
            'asset_cost_progress_id': purchase_line_id.asset_cost_progress_id.id,
            'purchase_line_number': purchase_line_id.line_number,
            'picking_line_number': pmoves,
            'po_line_gr_match_ids': [(4, purchase_line_id.id)],
            'tax_ids': tax_ids,
            'project_ids': [(6, 0, purchase_line_id.project_ids.ids)],
        }

        currency = purchase_line_id.order_id.currency_id
        account_id = purchase_line_id.product_id.property_account_expense_id
        if not account_id:
            raise ValidationError(_("Expense Account for product {} not found.".format(
                purchase_line_id.product_id.name)))
        move_line.update({
            'currency_id': currency and currency.id or self.env.user.company_id.currency_id.id,
            'date_maturity': self.invoice_date_due,
            'partner_id': purchase_line_id.order_id.partner_id.id,
            'account_id': account_id.id,
        })

        self.invoice_line_ids = [(0, False, move_line)]

    def set_account_move_line_from_gr_line(self, stock_move, picking_move):
        self.ensure_one()
        tax_ids = [(6, False, stock_move.product_id.supplier_taxes_id.ids)] if \
            stock_move.product_id.supplier_taxes_id else False
        move_line = {
            'sequence': stock_move.sequence,
            'name': '%s: %s' % (
                stock_move.picking_id.purchase_id.name, stock_move.name),
            'product_id': stock_move.product_id.id,
            'product_uom_id': stock_move.product_uom.id,
            'quantity': picking_move.quantity_to_billed,
            'price_unit': stock_move.purchase_line_id.price_unit,
            'analytic_account_id': stock_move.purchase_line_id.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, stock_move.purchase_line_id.analytic_tag_ids.ids)],
            'purchase_line_id': stock_move.purchase_line_id.id,
            'stock_picking_id': stock_move.picking_id.id,
            'stock_move_id': stock_move.id,
            'asset_cost_progress_id': stock_move.purchase_line_id.asset_cost_progress_id.id,
            'purchase_line_number': stock_move.purchase_line_id.line_number,
            'picking_line_number': stock_move.line_number,
            'stock_move_gr_match_ids': [(4, stock_move.id)],
            'tax_ids': tax_ids,
            'project_ids': [(6, 0, stock_move.project_ids.ids)],
        }

        if self.currency_id == stock_move.picking_id.company_id.currency_id:
            currency = False
        else:
            currency = stock_move.picking_id.purchase_id.currency_id

        if stock_move.product_id.categ_id.property_stock_account_input_categ_id:
            account_id = stock_move.product_id.categ_id.property_stock_account_input_categ_id
        else:
            account_id = False

        if not account_id:
            raise ValidationError(_("Stock Input Account for product {} not found.".format(stock_move.product_id.name)))
        move_line.update({
            'currency_id': currency and currency.id or self.env.user.company_id.currency_id.id,
            'date_maturity': self.invoice_date_due,
            'partner_id': stock_move.picking_id.purchase_id.partner_id.id,
            'account_id': account_id.id,
        })

        self.invoice_line_ids = [(0, False, move_line)]
        # stock_move.is_gr_matched = True

    def gr_matching_add_past_bill(self, bill_line):
        self.ensure_one()
        copied_vals = bill_line.copy_data()[0]
        copied_vals['move_id'] = self.id
        copied_vals['quantity'] = -copied_vals['quantity']
        self.invoice_line_ids = [(0, False, copied_vals)]

    def gr_matching_final_set(self):
        self.ensure_one()
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        refs = self._get_invoice_reference()
        self.ref = ', '.join(refs)

        self._onchange_currency()
        self.partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

    def _compute_payments_widget_to_reconcile_info(self):
        """ TOTAL OVERRIDE of function to add content """
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids \
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('parent_state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

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
                    'payment_references': '(%s)' % (line.payment_id.payment_id.multi_payment_reference) or '',
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

    def get_period_info(self):
        """ helper function to get the period data from date """
        from calendar import monthrange
        from datetime import date
        result = ['', '']
        if self.date:
            rg = monthrange(self.date.year, self.date.month)
            dstart = date(self.date.year, self.date.month, 1)
            dend = date(self.date.year, self.date.month, rg[1])
            result = [dstart.strftime('%d-%b-%Y'), dend.strftime('%d-%b-%Y')]
        return result

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        super(AccountMove, self)._compute_payments_widget_reconciled_info()
        for move_line in self.line_ids:
            # print(move_line, 'masuk sini belum', move_line.amount_residual, move_line.move_id.amount_residual)
            if move_line.move_id.amount_residual == 0 and move_line.full_reconcile_id and move_line.exclude_from_invoice_tab:
                # print(move_line.move_id._get_reconciled_payments(), "cek masuk cara odoo")
                if all(payment.date_bank_statement for payment in move_line.move_id._get_reconciled_payments()):
                    # print("masuk paid cara odoo")
                    move_line.move_id.payment_state = 'paid'
                elif move_line.move_id.mnc_payment_state != move_line.move_id.payment_state:
                    move_line.move_id.payment_state = move_line.move_id.mnc_payment_state
                else:
                    # print(move_line.full_reconcile_id, '1. harusnya inpayment masuk else soalnya karena belum semua recon')
                    move_line.move_id.payment_state = 'in_payment'
            elif move_line.move_id.state == 'posted' and move_line.move_id.amount_residual == 0 \
                    and not move_line.full_reconcile_id and move_line.exclude_from_invoice_tab:
                print(move_line.move_id.amount_residual, '2. harusnya in_payment')
                # move_line.move_id.payment_state = move_line.move_id.mnc_payment_state
                move_line.move_id.payment_state = 'in_payment'
            elif move_line.move_id.amount_residual > 0 and not move_line.product_id \
                    and move_line.move_id.amount_residual != move_line.move_id.amount_total_signed:
                # print(move_line.move_id.amount_residual, 'harusnya partial')
                move_line.move_id.payment_state = 'partial'
            elif move_line.move_id.amount_residual == move_line.move_id.amount_total_signed and move_line.exclude_from_invoice_tab:
                # print(move_line.amount_residual, 'harusnya not_paid')
                move_line.move_id.payment_state = 'not_paid'
            else:
                if not move_line.exclude_from_invoice_tab:
                    continue
                else:
                    move_line.move_id.payment_state = 'not_paid'

    def _compute_payments_widget_to_reconcile_info(self):
        super(AccountMove, self)._compute_payments_widget_to_reconcile_info()
        for move_line in self.line_ids:
            # print(move_line, 'masuk sini belum', move_line.amount_residual, move_line.move_id.amount_residual)
            if move_line.move_id.amount_residual == 0 and move_line.full_reconcile_id and move_line.exclude_from_invoice_tab:
                # print(move_line.move_id._get_reconciled_payments(), "cek masuk cara odoo")
                if all(payment.date_bank_statement for payment in move_line.move_id._get_reconciled_payments()):
                    # print("masuk paid cara odoo")
                    move_line.move_id.payment_state = 'paid'
                elif move_line.move_id.mnc_payment_state != move_line.move_id.payment_state:
                    move_line.move_id.payment_state = move_line.move_id.mnc_payment_state
                else:
                    # print(move_line.full_reconcile_id, '3. harusnya inpayment masuk else soalnya karena belum semua recon')
                    move_line.move_id.payment_state = 'in_payment'
            elif move_line.move_id.state == 'posted' and move_line.move_id.amount_residual == 0 \
                    and not move_line.full_reconcile_id and move_line.exclude_from_invoice_tab:
                # print(move_line.move_id.amount_residual, move_line.move_id.state, '4. harusnya in_payment')
                move_line.move_id.payment_state = move_line.move_id.mnc_payment_state
                # move_line.move_id.payment_state = 'in_payment'
            elif move_line.move_id.amount_residual > 0 and move_line.exclude_from_invoice_tab \
                    and move_line.move_id.amount_residual != move_line.move_id.amount_total_signed:
                # print(move_line.move_id.amount_residual, 'harusnya partial')
                move_line.move_id.payment_state = 'partial'
            elif move_line.move_id.amount_residual == move_line.move_id.amount_total_signed and move_line.exclude_from_invoice_tab:
                # print(move_line.amount_residual, 'harusnya not_paid')
                move_line.move_id.payment_state = 'not_paid'
            else:
                if not move_line.exclude_from_invoice_tab:
                    continue
                else:
                    move_line.move_id.payment_state = 'not_paid'

    @api.model
    def create(self, vals):
        default_move_type = vals.get('move_type') or self._context.get('default_move_type')
        if vals.get('date') and default_move_type:
            if default_move_type == 'entry':
                search_period = [
                    ('date_start', '<=', vals['date']),
                    ('date_stop', '>=', vals['date']),
                    ('company_id', '!=', False),
                ]
                journals = self.env['account.period'].search(search_period)
                if journals:
                    for period in journals:
                        if period.state == 'done' and period.company_id.id == self.env.company.id:
                            raise ValidationError('Failed, journal period close!')
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        default_move_type = vals.get('move_type') or self._context.get('default_move_type')
        if vals.get('date') and default_move_type:
            if default_move_type == 'entry':
                search_period = [
                    ('date_start', '<=', vals['date']),
                    ('date_stop', '>=', vals['date']),
                    ('company_id', '!=', False),
                ]
                journals = self.env['account.period'].search(search_period)
                if journals:
                    for period in journals:
                        if period.state == 'done' and period.company_id.id == self.env.company.id:
                            raise ValidationError('Failed, journal period close!')
        return super(AccountMove, self).write(vals)

    def action_applied_prepayment_to_bill(self):
        if self.state == 'posted':
            view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.prepayment.to.bill.form")])
            return {
                'name': _('Applied Prepayment to Vendor bill'),
                'res_model': 'applied.prepayment.to.bill',
                'view_mode': 'form',
                'context': {
                    'active_model': 'account.move',
                    'active_ids': self.ids,
                },
                'views': [(view_id_form[0].id, 'form')],
                'view_id ref="ins_base_mnc.applied_prepayment_to_bill_tree_view"': '',
                'target': 'new',
                'type': 'ir.actions.act_window',
            }

    def get_credit_note_data(self):
        """ helper function in report to show credit note data """
        # NOTE: the data consists of before, after, and difference
        # both for NET and PPN (amount_untaxed and amount_tax)
        # rules:
        # 1. get the invoice CN list: reversed_entry_id
        # 2. take the reversal_move_id.ids and store to use as index basis
        # 3. find the index of self.id, then loop
        # 4. in the loop, keep subtracting the Invoice amount_untaxed and amount_tax
        # with the CN until the index is found
        # 5. return all information

        result = {
            'net_before': 0,
            'net_after': 0,
            'net_diff': 0,
            'ppn_before': 0,
            'ppn_after': 0,
            'ppn_diff': 0,
        }

        # 1. get invoice and update the before (taken from invoice)
        # and diff (use the current CN data)
        invoice = self.reversed_entry_id
        result['net_before'] = invoice.amount_untaxed
        result['ppn_before'] = invoice.amount_tax
        result['net_diff'] = self.amount_untaxed
        result['ppn_diff'] = self.amount_tax

        # 2. convert to list
        cn_records = invoice.reversal_move_id
        cn_list = cn_records.ids

        # 3. get index of self.id
        idx = cn_list.index(self.id)

        # 4. loop and stop if the index is reached
        for index, cn in enumerate(cn_records):
            if index < idx:
                result['net_before'] -= abs(cn.amount_untaxed)
                result['ppn_before'] -= abs(cn.amount_tax)

        # cleanup the dict and return
        result['net_after'] = result['net_before'] - result['net_diff']
        result['ppn_after'] = result['ppn_before'] - result['ppn_diff']

        return result

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking")
    stock_move_id = fields.Many2one('stock.move', string="Stock Move")
