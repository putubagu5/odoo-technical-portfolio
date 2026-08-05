from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PayableAdjustment(models.Model):
    _name = 'ap.adjustment'
    _description = 'Account Payable Adjustment'
    _inherits = {'account.move': 'move_id'}
    _order = "date desc, name desc"
    _check_company_auto = True

    move_id = fields.Many2one(
        'account.move', string='Journal Entry', copy=False, index=True,
        readonly=True, required=True, ondelete='cascade',
        check_company=True)
    adj_name = fields.Char(
        string="Reference Number", copy=False, index=True,
        readonly=True)
    description = fields.Char(
        string="Description", copy=False)
    journal_id = fields.Many2one(
        'account.journal', string='AP Adjustment Journal', required=True,
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
    partner_id = fields.Many2one(
        'res.partner', string="Supplier", required=True,
        store=True, readonly=False, ondelete='restrict', copy=False,
        domain="['|', ('parent_id','=', False), ('is_company','=', True)]")
    invoice_id = fields.Many2one(
        'account.move', string='Invoice', required=True,
        copy=False, domain="[('partner_id', '=', partner_id),('move_type', '=', 'in_invoice'),"
                           "('payment_state', '=', 'not_paid')]")
    currency_id = fields.Many2one(
        'res.currency', string='Currency', store=True, readonly=False,
        related='invoice_id.currency_id', copy=False,
        help="The payment's currency.")
    amount_residual_signed = fields.Monetary(
        currency_field='currency_id', default=0.0,
        string="Total residual signed", related='invoice_id.amount_residual_signed',
        compute='_compute_amount', copy=False)
    type_adjustment = fields.Selection(selection=[
        ('deduction', 'Deduction'),
        ('additional', 'Additional')],
        string='Adjustment Type', required=True, copy=False)
    total_amount = fields.Monetary(
        currency_field='currency_id', default=0.0,
        string="Total Amount",
        compute='_compute_amount', copy=False)
    ap_adjustment_ids = fields.One2many(
        'ap.adjustment.line', 'ap_adjustment_id',
        string='Adjustment Lines', copy=False,
        ondelete='cascade',
        help="Adjustment Lines.")

    @api.depends('ap_adjustment_ids.amount')
    def _compute_amount(self):
        for rec in self:
            rec.total_amount = 0
            for pay in rec.ap_adjustment_ids:
                if pay.amount:
                    rec.total_amount += pay.amount

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.invoice_id:
            self.invoice_id = False

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.ap_adjustment_ids:
            for rec in self.ap_adjustment_ids:
                rec.invoice_line_id = False
                rec.account_id = False
                rec.counterpart_account_id = False
                rec.invoice_amount = False

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            if not pay.currency_id:
                pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id

    def action_post(self):
        ''' draft -> posted '''
        if self.type_adjustment == 'deduction':
            # print(self.ap_adjustment_ids, 'masuk buat insert negative amount ke invoice')
            self.invoice_id.amount_residual_signed = self.amount_residual_signed + self.total_amount
            self.invoice_id.amount_residual = self.amount_residual_signed + self.total_amount
            self.move_id._post(soft=False)

        elif self.type_adjustment == 'additional':
            # print(self.ap_adjustment_ids, 'masuk buat insert Positive amount ke invoice')
            self.invoice_id.amount_residual_signed = self.amount_residual_signed - self.total_amount
            self.invoice_id.amount_residual = self.amount_residual_signed - self.total_amount
            # print(self.invoice_id.name, self.invoice_id.amount_total_signed, self.invoice_id.amount_residual_signed)
            self.move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        if self.type_adjustment == 'deduction' and self.state == 'posted':
            # print(self.ap_adjustment_ids, 'masuk buat insert negative amount ke invoice')
            self.invoice_id.amount_residual_signed = self.invoice_id.amount_total_signed - self.total_amount
            self.invoice_id.amount_residual = self.invoice_id.amount_total_signed - self.total_amount
            self.move_id.button_cancel()

        elif self.type_adjustment == 'additional' and self.state== 'posted':
            print(self.ap_adjustment_ids, 'masuk buat insert Positive amount ke invoice')
            self.invoice_id.amount_residual_signed = self.invoice_id.amount_total_signed + self.total_amount
            self.invoice_id.amount_residual = self.invoice_id.amount_total_signed + self.total_amount
            self.move_id.button_cancel()


    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()

    def _prepare_move_line_default_vals(self):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        liquidity_line_name = _('Adjustment Account Payable %s', self.invoice_id.name)
        # find line move on journal and create counterpart journal
        line_vals_list = []
        # Payment Check has not been Sent with statment not yet reconcile and dp has not been paid
        for rec in self.ap_adjustment_ids:
            # print(rec, 'isi amountnya berapa', rec.amount)
            if rec:
                line_vals_list.append(
                    {
                        'name': liquidity_line_name,
                        'date_maturity': self.transaction_date,
                        'amount_currency': rec.amount,
                        'currency_id': self.currency_id.id,
                        'debit': rec.amount if self.type_adjustment == 'additional' else 0.0,
                        'credit': rec.amount if self.type_adjustment == 'deduction' else 0.0,
                        'partner_id': self.partner_id.id or self.journal_id.company_id.partner_id.id,
                        'operating_unit_id': self.operating_unit_id.id or False,
                        'analytic_account_id': rec.invoice_line_id.analytic_account_id.id or False,
                        'account_id': rec.account_id.id,
                    }, )
                # Counterpart Account
                line_vals_list.append(
                    {
                        'name': liquidity_line_name,
                        'date_maturity': self.transaction_date,
                        'amount_currency': rec.amount,
                        'currency_id': self.currency_id.id,
                        'debit': rec.amount if self.type_adjustment == 'deduction' else 0.0,
                        'credit': rec.amount if self.type_adjustment == 'additional' else 0.0,
                        'partner_id': self.partner_id.id or self.journal_id.company_id.partner_id.id,
                        'operating_unit_id': self.operating_unit_id.id or False,
                        'analytic_account_id': rec.invoice_line_id.analytic_account_id.id or False,
                        'account_id': rec.counterpart_account_id.id,
                    }, )

        print(line_vals_list)
        return line_vals_list

    @api.model_create_multi
    def create(self, vals):
        print(self,'berapa nilai vals', vals)
        # calculate payment with check and state is sent and statement is not reconcile
        data = []
        for val in vals:
            val['move_type'] = 'entry'
            val['name'] = '/'
            if val.get('ap_adjustment_ids'):
                data = vals
            elif val.get('line_type'):
                del vals
                vals = data

        res = super().create(vals)

        for i, pay in enumerate(res):
            to_write = {'id': pay.id}
            for k, v in vals[i].items():
                if k in self._fields and self._fields[k].store and k in pay.move_id._fields \
                        and pay.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                        pay._prepare_move_line_default_vals()]
            pay.move_id.write(to_write)

        if res.move_id:
            # print(res.move_id, 'masuk', res.id, res.ap_adjustment_ids)
            move_line = self.env['account.move.line'].search([('move_id', '=', res.move_id.id)])
            # print(move_line, 'line move')
            for line in res.ap_adjustment_ids:
                # print(line, 'tes line')
                for move in move_line:
                    if line.account_id.id == move.account_id.id:
                        line.move_line_id = move.id
                    elif line.counterpart_account_id.id == move.account_id.id:
                        line.counterpart_move_line_id = move.id
            if res.invoice_id:
                res.invoice_id.amount_residual_signed -= res.total_amount
                res.invoice_id.amount_residual = res.invoice_id.amount_residual_signed
                if res.invoice_id.amount_residual_signed > 0:
                    res.invoice_id.payment_state = 'partial'
                elif res.invoice_id.amount_residual_signed == 0:
                    res.invoice_id.payment_state = 'in_payment'
        return res

    def _synchronize_to_moves(self, changed_fields):
        # vals = []
        # move_line = self.env['account.move.line'].search([('move_id', '=', self.move_id.id)])
        for rec in self.move_id.line_ids:
            if rec.id:
                for line in self.ap_adjustment_ids:
                    print(line, "line")
                    print(line.move_line_id, line.counterpart_move_line_id, "line write", rec.id)
                    if rec.id == line.move_line_id.id and rec.debit > 0:
                        print(line.amount, line.account_id.id, "account")
                        # vals.append({
                        #     'id': rec.id,
                        #     'debit': line.amount,
                        #     'account_id': line.account_id.id
                        # },)
                        query = """
                                   update account_move_line
                                   set debit = %s , 
                                       credit = 0, 
                                       amount_currency = %s, 
                                       balance = %s,
                                       amount_residual = %s,
                                       account_id = %s,
                                       operating_unit_id = %s,
                                       analytic_account_id = %s
                                   where  id = %s
                               """
                        where_id = line.move_line_id.id
                        set1 = line.amount
                        set2 = line.account_id.id
                        set3 = line.invoice_id.operating_unit_id.id or None
                        set4 = line.invoice_line_id.analytic_account_id.id or None
                        self.env.cr.execute(query, [set1, set1, set1, set1, set2, set3, set4, where_id])

                    elif rec.id == line.counterpart_move_line_id.id and rec.credit > 0:
                        # print(line.amount, line.counterpart_account_id.id,"counterpart")
                        # vals.append({
                        #     'id': rec.id,
                        #     'credit': line.amount,
                        #     'account_id': line.counterpart_account_id.id
                        # },)
                        query2 = """
                                       update account_move_line
                                       set debit =  0, 
                                           credit = %s, 
                                           amount_currency = %s * -1, 
                                           balance = %s * -1,
                                           amount_residual = %s * -1,
                                           account_id = %s,
                                           operating_unit_id = %s,
                                           analytic_account_id = %s
                                       where  id = %s
                                   """
                        where_id = line.counterpart_move_line_id.id
                        set1 = line.amount
                        set2 = line.counterpart_account_id.id
                        set3 = line.invoice_id.operating_unit_id.id or None
                        set4 = line.invoice_line_id.analytic_account_id.id or None
                        self.env.cr.execute(query2, [set1, set1, set1, set1, set2, set3, set4, where_id])

    def write(self, vals):
        # OVERRIDE
        print('write vals', vals)
        res = super().write(vals)
        self._synchronize_to_moves(set(vals.keys()))
        return res


class PayableAdjustmentLines(models.Model):
    _name = 'ap.adjustment.line'
    _description = 'Account Payable Adjustment'
    _check_company_auto = True

    ap_adjustment_id = fields.Many2one(
        'ap.adjustment', string='AP Adjustment', copy=False)
    date = fields.Datetime(related='ap_adjustment_id.transaction_date', string='Date')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', related='ap_adjustment_id.state', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    invoice_id = fields.Many2one(
        'account.move', related='ap_adjustment_id.invoice_id',
        copy=False)
    line_type = fields.Selection(selection=[
        ('tax', 'Invoice Tax'),
        ('line', 'Invoice Line')], default='line',
        string='Line Type', copy=False)
    invoice_line_id = fields.Many2one(
        'account.move.line',
        domain="[('name','=', True)]",
        string='Invoice Line', copy=False)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', store=True, readonly=False,
        related='invoice_line_id.currency_id', copy=False,
        help="The payment's currency.")
    invoice_amount = fields.Monetary(
        currency_field='currency_id',
        default=0.0, string="Invoice Amount")
    amount = fields.Monetary(
        currency_field='currency_id', default=0.0,
        string="Adj Amount")
    account_id = fields.Many2one('account.account', 'Account')
    counterpart_account_id = fields.Many2one('account.account', 'Counterpart Account')
    company_id = fields.Many2one(
        'res.company', string='Company', store=True, readonly=True,
        related='ap_adjustment_id.company_id', change_default=True,
        default=lambda self: self.env.company)
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line', copy=False)
    counterpart_move_line_id = fields.Many2one(
        'account.move.line',
        string='Counterpart Move Line', copy=False)

    @api.onchange('invoice_line_id', 'line_type')
    def onchange_invoice_line(self):
        if self.invoice_line_id and self.line_type == 'line':
            self.account_id = self.invoice_line_id.account_id.id
            self.counterpart_account_id = self.invoice_line_id.move_id.transaction_type_id.account_id.id \
                if self.invoice_line_id.move_id.transaction_type_id \
                else self.invoice_line_id.partner_id.property_account_payable_id.id
            self.invoice_amount = self.invoice_line_id.price_total
        elif self.invoice_line_id and self.line_type == 'tax':
            for record in self.invoice_line_id.tax_ids:
                if record.invoice_repartition_line_ids:
                    for rec in record.invoice_repartition_line_ids:
                        if rec.account_id:
                            move_line = self.env['account.move.line'].search([('move_id', '=', self.invoice_id.id),
                                                                              ('tax_repartition_line_id', '=', rec.id)])
                            self.account_id = rec.account_id.id
                            self.counterpart_account_id = \
                                self.invoice_line_id.move_id.transaction_type_id.account_id.id \
                                    if self.invoice_line_id.move_id.transaction_type_id \
                                    else self.invoice_line_id.partner_id.property_account_payable_id.id
                            self.invoice_amount = move_line.price_total
