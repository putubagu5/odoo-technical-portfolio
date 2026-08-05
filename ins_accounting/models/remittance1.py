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
        write_off_line_vals = write_off_line_vals or {}

        currency_id = self.currency_id.id
        liquidity_line_name = _('Remitted %s', self.date)

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        # find line move on journal and create counterpart journal
        list_remittance = list_remitted = []
        if self.list_remittance and self.remittance_type == 'payment':
            value1 = "(" + self.list_remittance[1:-1] + ")"
            print(value1, "value1")
            sql = """
                     select distinct id, name, debit, credit, balance,amount_residual, account_id
                     from  account_move_line
                     where id in %s
                     and currency_id = %s
                  """ % (value1, self.currency_id.id)
            self.env.cr.execute(sql)
            list_remittance = self.env.cr.dictfetchall()
            print(list_remittance, "list_remittance")
        elif self.list_remittance and self.remittance_type == 'prepayment':
            value1 = "(" + self.list_remittance[1:-1] + ")"
            print(value1, "value1")
            sql = """
                     select distinct id, name, debit, credit, balance,amount_residual, account_id
                     from  account_move_line
                     where id in %s
                     and currency_id = %s
                  """ % (value1, self.currency_id.id)
            self.env.cr.execute(sql)
            list_remittance = self.env.cr.dictfetchall()
            print(list_remittance, "list_remittance")
        # if self.list_remittance:
        #     value1 = "(" + self.list_remittance[1:-1] + ")"
        #     sql = """
        #              select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                     sum(amount_residual) as amount_residual, account_id
        #              from  account_move_line
        #              where id in %s
        #              and debit > 0
        #              group by account_id
        #              union
        #              select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                     sum(amount_residual) as amount_residual, account_id
        #              from  account_move_line
        #              where id in %s
        #              and credit > 0
        #              group by account_id
        #          """ % (value1, value1)
        #     self.env.cr.execute(sql)
        #     list_remittance = self.env.cr.dictfetchall()
        #
        # if self.list_remitted:
        #     value2 = "(" + self.list_remitted[1:-1] + ")"
        #     sql2 = """
        #              select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                     sum(amount_residual) as amount_residual, account_id
        #              from  account_move_line
        #              where id in %s
        #              and debit > 0
        #              group by account_id
        #              union
        #              select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                     sum(amount_residual) as amount_residual, account_id
        #              from  account_move_line
        #              where id in %s
        #              and credit > 0
        #              group by account_id
        #          """ % (value2, value2)
        #     self.env.cr.execute(sql2)
        #     list_remitted = self.env.cr.dictfetchall()

        line_vals_list = []
        # Payment Check has not been Sent with statment not yet reconcile and dp has not been paid
        for rec in list_remittance:
            if rec:
                line_vals_list.append(
                    {
                        'name': rec['name'] or liquidity_line_name,
                        'date_maturity': self.date,
                        'amount_currency': rec['balance'] or write_off_amount_currency,
                        'currency_id': currency_id,
                        'debit': rec["credit"] if rec["credit"] > 0.0 else 0.0,
                        'credit': rec["debit"] if rec["debit"] > 0.0 else 0.0,
                        'partner_id': self.partner_id.id or self.journal_id.company_id.partner_id.id,
                        'operating_unit_id': False,
                        'account_id': rec["account_id"],
                    },
                )
            # Payment check has been Sent but not reconciled
            # for record in list_remitted:
            #     if record:
            #         line_vals_list.append(
            #             {
            #                 'name': liquidity_line_name,
            #                 'date_maturity': self.date,
            #                 'amount_currency': record['balance'] or write_off_amount_currency,
            #                 'currency_id': currency_id,
            #                 'debit': record["credit"] if record["credit"] > 0.0 else 0.0,
            #                 'credit': record["debit"] if record["debit"] > 0.0 else 0.0,
            #                 'partner_id': self.partner_id.id or self.journal_id.company_id.partner_id.id,
            #                 'operating_unit_id': False,
            #                 'account_id': record["account_id"] if record["credit"] > 0.0
            #                 else self.journal_id.remitted_account_id.id,
            #             },
            #         )
            print(line_vals_list, "line_val_list")
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
        if self.remittance_type == 'payment':
            calculate_remittance = self.env['account.payment'].search([('payment_type', '=', 'outbound'),
                                                                       ('remittance_flag', '=', False),
                                                                       ('reverse_date', '=', False),
                                                                       ('company_id', '=', self.env.company.id),
                                                                       ('is_matched', '=', False),
                                                                       ])
            print(calculate_remittance)
            payment_ids = []
            remitted_ids = []
            total = 0
            total2 = 0
            for rec in calculate_remittance:
                if rec.move_id.state == 'posted':
                    for record in rec.move_id.line_ids:
                        payment_ids.append(record.id)
            print(payment_ids, "payment_ids")
            self.list_remittance = payment_ids
        # calculate payment with check and state is sent and statement is not reconcile
        # for rec in calculate_remittance:
        #     if not rec.reconciled_statement_ids \
        #             and rec.payment_method_id.name == 'Checks' \
        #             and rec.state == 'posted' \
        #             and rec.is_move_sent \
        #             and rec.company_id == self.env.company:
        #         for record in rec.move_id.line_ids:
        #             if record.currency_id == rec.currency_id and record.credit > 0:
        #                 total += record.credit
        #             if record.credit > 0:
        #                 payment_ids.append(record.id)
        #             elif record.debit > 0:
        #                 remitted_ids.append(record.id)
        #
        # # calculate payment with check and state is not sent and statement is not reconcile
        # for rec in calculate_remittance:
        #     if not rec.reconciled_statement_ids \
        #             and rec.payment_method_id.name == 'Checks' \
        #             and rec.state == 'posted' \
        #             and not rec.is_move_sent \
        #             and rec.company_id == self.env.company:
        #         for record in rec.move_id.line_ids:
        #             if record.currency_id == rec.currency_id and record.credit > 0:
        #                 total2 += record.credit
        #             payment_ids.append(record.id)

        # calculate deposit on bill invoice
        elif self.remittance_type == 'prepayment':
            calculate_remittance = self.env['account.move'].search([('move_type', '=', 'in_invoice'),
                                                                     ('bill_type', '=', 'prepayment'),
                                                                     ('company_id', '=', self.env.company.id)])
            # print(calculate_remittance2)
            move_ids = []
            total3 = 0
            for rec2 in calculate_remittance:
                if rec2.state == 'posted':
                    check_payment = self.env['account.payment.invoice'].search([('move_id', '=', rec2.id)])
                    if check_payment:
                        for payment in check_payment:
                            if not payment.payment_id.remittance_flag \
                                    or not payment.payment_id.is_matched:
                                for record in payment.move_id.line_ids:
                                    move_ids.append(record.id)
                                print(move_ids, "move_ids with payment not remit & not recon")
                    if rec2.payment_state == 'not_paid':
                        for record in rec2.line_ids:
                            move_ids.append(record.id)
                            print(move_ids, "move_ids without payment")
            self.list_remittance = move_ids
        # self.list_remitted = remitted_ids
        # sql = """
        #         select	pp.id
        #         from	product_product pp
        #         join	product_template pt
        #         on		pp.product_tmpl_id = pt.id
        #         where	pt.type = 'service'
        #         and		pt.purchase_method = 'purchase'
        #         and		pt.sequence = 1
        #         limit 1
        #       """
        # self.env.cr.execute(sql)
        # dp_product = self.env.cr.dictfetchall()
        # product = None
        # for i in dp_product:
        #     product = i['id']
        # for rec2 in calculate_remittance2:
        #     if rec2.state == 'posted' and rec2.payment_state == 'not_paid':
        #         for record in rec2.line_ids:
        #             if product and record.product_id.id == product \
        #                     and record.company_id == self.env.company:
        #                 total3 += record.debit
        #                 move_ids.append(record.move_id.id)
        # if move_ids:
        #     ids = tuple(move_ids)
        #     sql = """
        #              select id
        #              from  account_move_line
        #              where move_id in %s
        #          """ % (ids,)
        #     self.env.cr.execute(sql)
        #     move_line = self.env.cr.dictfetchall()
        #     for line in move_line:
        #         payment_ids.append(line["id"])
        # self.amount = total + total2 + total3
        # self.list_remittance = payment_ids
        # self.list_remitted = remitted_ids
        #
        # if self.list_remittance and self.list_remittance != '[]':
        #     value1 = "(" + self.list_remittance[1:-1] + ")"
        #     sql = """
        #                     select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                            sum(amount_residual) as amount_residual, account_id
        #                     from  account_move_line
        #                     where id in %s
        #                       and debit > 0
        #                     group by account_id
        #                     union
        #                     select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                            sum(amount_residual) as amount_residual, account_id
        #                     from  account_move_line
        #                     where id in %s
        #                       and credit > 0
        #                     group by account_id
        #                 """ % (value1, value1)
        #     self.env.cr.execute(sql)
        #     payment_ids = self.env.cr.dictfetchall()
        # if self.list_remitted and self.list_remitted != '[]':
        #     value2 = "(" + self.list_remitted[1:-1] + ")"
        #     sql2 = """
        #                     select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                            sum(amount_residual) as amount_residual, account_id
        #                     from  account_move_line
        #                     where id in %s
        #                       and debit > 0
        #                     group by account_id
        #                     union
        #                     select sum(debit) as debit, sum(credit) as credit, sum(balance) as balance,
        #                            sum(amount_residual) as amount_residual, account_id
        #                     from  account_move_line
        #                     where id in %s
        #                       and credit > 0
        #                     group by account_id
        #                 """ % (value2, value2)
        #     self.env.cr.execute(sql2)
        #     remitted_ids = self.env.cr.dictfetchall()
        #
        # for rec in self.move_id.line_ids:
        #     # recalculate amount in account_move_line if remittance amount has changed
        #     if payment_ids:
        #         for remittance in payment_ids:
        #             if rec.account_id.id == remittance["account_id"] \
        #                     and rec.debit != remittance["credit"] \
        #                     and rec.debit > 0 and remittance["credit"] > 0:
        #                 query2 = """
        #                            update account_move_line
        #                            set debit = %s ,
        #                                credit = 0,
        #                                amount_currency = %s,
        #                                balance = %s,
        #                                amount_residual = %s
        #                            where  id = %s
        #                        """
        #                 where_id = rec.id
        #                 set1 = remittance["credit"]
        #                 self.env.cr.execute(query2, [set1, set1, set1, set1, where_id])
        #             if rec.account_id.id == remittance["account_id"] \
        #                     and rec.credit != remittance["debit"] \
        #                     and rec.credit > 0 and remittance["debit"] > 0:
        #                 query2 = """
        #                                update account_move_line
        #                                set credit = %s ,
        #                                    debit = 0,
        #                                    amount_currency = %s,
        #                                    balance = %s,
        #                                    amount_residual = %s
        #                                where  id = %s
        #                          """
        #                 where_id = rec.id
        #                 set1 = remittance["debit"]
        #                 set2 = -remittance["debit"]
        #                 self.env.cr.execute(query2, [set1, set2, set2, set2, where_id])
        #
        #     if remitted_ids:
        #         for remitted in remitted_ids:
        #             if rec.account_id.id == rec.journal_id.remitted_account_id.id \
        #                     and rec.debit != remitted["credit"] \
        #                     and rec.debit > 0 and remitted["credit"] > 0:
        #                 query2 = """
        #                               update account_move_line
        #                               set debit = %s ,
        #                                   credit = 0,
        #                                   amount_currency = %s,
        #                                   balance = %s,
        #                                   amount_residual = %s
        #                               where  id = %s
        #                           """
        #                 where_id = rec.id
        #                 set1 = remitted["credit"]
        #                 self.env.cr.execute(query2, [set1, set1, set1, set1, where_id])
        #             if rec.account_id.id == rec.journal_id.remitted_account_id.id \
        #                     and rec.credit != remitted["debit"] \
        #                     and rec.credit > 0 and remitted["debit"] > 0:
        #                 query2 = """
        #                               update account_move_line
        #                               set credit = %s ,
        #                                   debit = 0,
        #                                   amount_currency = %s,
        #                                   balance = %s,
        #                                   amount_residual = %s
        #                               where  id = %s
        #                           """
        #                 where_id = rec.id
        #                 set1 = remitted["debit"]
        #                 set2 = -remitted["debit"]
        #                 self.env.cr.execute(query2, [set1, set2, set2, set2, where_id])
        return calculate_remittance

    # def write(self, vals):
    #     # OVERRIDE
    #     res = super().write(vals)
    #     self.action_calculate_remittance()
    #     return res

    @api.model_create_multi
    def create(self, vals):
        #     calculate_remittance = self.env['account.payment'].search([('payment_type', '=', 'outbound'),
        #                                                                ('company_id', '=', self.env.company.id)])
        #
        #     payment_ids = []
        #     remitted_ids = []
        #     move_ids = []
        #     total = 0
        #     total2 = 0
        #     # calculate payment with check and state is sent and statement is not reconcile
        #     for rec in calculate_remittance:
        #         if not rec.reconciled_statement_ids \
        #                 and rec.payment_method_id.name == 'Checks' \
        #                 and rec.state == 'posted' \
        #                 and rec.is_move_sent \
        #                 and rec.company_id == self.env.company:
        #             for record in rec.move_id.line_ids:
        #                 if record.currency_id == rec.currency_id and record.credit > 0:
        #                     total += record.credit
        #                 if record.credit > 0:
        #                     payment_ids.append(record.id)
        #                 elif record.debit > 0:
        #                     remitted_ids.append(record.id)
        #
        #     # calculate payment with check and state is not sent and statement is not reconcile
        #     for rec in calculate_remittance:
        #         if not rec.reconciled_statement_ids \
        #                 and rec.payment_method_id.name == 'Checks' \
        #                 and rec.state == 'posted' \
        #                 and not rec.is_move_sent \
        #                 and rec.company_id == self.env.company:
        #             for record in rec.move_id.line_ids:
        #                 if record.currency_id == rec.currency_id and record.credit > 0:
        #                     total2 += record.credit
        #                 payment_ids.append(record.id)
        #
        #     # calculate deposit on bill invoice
        #     calculate_remittance2 = self.env['account.move'].search([('move_type', '=', 'in_invoice'),
        #                                                              ('company_id', '=', self.env.company.id)])
        #     total3 = 0
        #     sql = """
        #                select	pp.id
        #                from	product_product pp
        #                join	product_template pt
        #                on		pp.product_tmpl_id = pt.id
        #                where	pt.type = 'service'
        #                and		pt.purchase_method = 'purchase'
        #                and		pt.sequence = 1
        #                limit 1
        #              """
        #     self.env.cr.execute(sql)
        #     dp_product = self.env.cr.dictfetchall()
        #     product = None
        #     for i in dp_product:
        #         product = i['id']
        #         if not product:
        #             raise UserError(
        #                 _(
        #                     "please set product deposit in accounting configuration"
        #                 )
        #             )
        #
        #     for rec2 in calculate_remittance2:
        #         if rec2.state == 'posted' and rec2.payment_state == 'not_paid':
        #             for record in rec2.line_ids:
        #                 if product and record.product_id.id == product \
        #                         and record.company_id == self.env.company:
        #                     total3 += record.debit
        #                     move_ids.append(record.move_id.id)
        #     if move_ids:
        #         ids = tuple(move_ids)
        #         sql = """
        #                   select id
        #                   from  account_move_line
        #                   where move_id in %s
        #               """ % (ids,)
        #         self.env.cr.execute(sql)
        #         move_line = self.env.cr.dictfetchall()
        #         for line in move_line:
        #             payment_ids.append(line["id"])
        #     self.amount = total + total2 + total3
        #     for val in vals:
        #         val['move_type'] = 'entry'
        #         val['name'] = '/'
        #         val['list_remittance'] = payment_ids or False
        #         val['list_remitted'] = remitted_ids or False
        #         val['amount'] = total + total2 + total3
        # self.action_calculate_remittance()
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

            line_ids_commands = []
            if line_vals_list:
                for line in pay.move_id.line_ids:
                    line_ids_commands.append((2, line.id))
                for i in line_vals_list:
                    print(i, "iiiii", pay.move_id.line_ids)
                    line_ids_commands.append((0, 0, i))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.
            print(line_ids_commands, 'line_ids_commands')
            pay.move_id.write({
                'currency_id': pay.currency_id.id,
                'line_ids': line_ids_commands,
            })
            pay.amount = pay.move_id.amount_total_signed
