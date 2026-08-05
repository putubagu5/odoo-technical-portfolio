from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncArStatementReport(models.TransientModel):
    _name = 'wizard.mnc.ar.statement.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    @api.model
    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    @api.model
    def get_year_selection(self):
        years = []
        show_year = 0
        next_year = datetime.today().year + 2
        while show_year < 10:
            years.append(next_year)
            next_year -= 1
            show_year += 1
        return [(str(year), str(year)) for year in years]

    @api.model
    def get_this_year(self):
        return str(datetime.today().year)

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    all_partner = fields.Boolean(string="All Customer", default=True)
    partner_ids = fields.Many2many("res.partner", string="Customer")
    month = fields.Selection([
        ('01', 'Jan'), ('02', 'Feb'),
        ('03', 'Mar'), ('04', 'Apr'),
        ('05', 'May'), ('06', 'Jun'),
        ('07', 'Jul'), ('08', 'Aug'),
        ('09', 'Sep'), ('10', 'Oct'),
        ('11', 'Nov'), ('12', 'Dec')], string="Month")
    year = fields.Selection(selection="get_year_selection", default=get_this_year, string="Year")
    is_date_range = fields.Boolean(string="Custom Date Range")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    all_account_transaction = fields.Boolean(string="All GL Account", default=True)
    account_transaction_ids = fields.Many2many("account.transaction.type", string="GL Account")
    currency_id = fields.Many2one(comodel_name="res.currency", default=_get_default_currency_id, string="Currency")

    @api.onchange('company_id')
    def onchange_company_id(self):
        return {'domain': {
            'company_id': [
                ('id', 'in', self.env.user.company_ids.ids),
            ]
        }
        }

    def get_partner(self):
        self.ensure_one()

        partners = ''
        for data in self.partner_ids:
            if partners == '':
                partners = data.name
            else:
                partners += ', ' + data.name

        return partners

    def get_account_transaction(self):
        self.ensure_one()

        account_transactions = ''
        for data in self.account_transaction_ids:
            if account_transactions == '':
                account_transactions = data.name
            else:
                account_transactions += ', ' + data.name

        return account_transactions

    def get_period(self):
        self.ensure_one()

        period_name = ''
        if self.is_date_range:
            period_name = datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d-%b-%Y") + ' to ' + \
                          datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d-%b-%Y")
        else:
            period_name = dict(self._fields['month'].selection).get(self.month) + '-' + self.year

        return period_name

    def get_datas_report(self):
        DATA = []
        move_vals = []

        query = """ 
                    SELECT mv.id
                        FROM account_move AS mv
                            INNER JOIN res_partner rp ON rp.id=mv.partner_id
                    WHERE mv.partner_id IS NOT NULL AND mv.company_id=%s AND mv.move_type='out_invoice' AND mv.state='posted'
                """
        params = (self.company_id.id,)
        if self.is_date_range:
            query += ' AND mv.invoice_date >= %s AND mv.invoice_date <= %s'
            params += (self.start_date, self.end_date,)
        else:
            end_day = calendar.monthrange(int(self.year), int(self.month))[1]
            end_period = datetime.strptime(str(self.year) + '-' + str(self.month) + '-' + str(end_day), "%Y-%m-%d")

            query += " AND mv.invoice_date <= %s"
            params += (end_period,)

        if not self.all_partner:
            query += ' AND mv.partner_id IN %s'
            params += (tuple(self.partner_ids.ids),)
        if not self.all_account_transaction:
            query += ' AND mv.transaction_type_id IN %s'
            params += (tuple(self.account_transaction_ids.ids),)
        if self.currency_id:
            query += ' AND mv.currency_id = %s'
            params += (self.currency_id.id,)

        query += ' ORDER BY rp.name asc'

        self._cr.execute(query, params)
        move_ids = self.env['account.move'].sudo().browse([r[0] for r in self._cr.fetchall()])
        for move in move_ids:
            receipt_ids = []
            amount_remaining = move.amount_residual

            for receipt in move.applied_misc_ids:
                receipt_ids.append({
                    'receipt_number': receipt.misc_id.receipt_number,
                    'state': 'Paid',
                    'receipt_date': datetime.strptime(str(receipt.transaction_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                    'applied_date': datetime.strptime(str(receipt.date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                    'applied_amount': receipt.applied_amount,
                    'amount_remaining': amount_remaining
                })
                amount_remaining -= receipt.applied_amount

            move_vals.append({
                'move_id': move.id,
                'move_number': move.name,
                'payment_reference': move.payment_reference,
                'voucher_no': move.voucher_no,
                'ref': move.ref,
                'advertiser_gen21': move.advertiser_gen21,
                'partner_id': move.partner_id.id,
                'partner_name': move.partner_id.name,
                'invoice_date': datetime.strptime(str(move.invoice_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                'transaction_type_id': move.transaction_type_id.display_name,
                'account_id': move.transaction_type_id.account_id.id,
                'account_code': move.transaction_type_id.account_id.code,
                'account_name': move.transaction_type_id.account_id.name,
                'amount_total': move.amount_total,
                'amount_residual': move.amount_residual,
                'receipt_ids': receipt_ids,
                'state': dict(move._fields['state'].selection).get(move.state)
            })

        grouped = collections.defaultdict(list)
        for item in move_vals:
            grouped[item['partner_id']].append(item)

        for partner, items in grouped.items():
            partner_id = self.env['res.partner'].sudo().browse(partner)

            DATA.append({
                'partner_id': partner_id.id,
                'partner_name': partner_id.name,
                'partner_no': partner_id.partner_no,
                'items': items
            })

        return DATA

    def button_print_pdf(self):
        template = 'mnc_hrl_reporting.mnc_ar_statement_report'
        report = self.env['ir.actions.report']._get_report_from_name(template)
        datas = self.get_datas_report()

        domain = {
            'user': self.env.user.name,
            'company_id': self.company_id.id,
            'company_name': self.company_id.name,
            'is_date_range': self.is_date_range,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'year': self.year,
            'month': self.month,
            'period_name': self.get_period(),
            'all_partner': self.all_partner,
            'partner_ids': self.partner_ids.ids,
            'partner_name': 'All Customer' if self.all_partner else self.get_partner(),
            'all_account_transaction': self.all_account_transaction,
            'account_transaction_ids': self.account_transaction_ids.ids,
            'account_transaction_name': 'All Account' if self.all_account_transaction else self.get_account_transaction(),
            'currency_id': self.currency_id.id,
            'currency_name': self.currency_id.name,
            'datas': datas
        }
        values = {
            'ids': self.ids,
            'model': report.model,
            'form': domain
        }

        return self.env.ref('mnc_hrl_reporting.action_mnc_ar_statement_report').report_action(None, data=values)
        # return self.env.ref('mnc_hrl_reporting.action_mnc_ar_statement_report').report_action(self, data=values)
