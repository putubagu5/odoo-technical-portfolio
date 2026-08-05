from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AppliedCustomer(models.TransientModel):
    _name = 'reverse.remittance'
    _inherits = {'account.move': 'move_id'}

    move_id = fields.Many2one(
        'account.move', string='Journal Entry', copy=False, index=True,
        readonly=True, required=True, ondelete='cascade',
        check_company=True)
    company_id = fields.Many2one(
        'res.company', required=True, readonly=True)
    remit_id = fields.Many2one(
        'remittance',
        string='remittance', required=True,
        default=lambda self: self.env.context.get('active_ids'),
        domain="[('id', '=', active_id)]")
    remit_date = fields.Date(string='Remit Date')
    journal_id = fields.Many2one(
        'account.journal', string='Reverse Remittance Journal',
        copy=False, check_company=True, index=True)
    date = fields.Date(
        string='transaction date')


    def _prepare_move_line_default_vals(self):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        line_vals_list = []
        # Payment Check has not been Sent with statment not yet reconcile and dp has not been paid
        for rec in self.remit_id.move_id.line_ids:
            if rec:
                get_date = rec.date + relativedelta(months=1)
                first_date = get_date.replace(day=1)
                line_vals_list.append(
                    {
                        'name': rec.name,
                        'date_maturity': first_date,
                        'amount_currency': rec.amount_currency,
                        'currency_id': rec.currency_id.id,
                        'debit': rec.credit,
                        'credit': rec.debit,
                        'partner_id': rec.partner_id.id,
                        'operating_unit_id': False,
                        'account_id': rec.account_id.id,
                    },
                )
        return line_vals_list

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        self.move_id.button_cancel()

    @api.model_create_multi
    def create(self, vals):
        # OVERRIDE

        for val in vals:
            val['move_type'] = 'entry'
            val['name'] = '/'
            get_date = val['remit_date'] + relativedelta(months=1)
            first_date = get_date.replace(day=1)
            val['date'] = first_date
        reverse_remit = super().create(vals)

        for i, pay in enumerate(reverse_remit):
            to_write = {'id': pay.id}
            for k, v in vals[i].items():
                if k in self._fields and self._fields[k].store and k in pay.move_id._fields \
                        and pay.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                        pay._prepare_move_line_default_vals()]

            pay.move_id.write(to_write)
        if reverse_remit.move_id:
            get_date = reverse_remit.remit_id.date + relativedelta(months=1)
            reverse_remit.date = get_date.replace(day=1)
            reverse_remit.action_post()
            reverse_remit.remit_id.reverse_move_id = reverse_remit.move_id.id
        return reverse_remit
