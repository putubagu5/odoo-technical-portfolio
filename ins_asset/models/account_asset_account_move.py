from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero

class AccountAssetAccountMove(models.Model):
    _name = 'account.asset.account.move'

    name = fields.Char('Name')
    journal_id = fields.Many2one('account.journal', string='Journal')
    asset_category_id = fields.Many2one('account.asset', string='Asset Category')
    date_invoice = fields.Date('Date Invoice')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('post', 'Post'),
            ('cancel', 'Cancel')], default='draft',
            string='State')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.company)
    amount = fields.Monetary(string='Amount',default=0.0, currency_field = 'currency_id')
    move_id = fields.Many2one('account.move','Journal Items')
    depreciation_ids = fields.Many2many('account.asset.depreciation.line',
                                        'account_move_depreciation_line_rel',
                                        'depreciation_id',
                                        'account_id',
                                        string='Depreciation')

    def _prepare_move(self):
        account_analytic_id = self.asset_category_id.account_analytic_id
        analytic_tag_ids = self.asset_category_id.analytic_tag_ids
        depreciation_date = self.date_invoice
        company_currency = self.company_id.currency_id
        current_currency = self.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            self.amount, company_currency, self.company_id, depreciation_date)

        move_line_1 = {
            'name': self.name,
            'account_id': self.asset_category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'analytic_account_id': account_analytic_id.id if account_analytic_id else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if analytic_tag_ids else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * self.amount or 0.0,
        }

        move_line_2 = {
            'name': self.name,
            'account_id': self.asset_category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'analytic_account_id': account_analytic_id.id if account_analytic_id else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if analytic_tag_ids else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and self.amount or 0.0,
        }

        move_vals = {
            'ref': self.name,
            'date': depreciation_date or False,
            'journal_id': self.journal_id.id,
            'asset_id': self.asset_category_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }

        return move_vals

    def post(self):
        move_vals = self._prepare_move()
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        for depreciation_id in self.depreciation_ids:
            depreciation_id.write({'move_id': move.id})

        self.move_id = move.id
        self.state = 'post'

    def cancel(self):
        if self.move_id:
            self.move_id.button_cancel()

        for depreciation_id in self.depreciation_ids:
            depreciation_id.write({
                'move_id': False
            })
        self.depreciation_ids = [(5, 0, 0)]
        self.state = 'cancel'

    