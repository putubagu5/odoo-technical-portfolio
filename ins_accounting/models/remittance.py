from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class Remittance(models.Model):
    _name = 'remittance'
    _inherits = {'account.move': 'move_id'}
    _description = 'Remittance'
    _order = "date desc"

    move_id = fields.Many2one(
        'account.move', string='Journal Entry', copy=False, index=True,
        readonly=True, required=True, ondelete='cascade',
        check_company=True)
    company_id = fields.Many2one(
        'res.company', required=True, readonly=True,
        default=lambda self: self.env.company)
    journal_id = fields.Many2one(
        'account.journal', string='Remittance Journal',
        copy=False, check_company=True, index=True)
    user_id = fields.Many2one(
        'res.users', string='User',
        copy=False, index=True,
        default=lambda self: self.env.user)
    date = fields.Date(
        string='transaction date',
        default=fields.Date.context_today)
    period = fields.Char(
        string='period', compute='_compute_period')
    partner_id = fields.Many2one(
        'res.partner', string="Partner",
        store=True, compute='_compute_currency_id')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id', copy=False,
        help="The remittance's currency.")
    amount = fields.Monetary(
        currency_field='currency_id', string="Amount", default=0.0)
    reverse_journal_id = fields.Many2one(
        'account.journal', string='Reverse Journal',
        copy=False, check_company=True, index=True)
    reverse_move_id = fields.Many2one(
        'account.move', string='Reverse Remittance Journal',
        copy=False, required=False, readonly=False,
        ondelete='cascade', check_company=True)
    reverse_date = fields.Date(
        string='Reserve date',
        default=fields.Date.context_today)
    list_remittance = fields.Char(string='List remittance')
    list_remitted = fields.Char(string='List remitted')
    remittance_type = fields.Selection(selection=[
        ('prepayment', 'Prepayment'),
        ('payment', 'Payment'),
    ], string='Type', default='payment')

    # payment_ids = fields.Many2one(
    #     'account.move.line', string='Payment Check Posted Record',
    #     copy=False, required=False, readonly=False,
    #     ondelete='cascade', check_company=True)
    # dp_ids = fields.Many2one(
    #     'account.move.line', string='DP Posted Record',
    #     copy=False, required=False, readonly=False,
    #     ondelete='cascade', check_company=True)

    @api.depends('date')
    def _compute_period(self):
        for rec in self:
            if rec.date:
                year = rec.date.year
                month = rec.date.strftime("%b")
                rec.period = str(year) + "-" + str(month)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id and not self.journal_id.remitted_account_id:
            raise UserError(
                _(
                    "please select journal with remittance account or please set remittance account in the journal"
                )
            )
        if self.journal_id and self.journal_id.remitted_account_id:
            self.reverse_journal_id = self.journal_id.id

    @api.onchange('reverse_journal_id')
    def _onchange_reverse_journal_id(self):
        if self.reverse_journal_id and not self.reverse_journal_id.remitted_account_id:
            raise UserError(
                _(
                    "please select journal with remittance account or please set remittance account in the journal"
                )
            )

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id
            pay.partner_id = pay.journal_id.company_id.partner_id.id

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        # write_off_line_vals = write_off_line_vals or {}
        #
        # currency_id = self.currency_id.id
        # liquidity_line_name = _('Remitted %s', self.date)
        #
        # # Compute amounts.
        # write_off_amount_currency = write_off_line_vals.get('amount', 0.0)
        #
        # # find line move on journal and create counterpart journal
        # list_remittance = list_remitted = []
        # if self.list_remittance and self.remittance_type == 'payment':
        #     value1 = "(" + self.list_remittance[1:-1] + ")"
        #     print(value1, "value1")
        #     sql = """
        #              select distinct id, name, debit, credit, balance,amount_residual, account_id
        #              from  account_move_line
        #              where id in %s
        #              and currency_id = %s
        #           """ % (value1, self.currency_id.id)
        #     self.env.cr.execute(sql)
        #     list_remittance = self.env.cr.dictfetchall()
        #     print(list_remittance, "list_remittance")
        # elif self.list_remittance and self.remittance_type == 'prepayment':
        #     value1 = "(" + self.list_remittance[1:-1] + ")"
        #     print(value1, "value1")
        #     sql = """
        #              select distinct id, name, debit, credit, balance,amount_residual, account_id
        #              from  account_move_line
        #              where id in %s
        #              and currency_id = %s
        #           """ % (value1, self.currency_id.id)
        #     self.env.cr.execute(sql)
        #     list_remittance = self.env.cr.dictfetchall()
        #     print(list_remittance, "list_remittance")
        #
        # line_vals_list = []
        # # Payment Check has not been Sent with statment not yet reconcile and dp has not been paid
        # for rec in list_remittance:
        #     if rec:
        #         line_vals_list.append(
        #             {
        #                 'name': rec['name'] or liquidity_line_name,
        #                 'date_maturity': self.date,
        #                 'amount_currency': rec['balance'] or write_off_amount_currency,
        #                 'currency_id': currency_id,
        #                 'debit': rec["credit"] if rec["credit"] > 0.0 else 0.0,
        #                 'credit': rec["debit"] if rec["debit"] > 0.0 else 0.0,
        #                 'partner_id': self.partner_id.id or self.journal_id.company_id.partner_id.id,
        #                 'operating_unit_id': False,
        #                 'account_id': rec["account_id"],
        #             },
        #         )
        #     print(line_vals_list, "line_val_list")
        # line_vals_list = []
        # print(self.list_remittance, 'isi line vals')

        line_vals_list = []
        if self.remittance_type == 'payment':
            sql = """
                        select *
                        from (
                        select	distinct aml.id, concat(aml.name,' | payment reference ',ap.multi_payment_reference)::character varying as name, current_date as date_maturity,
                                aml.amount_currency * -1 as amount_currency, aml.currency_id,
                                case when 
                                    credit > 0
                                    then credit
                                    else 0
                                end as debit,
                                case when 
                                    debit > 0
                                    then debit
                                    else 0
                                end as credit, rc.partner_id, null as operating_unit_id,
                                aml.account_id, aml.id
                        from	account_payment ap
                        join	account_move_line aml
                          on	ap.move_id = aml.move_id
                        join	res_company rc
                          on 	aml.company_id = rc.id
                        where ap.payment_type = 'outbound'
                          and ap.remittance_flag = coalesce(null,False)
                          and ap.reverse_date is null
                          and ap.is_matched = coalesce(null, false)
                          and aml.company_id = %s
                          and aml.parent_state = 'posted'
                          order by 1 asc
                          ) as A
                """ % self.company_id.id
            self.env.cr.execute(sql)
            list_query = self.env.cr.dictfetchall()
            print(list_query, 'output query preparemoveline payment')
            line_vals_list = list_query

        elif self.remittance_type == 'prepayment':
            sql = """
                    select *
                    from (
                            select	distinct aml.id, concat(aml.name,' | payment reference ',ap.multi_payment_reference)::character varying as name, current_date as date_maturity,
                                    aml.amount_currency * -1 as amount_currency, aml.currency_id,
                                    case when 
                                        aml.credit > 0
                                        then aml.credit
                                        else 0
                                    end as debit,
                                    case when 
                                        aml.debit > 0
                                        then aml.debit
                                        else 0
                                    end as credit, rc.partner_id, null as operating_unit_id,
                                    aml.account_id
                            from account_move am
                            join account_move_line aml
                              on am.id = aml.move_id
                            join account_payment_invoice api
                              on api.move_id = am.id
                            join account_payment ap
                              on api.payment_id = ap.id
                            join res_company rc
                              on aml.company_id = rc.id
                            where am.move_type = 'in_invoice'
                              and am.bill_type = 'prepayment'
                              and aml.company_id = %s
                              and am.state = 'posted'
                              and (coalesce(ap.is_matched, false) = false 
                                  or (ap.bank_statement_name is null 
                                      and ap.date_bank_statement is null)
                                    )
                              and coalesce(ap.remittance_flag, false) = false
                            union
                            select	distinct aml.id, aml.name, current_date as date_maturity,
                                    aml.amount_currency * -1 as amount_currency, aml.currency_id,
                                    case when 
                                        aml.credit > 0
                                        then aml.credit
                                        else 0
                                    end as debit,
                                    case when 
                                        aml.debit > 0
                                        then aml.debit
                                        else 0
                                    end as credit, rc.partner_id, null as operating_unit_id,
                                    aml.account_id
                            from account_move am
                            join account_move_line aml
                              on am.id = aml.move_id
                            join res_company rc
                              on aml.company_id = rc.id
                            where am.move_type = 'in_invoice'
                              and am.bill_type = 'prepayment'
                              and aml.company_id = %s
                              and am.state = 'posted'
                              and am.payment_state = 'not_paid'   
                      ) as A
                      order by 1 asc
                """ % (self.company_id.id, self.company_id.id)
            self.env.cr.execute(sql)
            list_query = self.env.cr.dictfetchall()
            print(list_query, 'output query preparemoveline prepayment')
            line_vals_list = list_query
        return line_vals_list

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        self.move_id.button_cancel()

    def action_reverse(self):
        reverse_remit = self.env['reverse.remittance']
        if self.reverse_move_id:
            raise UserError(
                _(
                    "the remittance is already reverse"
                )
            )
        elif not self.reverse_move_id and self.state != 'posted':
            raise UserError(
                _(
                    "the remittance state is not posted. please post the remittance firstly"
                )
            )
        elif not self.reverse_move_id and self.state == 'posted':
            vals_list = [
                {
                    'remit_id': self.id,
                    'company_id': self.company_id.id,
                    'journal_id': self.reverse_journal_id.id,
                    'remit_date': self.date

                },
            ]
            reverse_remit.create(vals_list)
        return reverse_remit

    def action_calculate_remittance(self, query=None):
        # if self.remittance_type == 'payment':
        #     calculate_remittance = self.env['account.payment'].search([('payment_type', '=', 'outbound'),
        #                                                                ('remittance_flag', '=', False),
        #                                                                ('reverse_date', '=', False),
        #                                                                ('company_id', '=', self.env.company.id),
        #                                                                ('is_matched', '=', False),
        #                                                                ])
        #     print(calculate_remittance)
        #     payment_ids = []
        #     remitted_ids = []
        #     total = 0
        #     total2 = 0
        #     for rec in calculate_remittance:
        #         if rec.move_id.state == 'posted':
        #             for record in rec.move_id.line_ids:
        #                 payment_ids.append(record.id)
        #     print(payment_ids, "payment_ids")
        #     self.list_remittance = payment_ids
        #
        # # calculate deposit on bill invoice
        # elif self.remittance_type == 'prepayment':
        #     calculate_remittance = self.env['account.move'].search([('move_type', '=', 'in_invoice'),
        #                                                              ('bill_type', '=', 'prepayment'),
        #                                                              ('company_id', '=', self.env.company.id)])
        #     # print(calculate_remittance2)
        #     move_ids = []
        #     total3 = 0
        #     for rec2 in calculate_remittance:
        #         if rec2.state == 'posted':
        #             check_payment = self.env['account.payment.invoice'].search([('move_id', '=', rec2.id)])
        #             if check_payment:
        #                 for payment in check_payment:
        #                     if not payment.payment_id.remittance_flag \
        #                             or not payment.payment_id.is_matched:
        #                         for record in payment.move_id.line_ids:
        #                             move_ids.append(record.id)
        #                         print(move_ids, "move_ids with payment not remit & not recon")
        #             if rec2.payment_state == 'not_paid':
        #                 for record in rec2.line_ids:
        #                     move_ids.append(record.id)
        #                     print(move_ids, "move_ids without payment")
        #     self.list_remittance = move_ids

        if self.remittance_type == 'payment':
            sql = """
                    select *
                    from (
                    select	distinct aml.id, concat(aml.name,' | payment reference ',ap.multi_payment_reference)::character varying as name, current_date as date_maturity,
                            aml.amount_currency * -1 as amount_currency, aml.currency_id,
                            case when 
                                credit > 0
                                then credit
                                else 0
                            end as debit,
                            case when 
                                debit > 0
                                then debit
                                else 0
                            end as credit, rc.partner_id, null as operating_unit_id,
                            aml.account_id
                    from	account_payment ap
                    join	account_move_line aml
                      on	ap.move_id = aml.move_id
                    join	res_company rc
                      on 	aml.company_id = rc.id
                    where ap.payment_type = 'outbound'
                      and ap.remittance_flag = coalesce(null,False)
                      and ap.reverse_date is null
                      and ap.is_matched = coalesce(null, false)
                      and aml.company_id = %s
                      and aml.parent_state = 'posted'
                      order by 1 asc
                      ) as A
                  """ % self.company_id.id
            self.env.cr.execute(sql)
            list_query = self.env.cr.dictfetchall()
            print(list_query, 'output query calculate payment')
            list_remittance = []
            for rec in list_query:
                list_remittance.append(rec.get('id'))
            self.list_remittance = list_remittance
            print(self.list_remittance, 'isi list remittance')
            # self.list_remittance = list_query

        # calculate deposit on bill invoice
        elif self.remittance_type == 'prepayment':
            sql = """
                    select *
                    from (
                    select	distinct aml.id, concat(aml.name,' | payment reference ',ap.multi_payment_reference)::character varying as name, current_date as date_maturity,
                            aml.amount_currency * -1 as amount_currency, aml.currency_id,
                            case when 
                                aml.credit > 0
                                then aml.credit
                                else 0
                            end as debit,
                            case when 
                                aml.debit > 0
                                then aml.debit
                                else 0
                            end as credit, rc.partner_id, null as operating_unit_id,
                            aml.account_id
                    from account_move am
                    join account_move_line aml
                      on am.id = aml.move_id
                    join account_payment_invoice api
                      on api.move_id = am.id
                    join account_payment ap
                      on api.payment_id = ap.id
                    join res_company rc
                      on aml.company_id = rc.id
                    where am.move_type = 'in_invoice'
                      and am.bill_type = 'prepayment'
                      and aml.company_id = %s
                      and am.state = 'posted'
                      and (coalesce(ap.is_matched, false) = false 
                                  or (ap.bank_statement_name is null 
                                      and ap.date_bank_statement is null)
                                    )
                      and coalesce(ap.remittance_flag, false) = false
                    union
                    select	distinct aml.id, aml.name, current_date as date_maturity,
                            aml.amount_currency * -1 as amount_currency, aml.currency_id,
                            case when 
                                aml.credit > 0
                                then aml.credit
                                else 0
                            end as debit,
                            case when 
                                aml.debit > 0
                                then aml.debit
                                else 0
                            end as credit, rc.partner_id, null as operating_unit_id,
                            aml.account_id
                    from account_move am
                    join account_move_line aml
                      on am.id = aml.move_id
                    join res_company rc
                      on aml.company_id = rc.id
                    where am.move_type = 'in_invoice'
                      and am.bill_type = 'prepayment'
                      and aml.company_id = %s
                      and am.state = 'posted'
                      and am.payment_state = 'not_paid'
                      ) as A
                    order by 1 asc
                  """ % (self.company_id.id, self.company_id.id)
            self.env.cr.execute(sql)
            list_query = self.env.cr.dictfetchall()
            print(list_query, 'output query calculate prepayment')
            list_remittance = []
            for rec in list_query:
                list_remittance.append(rec.get('id'))
            self.list_remittance = list_remittance
            print(self.list_remittance, 'isi list remittance')

        # return calculate_remittance

    # def write(self, vals):
    #     # OVERRIDE
    #     res = super().write(vals)
    #     self.action_calculate_remittance()
    #     return res

    @api.model_create_multi
    def create(self, vals):
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
            pay.action_calculate_remittance()

        # self.amount = self.move_id.amount_total_signed
        return res

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        # self.action_calculate_remittance()
        self._synchronize_to_moves(set(vals.keys()))
        # self.amount = self.move_id.amount_total_signed
        return res

    def _synchronize_to_moves(self, changed_fields):
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in (
                'date', 'amount', 'currency_id', 'period',
                'remittance_type', 'user_id', 'list_remittance', 'list_remitted',
        )):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.
            write_off_line_vals = {
                'amount': self.move_id.amount_total_signed,
            }
            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
            print(line_vals_list, 'isi line vals in sycnronize move')
            line_ids_commands = []
            if line_vals_list:
                for line in pay.move_id.line_ids:
                    print(line.id, 'looping append line.id')
                    line_ids_commands.append((2, line.id))
                for i in line_vals_list:
                    print(i, "iiiii")
                    line_ids_commands.append((0, 0, i))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.
            print(line_ids_commands, 'line_ids_commands')
            pay.move_id.write({
                'currency_id': pay.currency_id.id,
                'line_ids': line_ids_commands,
            })
            pay.amount = pay.move_id.amount_total_signed
