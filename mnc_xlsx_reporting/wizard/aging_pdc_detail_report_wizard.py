import pytz
from datetime import datetime
from odoo import models, fields, _


class AgingPDCDetailReportWizard(models.TransientModel):
    _name = 'aging.pdc.detail.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Aging PDC Detail Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('aging_pdc_detail', 'Aging PDC Detail')
        ],
    )

    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Accounts',
        help='Chart of account used to filter report',
    )

    customer_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Customers',
        help='Customers used to filter report',
        domain=['|', ('parent_id', '=', False), ('is_company', '=', True)]
    )

    def generate_report_xlsx(self):
        res = super(AgingPDCDetailReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'aging_pdc_detail':
            return self.env.ref('mnc_xlsx_reporting.action_aging_pdc_detail_pdf').\
            report_action(self)

        return res

    def get_user_allowed_company(self):
        for wizard in self:
            company_ids = wizard.env.context.get('allowed_company_ids', [])
            if not company_ids:
                company_ids = wizard.env.user.company_id.ids

            return company_ids

    def get_customer(self):
        for wizard in self:
            customer = ''
            if wizard.customer_type and wizard.customer_type == 'all':
                customer = 'All'
            elif wizard.customer_type and wizard.customer_type == 'specific':
                customer = ', '.join(customer.name for customer in wizard.customer_ids)

            return customer

    def get_period(self):
        for wizard in self:
            period = ''
            start_date = wizard.start_date.strftime('%b-%y')
            if wizard.date_type and wizard.date_type == 'range_of_date':
                end_date = wizard.end_date.strftime('%b-%y')
                period += '{start_date} s/d {end_date}'\
                    .format(start_date=start_date, end_date=end_date)
            elif wizard.date_type and wizard.date_type == 'as_of_date':
                period = 'Before {start_date}'.format(start_date=start_date)
            elif wizard.date_type and wizard.date_type == 'current_date':
                period = start_date

            return period
    
    def get_accounts(self):
        for wizard in self:
            account = ''
            if wizard.account_type and wizard.account_type == 'all':
                account = 'All'
            elif wizard.account_type and wizard.account_type == 'specific':
                account = ', '.join(\
                    account.display_name for account in wizard.account_ids)

            return account

    def get_currency(self, company_id):
        for wizard in self:
            Company = self.env['res.company'].browse(company_id)
            currency_id = Company.currency_id
            if not currency_id:
                currency_id = wizard.env.user.company_id.currency_id

            return currency_id

    def get_print_date(self):
        return datetime.now().astimezone(pytz.timezone(self.env.user.tz)).\
            strftime('%d-%b-%Y %H:%M:%S').upper()

    def get_receipt_per_customer(self, company_id):
        for wizard in self:
            currency = wizard.get_currency(company_id)
            domain = [
                ('company_id', '=', company_id),
                ('currency_id', '=', currency.id),
            ]

            if wizard.account_type and wizard.account_type == 'specific':
                domain += [('applied_partner_account', 'in', wizard.account_ids.ids)]

            if wizard.date_type and wizard.date_type == 'range_of_date':
                domain += [('date', '>=', wizard.start_date), ('date', '<=', wizard.end_date)]
            elif wizard.date_type and wizard.date_type == 'as_of_date':
                domain += [('date', '<=', wizard.start_date)]
            elif wizard.date_type and wizard.date_type == 'current_date':    
                domain += [('date', '=', wizard.start_date)]

            Receipts = self.env['miscellaneous.miscellaneous'].search(domain, order='id desc')
            customers = Receipts.mapped('misc_partner_id')
            data_receipts = []
            for customer in customers:
                receipt_per_customer = Receipts.filtered(\
                        lambda receipt: receipt.misc_partner_id.id == customer.id)
                data_receipts.append({
                    'customer_name': '{customer_name} ({partner_no})'.\
                        format(customer_name=customer.name, partner_no=customer.partner_no),
                    'receipt_ids': receipt_per_customer.ids,
                    'total_amount': sum(receipt_per_customer.mapped('amount')),
                    'total_unapplied_amount': 0,
                    'total_applied_amount': sum(receipt_per_customer.mapped('applied_amount')),
                })

            return data_receipts

    def get_invoice_account(self, invoice):
        account = ""
        if invoice.move_id.line_ids:
            account = invoice.move_id.line_ids[0].account_id
            account = account.code

        return account
    
