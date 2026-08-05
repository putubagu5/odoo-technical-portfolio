from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AppliedCustomer(models.TransientModel):
    _name = 'applied.customer'
    _inherits = {'account.move': 'move_id'}

    move_id = fields.Many2one(
        'account.move', string='Journal Entry', copy=False, index=True,
        readonly=True, required=True, ondelete='cascade',
        check_company=True)
    company_id = fields.Many2one(
        'res.company', required=True, readonly=True)
    misc_id = fields.Many2one(
        'miscellaneous.miscellaneous',
        string='Receipt', required=True,
        domain="[('id', '=', active_id)]")
    journal_id = fields.Many2one(
        'account.journal', string='Applied to partner Journal',
        copy=False, check_company=True, index=True)
    date = fields.Date(
        string='transaction date',
        default=fields.Date.context_today)

    def _seek_for_lines(self):
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in (self.misc_id.applied_customer_journal_id.payment_debit_account_id,
                                   self.misc_id.applied_customer_journal_id.payment_credit_account_id):
                liquidity_lines += line
            elif line.account_id.internal_type in (
                    'receivable', 'payable') or line.misc_id.misc_partner_id == line.company_id.partner_id:
                counterpart_lines += line
        return liquidity_lines, counterpart_lines

    def _prepare_move_line_default_vals(self):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        # Compute amounts.
        liquidity_amount_currency = self.misc_id.amount
        liquidity_balance = self.misc_id.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency
        counterpart_balance = -liquidity_balance
        currency_id = self.misc_id.currency_id.id
        liquidity_line_name = self.misc_id.name
        debit_receive = credit_receive = []
        if self.misc_id.misc_type == 'receive':
            liquidity_line_name = _('Applied receipt to Customer From %s', self.journal_id.name)
            credit_receive = self.misc_id.misc_partner_id.property_account_receivable_id.id
            debit_receive = self.misc_id.destination_account_id.id,
        elif self.misc_id.misc_type == 'payment':
            liquidity_line_name = _('Applied payment to vendor from %s', self.journal_id.name)
            credit_receive = self.misc_id.destination_account_id.id,
            debit_receive = self.misc_id.misc_partner_id.property_account_payable_id.id

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.misc_id.misc_partner_id.id,
                'operating_unit_id': self.misc_id.operating_unit_id.id,
                'account_id': debit_receive,
            },
            # Receivable
            {
                'name': self.misc_id.name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.misc_id.misc_partner_id.id,
                'operating_unit_id': self.misc_id.operating_unit_id.id,
                'account_id': credit_receive,
            },
        ]
        return line_vals_list

    def _synchronize_to_moves(self, changed_fields):
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in (
                'misc_id', 'date',
        )):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            liquidity_lines, counterpart_lines = pay._seek_for_lines()
            line_vals_list = pay._prepare_move_line_default_vals()

            line_ids_commands = []
            if liquidity_lines:
                line_ids_commands.append((1, liquidity_lines.id, line_vals_list[0]))
            else:
                line_ids_commands.append((0, 0, line_vals_list[0]))
            if counterpart_lines:
                line_ids_commands.append((1, counterpart_lines.id, line_vals_list[1]))
            else:
                line_ids_commands.append((0, 0, line_vals_list[1]))

            for extra_line_vals in line_vals_list[2:]:
                line_ids_commands.append((0, 0, extra_line_vals))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            pay.move_id.write({
                'partner_id': pay.misc_partner_id.id,
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        if self.invoice_ids:
            for rec in self.invoice_ids:
                if rec.state == 'posted':
                    raise UserError(_(
                        "You have Receipt, "
                        "Please cancel Applied Receipt firstly before cancel this Receipt."))
                if rec.state == 'cancel':
                    self.move_id.button_cancel()

        elif not self.invoice_ids:
            self.move_id.button_cancel()


    @api.model_create_multi
    def create(self, vals):
        # OVERRIDE
        for val in vals:
            print(val, 'masuk', self)
            val['move_type'] = 'entry'
            val['name'] = '/'
            val['ref'] = self.misc_id.name
            val['narration'] = self.misc_id.name
        cust = super().create(vals)

        for i, pay in enumerate(cust):
            to_write = {'id': pay.id}
            for k, v in vals[i].items():
                if k in self._fields and self._fields[k].store and k in pay.move_id._fields \
                        and pay.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                        pay._prepare_move_line_default_vals()]

            pay.move_id.write(to_write)
        print(cust)
        if cust.move_id:
            print(cust.move_id, 'masuk')
            cust.action_post()
            cust.misc_id.applied_customer_move_id = cust.move_id.id
        return cust
