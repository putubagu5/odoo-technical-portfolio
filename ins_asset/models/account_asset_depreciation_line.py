from datetime import date
from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AccountAssetDepreciationLine(models.Model):
    _name = 'account.asset.depreciation.line'
    _description = 'Asset depreciation line'

    name = fields.Char(string='Depreciation Name', index=True)
    sequence = fields.Integer(required=True)
    asset_id = fields.Many2one('account.asset', string='Asset', required=True, ondelete='cascade')
    parent_state = fields.Selection(related='asset_id.state', string='State of Asset')
    amount = fields.Float(string='Current Depreciation', digits=0, required=True)
    remaining_value = fields.Float(string='Next Period Depreciation', digits=0, required=True)
    depreciated_value = fields.Float(string='Cumulative Depreciation', required=True)
    depreciation_date = fields.Date('Depreciation Date', index=True)
    move_id = fields.Many2one('account.move', string='Depreciation Entry')
    move_check = fields.Boolean(compute='_get_move_check', string='Linked', store=True)
    move_posted_check = fields.Boolean(compute='_get_move_posted_check', string='Posted', store=True)

    @api.depends('move_id')
    def _get_move_check(self):
        for line in self:
            line.move_check = bool(line.move_id)

    @api.depends('move_id.state')
    def _get_move_posted_check(self):
        for line in self:
            line.move_posted_check = True if line.move_id and line.move_id.state == 'posted' else False

    def create_move(self, post_move=True):
        depreciation_entries = self.env['account.asset.account.move'].sudo()
        for line in self:
            depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            records = depreciation_entries.search([
                ('journal_id', '=', line.asset_id.journal_id.id),
                ('asset_category_id', '=', line.asset_id.model_id.id),
                ('date_invoice', '=', depreciation_date),
                ('company_id', '=', line.asset_id.company_id.id),
                ('state','=', 'draft')
                ], limit = 1)
            if not records:
                depreciation_entries.create({
                    'name' : line.asset_id.model_id.display_name,
                    'asset_category_id': line.asset_id.model_id.id,
                    'date_invoice': depreciation_date,
                    'company_id': line.asset_id.company_id.id,
                    'currency_id': line.asset_id.company_id.currency_id.id,
                    'amount': line.amount,
                    'state': 'draft',
                    'journal_id': line.asset_id.journal_id.id,
                    'depreciation_ids': [(4, line.id)]
                    })
            else:
                amount = records.amount + line.amount
                records.write({'amount': amount,'depreciation_ids': [(4,line.id)] })

            line.sudo().write({'move_check': True})
        return

    def _prepare_move(self, line):
        category_id = line.asset_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            line.amount, company_currency, line.asset_id.company_id, depreciation_date)
        # asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
        move_line_1 = {
            'name': line.name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            # 'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if account_analytic_id else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if analytic_tag_ids else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': line.name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            # 'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if account_analytic_id else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if analytic_tag_ids else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        move_vals = {
            'ref': line.asset_id.asset_no,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'asset_id': category_id.model_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        return move_vals

    def _prepare_move_grouped(self):
        asset_id = self[0].asset_id
        category_id = asset_id.category_id  # we can suppose that all lines have the same category
        account_analytic_id = asset_id.account_analytic_id
        analytic_tag_ids = asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
        amount = 0.0
        for line in self:
            # Sum amount of all depreciation lines
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            company = line.asset_id.company_id
            amount += current_currency._convert(line.amount, company_currency, company, fields.Date.today())

        name = category_id.name + _(' (grouped)')
        move_line_1 = {
            'name': name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0,
            'credit': amount,
            'journal_id': category_id.journal_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
        }
        move_line_2 = {
            'name': name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0,
            'debit': amount,
            'journal_id': category_id.journal_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
        }
        move_vals = {
            'ref': category_id.name,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }

        return move_vals

    def create_grouped_move(self, post_move=True):
        if not self.exists():
            return []

        created_moves = self.env['account.move']
        move = self.env['account.move'].create(self._prepare_move_grouped())
        self.write({'move_id': move.id, 'move_check': True})
        created_moves |= move

        # if post_move and created_moves:
        #     self.post_lines_and_close_asset()
        #     created_moves.post()
        return [x.id for x in created_moves]

    def _generate_create_move(self):
        depreciation_ids = self.sudo().search([('depreciation_date','<=',date.today()),('move_check','=',False)], limit=100)
        for depreciation_id in depreciation_ids:
            depreciation_id.create_move(post_move=True)
        return True

    def post_lines_and_close_asset(self):
        # we re-evaluate the assets to determine whether we can close them
        for line in self:
            line.log_message_when_posted()
            asset = line.asset_id
            if asset.currency_id.is_zero(asset.value_residual):
                asset.message_post(body=_("Document closed."))
                asset.write({'state': 'close'})

    def log_message_when_posted(self):
        def _format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, values in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % name
                message += '%s</div>' % values
            return message

        for line in self:
            if line.move_id and line.move_id.state == 'draft':
                # partner_name = line.asset_id.partner_id.name
                currency_name = line.asset_id.currency_id.name
                msg_values = {_('Currency'): currency_name, _('Amount'): line.amount}
                # if partner_name:
                #     msg_values[_('Partner')] = partner_name
                msg = _format_message(_('Depreciation line posted.'), msg_values)
                line.asset_id.message_post(body=msg)

    def unlink(self):
        for record in self:
            if record.move_check:
                if record.asset_id.category_id.type == 'purchase':
                    msg = _("You cannot delete posted depreciation lines.")
                else:
                    msg = _("You cannot delete posted installment lines.")
                raise UserError(msg)
        return super(AccountAssetDepreciationLine, self).unlink()
