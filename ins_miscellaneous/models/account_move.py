from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
from json import dumps

import json


class InheritAcountMove(models.Model):
    _inherit = 'account.move'

    def _get_applied(self):
        applied = self.env['applied.invoices']
        for record in self:
            apply = applied.search([('invoice_id', '=', record.id),
                                    ('transaction_type', '=', 'apply'),
                                    ('state', '=', 'posted')])
            if apply:
                record.applied_misc_ids = [(6, 0, [rec.id for rec in apply])]
            else:
                record.applied_misc_ids = False
    applied_misc_ids = fields.Many2many(
        'applied.invoices', 'invoice_id',
        compute='_get_applied',
        string='Applied from Receipt')

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        super(InheritAcountMove, self)._compute_payments_widget_reconciled_info()
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                payments_widget_vals['content'] = move._get_reconciled_info_JSON_values()
            if payments_widget_vals['content']:
                move.invoice_payments_widget = json.dumps(payments_widget_vals, default=date_utils.json_default)
                print(type(payments_widget_vals['content']),'ins_miscellaneous')
                if move.applied_misc_ids:
                    total_reconcile_amount = total_applied_amount = 0
                    for amount in payments_widget_vals['content']:
                        print(amount)
                        total_reconcile_amount += amount['amount']
                    for rec in move.applied_misc_ids:
                        if rec.transaction_type == 'apply':
                            total_applied_amount += (rec.applied_amount + rec.payment_difference)
                            print(total_applied_amount, 'kalo yang ini')
                            for recon in rec.misc_id.move_id.line_ids:
                                if recon.full_reconcile_id:
                                    print(recon.full_reconcile_id, 'recon', recon.matching_number)
                                    for line_move in rec.invoice_id.line_ids:
                                        if not line_move.product_id and line_move.name == line_move.name:
                                            line_move.full_reconcile_id = recon.full_reconcile_id.id
                                            line_move.matching_number = recon.matching_number
                    print(total_applied_amount, 'tes1', total_reconcile_amount, move.mnc_payment_state)
                    move.amount_residual_signed = move.amount_total_signed - \
                                                  (total_applied_amount + total_reconcile_amount)
                    move.amount_residual = move.amount_total_signed - \
                                                  (total_applied_amount + total_reconcile_amount)
                    # for line in move.line_ids:
                    #     print('apakah masuk kondisi disini [ins_miscellaneous looping buat ngeset payment state]')
                    #     print(line.move_id.payment_state, line.move_id, line.full_reconcile_id )
                    #     if line.name == line.move_id.name and not line.product_id and not line.tax_line_id:
                    #         line.amount_residual = line.move_id.amount_residual
                    #         line.amount_residual_currency = line.amount_residual
                    #         if line.amount_residual == 0 and line.full_reconcile_id:
                    #             print(line.full_reconcile_id, 'harusnya paid1')
                    #             line.move_id.payment_state = 'paid'
                    #         elif line.amount_residual == 0 and not line.full_reconcile_id:
                    #             line.move_id.payment_state = 'in_payment'
                    #         elif line.amount_residual > 0:
                    #             line.move_id.payment_state = 'partial'
                    #         elif line.amount_residual == line.move_id.amount_total_signed:
                    #             line.move_id.payment_state = 'not_paid'
            else:
                move.invoice_payments_widget = json.dumps(False)
                print(move.invoice_payments_widget,'invoice_payment_widget')
                if move.applied_misc_ids:
                    total_reconcile_amount = total_applied_amount = 0
                    for amount in payments_widget_vals['content']:
                        total_reconcile_amount += amount['amount']
                    for rec in move.applied_misc_ids:
                        if rec.transaction_type == 'apply':
                            total_applied_amount += (rec.applied_amount + rec.payment_difference)
                            print(rec.misc_id.move_id.line_ids)
                            print(total_applied_amount, 'berapa nilai misc kalo disini')
                            for recon in rec.misc_id.move_id.line_ids:
                                if recon.full_reconcile_id:
                                    print(recon.full_reconcile_id, 'recon2', recon.matching_number)
                                    for line_move in rec.invoice_id.line_ids:
                                        if not line_move.product_id \
                                                and not line_move.tax_line_id \
                                                and line_move.name == line_move.move_id.name:
                                            line_move.full_reconcile_id = recon.full_reconcile_id.id
                                            line_move.matching_number = recon.matching_number
                    print(total_applied_amount, 'tes2', total_reconcile_amount)
                    move.amount_residual_signed = move.amount_total_signed - \
                                                  total_applied_amount + total_reconcile_amount
                    move.amount_residual = move.amount_residual_signed
                    for line in move.line_ids:
                        if line.name == line.move_id.name and not line.product_id and not line.tax_line_id:
                            line.amount_residual = line.move_id.amount_residual
                            line.amount_residual_currency = line.amount_residual
                            if line.amount_residual == 0 and line.full_reconcile_id:
                                print(line.full_reconcile_id, 'harusnya paid2')
                                line.move_id.payment_state = 'paid'
                            elif line.amount_residual == 0 and not line.full_reconcile_id:
                                line.move_id.payment_state = 'in_payment'
                            elif line.amount_residual > 0:
                                line.move_id.payment_state = 'partial'
                            elif line.amount_residual == line.move_id.amount_total_signed:
                                line.move_id.payment_state = 'not_paid'
