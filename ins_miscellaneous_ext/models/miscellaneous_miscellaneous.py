from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class Miscellaneous(models.Model):
    _inherit = 'miscellaneous.miscellaneous'

    @api.onchange('journal_group')
    def _onchange_journal_group(self):
        if self.journal_group == 'split' and self.state == 'draft':
            self.misc_partner_id = False

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
            })
        return line_vals_list

    def action_applied_to_partner(self):
        applied_partner = self.env['applied.customer']
        print(self.misc_partner_id,'applied_partner')
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
