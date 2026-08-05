from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PaymentInvoice(models.TransientModel):
    _name = 'wizard.payment.invoice'
    _description = 'Payment Invoice'

    @api.model
    def _get_default_partner(self):
        """ function to get default partner from active_id """
        result = False
        active_id = self._context.get('active_id', False)
        if active_id:
            payment = self.env['account.payment'].browse(active_id)
            partner = payment.partner_id if payment else False
            if partner:
                result = partner
        return result

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ onchange function to return domain to partner_id field """
        partner = False
        active_id = self._context.get('active_id', False)
        if active_id:
            payment = self.env['account.payment'].browse(active_id)
            partner = payment.partner_id if payment else False

        # return domain of partner_id and move_id
        return {
            'domain': {
                'partner_id': [('id', '=', partner.id)],
                'move_ids': [
                    ('partner_id', '=', partner.id),
                    ('payment_state', 'in', ('not_paid', 'in_payment', 'partial')),
                    ('amount_residual', '!=', 0),
                ],
            }
        }

    partner_id = fields.Many2one('res.partner', 'Vendor', default=_get_default_partner)
    move_ids = fields.Many2many('account.move', string='Invoices')
    line_ids = fields.One2many('wizard.payment.invoice.line', 'payment_id', 'Lines')

    @api.onchange('move_ids')
    def _onchange_move_ids(self):
        """ onchange function to add lines """
        for rec in self:
            lines = [(5, 0, 0)]  # empty all
            for line in rec.move_ids:
                # get account from line.line_ids, where credit exists and type
                # is payable (user_type_id)
                ln = line.line_ids.filtered(
                    lambda x: x.credit and x.account_id.internal_type == 'payable')
                account = ln.account_id
                move_id = line._origin.id
                description = '%s' % (line._origin.ref or '')
                data = {
                    'name': line.name,
                    'payment_reference': line.payment_reference or False,
                    'date_invoice': line.invoice_date,
                    'date_accounting': line.date,
                    'account_id': account.id or False,
                    'description': description,
                    'po_number': line.po_numbers,
                    'currency_id': line.currency_id.id,
                    'amount': line._origin.amount_residual,
                    'move_id': move_id,
                }
                lines.append((0, 0, data))
            rec.line_ids = lines

    def _check_currency(self):
        """ helper function to check if line has different currencies """
        currencies = set(x.currency_id.id for x in self.line_ids)
        if len(currencies) > 1:
            raise ValidationError('Cannot process data. Multiple Currencies detected')

    def button_confirm(self):
        """ function to confirm """
        self.ensure_one()
        self._check_currency()  # check currency first
        active_id = self._context.get('active_id', False)
        print("===CHECK CONFIRM INVOICE PAYMENT===")
        print(active_id,'active_id')
        if active_id:
            payment = self.env['account.payment'].browse(active_id)
            print(payment)
            # empty first
            lines = [(2, x.id) for x in payment.payment_invoice_ids]
            print(lines)
            print(self.line_ids)
            total_amount = 0.0
            for line in self.line_ids:
                move_id = line.move_id.id
                print(move_id)
                data = {
                    'name': line.name,
                    'payment_reference': line.payment_reference or False,
                    'date_invoice': line.date_invoice,
                    'date_accounting': line.date_accounting,
                    'account_id': line.account_id.id,
                    'description': line.description,
                    'po_number': line.po_number,
                    'currency_id': line.currency_id.id,
                    'amount': line.amount,
                    'move_id': move_id,
                }
                print(data)
                lines.append((0, 0, data))
                total_amount += line.amount

            print(lines)
            payment.payment_invoice_ids = lines
            payment.amount = total_amount

        print("===CHECK CONFIRM INVOICE PAYMENT===")
        return True
