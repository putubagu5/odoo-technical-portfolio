from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BankCashTransfer(models.Model):
    _name = 'bank.cash.transfer'
    _description = 'Internal Bank Cash Transfer'

    name = fields.Char("Transfer Reference", default="New")
    doc_ref = fields.Char("Document Reference", default="New")
    partner_id = fields.Many2one(
        'res.partner', string="Customer/Vendor",
        store=True, compute='_compute_currency_id')
    bank_from = fields.Many2one('account.journal', string='Bank From')
    partner_bank_from = fields.Many2one(
        'res.partner.bank', string="Recipient Bank Account",
        related='bank_from.bank_account_id')
    bank_to = fields.Many2one('account.journal', string='Bank To')
    partner_bank_to = fields.Many2one(
        'res.partner.bank', string="Recipient Bank Account",
        related='bank_to.bank_account_id')
    clearing_account_id = fields.Many2one(
        'account.account', string='Clearing Account',
        compute='_compute_currency_id',
        readonly=False, help="Account.")
    amount = fields.Monetary(string='Amount', copy=False)
    receive_bank_to_amount = fields.Monetary(string='Amount Receive Bank To',
                                             copy=False, compute='_compute_receive_bank_to_amount')
    date = fields.Date(string='Transfer Date', required=True, index=True,
                       copy=False, default=fields.Datetime.now)
    note = fields.Char(string="Description", copy=False,
                       help="Note Description transfer bank or cash or etc.")
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          store=True, readonly=False,
                                          compute='_compute_company_currency_id',
                                          help="Company currency.")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  store=True, readonly=False,
                                  compute='_compute_currency_id',
                                  help="Banks From currency.")
    bank_to_currency_id = fields.Many2one('res.currency', string='Currency',
                                          store=True, readonly=False,
                                          compute='_bank_to_compute_currency_id',
                                          help="Banks To currency.")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', domain="[('user_ids', '=', uid)]")
    transfer_ids = fields.One2many('account.payment', 'transfer_id',
                                   string="Transfer Bank Cash", ondelete='cascade')
    transfer_state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel')],
        string="Transfer Status", store=True,
        readonly=True, copy=False, tracking=True,
        default='draft', compute='_compute_state')
    ref_description = fields.Char(string="Description")
    amount_in_words = fields.Char('Amount To Words', compute='compute_amount_in_words')
    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate Bank From', digits=(12, 4),
                                        help="Conversion Rate to Company Currency Rate")
    manual_currency_rate2 = fields.Float('Rate Bank To', digits=(12, 4),
                                         help="Conversion Rate to Company Currency Rate")

    # add payment fields here
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], 'Payment Type', default='outbound')
    available_payment_method_ids = fields.Many2many('account.payment.method',
                                                    compute='_compute_payment_method_fields')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method',
                                        readonly=False, store=True,
                                        compute='_compute_payment_method_id',
                                        domain="[('id', 'in', available_payment_method_ids)]")
    payment_method_code = fields.Char(related='payment_method_id.code')
    document_no = fields.Char('Document No')
    giro_no = fields.Char('Giro No')
    payment_doc_master_id = fields.Many2one('res.payment.document', 'Series',
                                            domain='[("journal_id", "=", bank_from)]')
    payment_doc_id = fields.Many2one(
        'res.payment.document.line', 'Document No',
        domain='[("document_id", "=", payment_doc_master_id), ("is_used", "=", False), ("cancelled", "=", False)]')
    giro_master_id = fields.Many2one('res.giro', 'Giro Series',
                                     domain='[("journal_id", "=", bank_from)]')
    giro_id = fields.Many2one(
        'res.giro.line', 'Giro No',
        domain='[("giro_id", "=", giro_master_id), ("is_used", "=", False), ("cancelled", "=", False)]')

    words1 = fields.Char(string="Words 1", compute="_compute_words")
    words2 = fields.Char(string="Words 2", compute="_compute_words")

    @api.depends('payment_type',
                 'bank_from.inbound_payment_method_ids',
                 'bank_from.outbound_payment_method_ids')
    def _compute_payment_method_fields(self):
        """ pure function taken from account module in account.payment """
        for rec in self:
            if rec.payment_type == 'inbound':
                rec.available_payment_method_ids = rec.bank_from.inbound_payment_method_ids
            else:
                rec.available_payment_method_ids = rec.bank_from.outbound_payment_method_ids

    @api.depends('payment_type', 'bank_from')
    def _compute_payment_method_id(self):
        ''' Compute the 'payment_method_id' field.
        This field is not computed in '_compute_payment_method_fields' because it's a stored editable one.
        '''
        for rec in self:
            if rec.payment_type == 'inbound':
                available_payment_methods = rec.bank_from.inbound_payment_method_ids
            else:
                available_payment_methods = rec.bank_from.outbound_payment_method_ids

            # Select the first available one by default.
            if rec.payment_method_id in available_payment_methods:
                rec.payment_method_id = rec.payment_method_id
            elif available_payment_methods:
                rec.payment_method_id = available_payment_methods[0]._origin
            else:
                rec.payment_method_id = False

    @api.onchange('manual_currency_rate_active', 'bank_from', 'bank_to')
    def _onchange_manual_currency_rate_active(self):
        if self.manual_currency_rate_active and self.bank_from and \
                self.currency_id == self.company_id.currency_id:
            print("masuk kondisi rate1")
            self.manual_currency_rate = 1
        elif self.manual_currency_rate_active and self.bank_to and \
                self.bank_to_currency_id == self.company_id.currency_id:
            print("masuk kondisi rate2")
            self.manual_currency_rate2 = 1
        elif self.manual_currency_rate_active and self.bank_to and self.bank_from and \
                self.bank_to_currency_id == self.company_id.currency_id and \
                self.currency_id == self.company_id.currency_id:
            print("masuk kondisi rate3")
            self.manual_currency_rate = 1
            self.manual_currency_rate2 = 1
        else:
            self.manual_currency_rate = False
            self.manual_currency_rate2 = False

    @api.onchange('bank_from', 'bank_to')
    def _onchange_journal_id(self):
        if self.bank_from and self.bank_to and self.bank_from == self.bank_to:
            raise UserError(
                _(
                    "please select difference bank between bank from or bank to"
                )
            )

    @api.depends('amount', 'currency_id')
    def compute_amount_in_words(self):
        for rec in self:
            if rec.currency_id:
                lang_2 = 'id'
                currency_to_slip = 'Rupiah'
                # convert to integer to remove decimal place
                amount = rec.amount
                words_amount_2 = num2words(int(amount), lang=lang_2)
                rec.amount_in_words = words_amount_2.title() + " " + currency_to_slip
            else:
                rec.amount_in_words = ''

    @api.depends('transfer_ids.state')
    def _compute_state(self):
        if self.transfer_ids:
            for line in self.transfer_ids:
                if 'draft' in line.state and 'posted' in line.state:
                    self.transfer_state = 'in_progress'
                elif 'draft' in line.state and 'posted' not in line.state:
                    self.transfer_state = 'draft'
                elif 'posted' in line.state and 'draft' not in line.state:
                    self.transfer_state = 'posted'
                elif 'cancel' in line.state and line.state not in ('draft', 'posted'):
                    self.transfer_state = 'cancel'

    @api.depends('bank_from', 'bank_to', 'amount', 'manual_currency_rate', 'manual_currency_rate2')
    def _compute_receive_bank_to_amount(self):
        for rec in self:
            rec.receive_bank_to_amount = False
            if rec.currency_id == rec.company_currency_id and rec.bank_to_currency_id == rec.company_currency_id:
                rec.receive_bank_to_amount = rec.amount
            elif rec.manual_currency_rate_active and rec.currency_id != rec.company_currency_id and rec.bank_to_currency_id == rec.company_currency_id:
                rec.receive_bank_to_amount = rec.amount * rec.manual_currency_rate
            elif rec.manual_currency_rate_active and rec.currency_id == rec.company_currency_id and rec.bank_to_currency_id != rec.company_currency_id:
                rec.receive_bank_to_amount = rec.amount / rec.manual_currency_rate2
            elif rec.manual_currency_rate_active and rec.currency_id != rec.company_currency_id and rec.bank_to_currency_id != rec.company_currency_id:
                rec.receive_bank_to_amount = rec.amount * rec.manual_currency_rate / (rec.manual_currency_rate2 or 1.0)
            else:
                rec.receive_bank_to_amount = rec.amount

    @api.depends('bank_from', 'bank_to')
    def _compute_company_currency_id(self):
        for pay in self:
            pay.company_currency_id = self.company_id.currency_id

    @api.depends('bank_from')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.bank_from.currency_id or pay.bank_from.company_id.currency_id
            pay.clearing_account_id = pay.bank_from.company_id.transfer_account_id
            pay.partner_id = pay.bank_from.company_id.partner_id.id

    @api.depends('bank_to')
    def _bank_to_compute_currency_id(self):
        for pay in self:
            pay.bank_to_currency_id = pay.bank_to.currency_id or pay.bank_to.company_id.currency_id

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name', 'New') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('bank.cash.transfer') or '/'
        bank = super().create(vals)
        # if bank.id:
        #     bank.action_create_transfer()
        return bank

    def action_create_transfer(self):
        transfer = self.env['account.payment']
        send_payment_method_id = self.env['account.payment.method'].search([
            ('payment_type', '=', 'inbound'), ('code', '=', 'manual')], limit=1)
        receive_payment_method_id = self.env['account.payment.method'].search([
            ('payment_type', '=', 'outbound'), ('code', '=', 'manual')], limit=1)
        if not self.partner_id:
            self.partner_id = self.bank_from.company_id.partner_id.id or self.bank_to.company_id.partner_id.id
        vals_list = [
            # send transfer
            {
                'payment_type': 'outbound',
                'partner_id': self.partner_id.id or False,
                'destination_account_id': self.clearing_account_id.id,
                'is_internal_transfer': True,
                'company_id': self.company_id.id or self.env.company,
                'amount': self.amount or 0.0,
                'currency_id': self.currency_id.id,
                'manual_currency_rate_active': self.manual_currency_rate_active,
                'manual_currency_rate': self.manual_currency_rate,
                'date': self.date,
                'ref': self.note or False,
                'journal_id': self.bank_from.id,
                'operating_unit_id': self.operating_unit_id.id or False,
                'payment_method_id': send_payment_method_id.id or False,
                'partner_bank_id': self.partner_bank_from.id or False,
                'payment_doc_master_id': self.payment_doc_master_id.id or False,
                'payment_doc_id': self.payment_doc_id.id or False,
                'giro_master_id': self.giro_master_id.id or False,
                'giro_id': self.giro_id.id or False,
                'transfer_id': self.id,
            },
            # Receive transfer
            {
                'payment_type': 'inbound',
                'partner_id': self.partner_id.id or False,
                'destination_account_id': self.clearing_account_id.id,
                'is_internal_transfer': True,
                'company_id': self.company_id.id or self.env.company,
                'amount': self.receive_bank_to_amount or 0.0,
                'currency_id': self.bank_to_currency_id.id,
                'manual_currency_rate_active': self.manual_currency_rate_active,
                'manual_currency_rate': self.manual_currency_rate2,
                'date': self.date,
                'ref': self.note or False,
                'journal_id': self.bank_to.id,
                'operating_unit_id': self.operating_unit_id.id or False,
                'payment_method_id': receive_payment_method_id.id or False,
                'partner_bank_id': self.partner_bank_to.id or False,
                'payment_doc_master_id': self.payment_doc_master_id.id or False,
                'payment_doc_id': self.payment_doc_id.id or False,
                'giro_master_id': self.giro_master_id.id or False,
                'giro_id': self.giro_id.id or False,
                'transfer_id': self.id,
            },
        ]
        transfer.create(vals_list)
        # recompute currency rate when different with company currency.
        # if transfer:
        #     self.ensure_one()
        #     company = self.env.company
        #     comp_curr = company.currency_id
        #     for rec in transfer:
        #         if rec.is_internal_transfer and rec.manual_currency_rate_active:
        #             rec.amount = comp_curr._convert(rec.amount, rec.currency_id, company, rec.date)
        return transfer

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        # for record in self:
        #     if record.transfer_ids:
        #         for rec in record.transfer_ids:
        #             if rec.amount != record.amount and rec.payment_type == 'outbound':
        #                 rec.write({'amount': record.amount})
        #             elif rec.amount != record.amount and rec.payment_type == 'inbound':
        #                 rec.write({'amount': record.amount})
        #             if rec.manual_currency_rate != record.manual_currency_rate:
        #                 rec.write({'manual_currency_rate': record.manual_currency_rate})
        #             if rec.ref != record.note:
        #                 rec.write({'ref': record.note})
        #                 # rec.ref = record.note or False
        #             if rec.currency_id != record.currency_id:
        #                 rec.write({'currency_id': record.currency_id})
        #                 # rec.currency_id = record.currency_id
        #             if rec.date != record.date:
        #                 rec.write({'date': record.date})
        #                 # rec.date = record.date
        #             if rec.operating_unit_id != record.operating_unit_id:
        #                 rec.write({'operating_unit_id': record.operating_unit_id or False})
        #                 # rec.operating_unit_id = record.operating_unit_id or False
        #             if rec.payment_type == 'outbound' and rec.journal_id != record.bank_from:
        #                 rec.write({'journal_id': record.bank_from.id or False})
        #                 # rec.journal_id = record.bank_from.id
        #             elif rec.payment_type == 'inbound' and rec.journal_id != record.bank_to:
        #                 rec.write({'journal_id': record.bank_to.id or False})
        #                 # rec.journal_id = record.bank_to.id
        #             if rec.payment_type == 'outbound' and rec.manual_currency_rate_active != record.manual_currency_rate_active:
        #                 rec.write({'manual_currency_rate_active': record.manual_currency_rate_active or False})
        #             elif rec.payment_type == 'inbound' and rec.manual_currency_rate_active != record.manual_currency_rate_active:
        #                 rec.write({'manual_currency_rate_active': record.manual_currency_rate_active or False})

        return res

    def action_posted(self):
        """ function to change state from draft to posted """
        for rec in self:
            if not rec.transfer_ids:
                rec.action_create_transfer()
            if rec.transfer_ids:
                for payment in rec.transfer_ids:
                    payment.action_post()
        return True

    def action_cancel(self):
        ''' function to change state from draft or posted to cancelled '''
        for rec in self.transfer_ids:
            rec.action_cancel()
        return True

    @api.depends('amount_in_words')
    def _compute_words(self):
        for record in self:
            words1 = ''
            words2 = ''
            if record.amount_in_words:
                txt_split = record.amount_in_words.split()
                if len(txt_split) > 0:
                    is_words2 = False
                    for text in txt_split:
                        if len(words1 + text) < 78 and is_words2 == False:
                            words1 = words1 + text + ' '
                        else:
                            is_words2 = True
                            words2 = words2 + text + ' '
                    record.words1 = words1
                    record.words2 = words2
