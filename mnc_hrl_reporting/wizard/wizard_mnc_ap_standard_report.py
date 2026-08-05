from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncApStandardReport(models.TransientModel):
    _name = 'wizard.mnc.ap.standard.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

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
    is_date_range = fields.Boolean(string="Custom Date Range")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    month = fields.Selection([
        ('01', 'Jan'), ('02', 'Feb'),
        ('03', 'Mar'), ('04', 'Apr'),
        ('05', 'May'), ('06', 'Jun'),
        ('07', 'Jul'), ('08', 'Aug'),
        ('09', 'Sep'), ('10', 'Oct'),
        ('11', 'Nov'), ('12', 'Dec')], string="Month")
    year = fields.Selection(selection="get_year_selection", default=get_this_year, string="Year")
    all_account = fields.Boolean(string="All Account", default=True)
    account_ids = fields.Many2many('account.account', string="Account")
    file = fields.Binary('File')

    @api.onchange('company_id')
    def onchange_company_id(self):
        return {'domain': {
            'company_id': [
                ('id', 'in', self.env.user.company_ids.ids),
            ]
        }
        }

    def get_account(self):
        self.ensure_one()

        account_name = ''
        for account in self.account_ids:
            if account_name == '':
                account_name = account.display_name
            else:
                account_name += ', ' + account.display_name

        return account_name

    def button_print_excel(self):
        self.ensure_one()

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        left_title = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title.set_font_size('15')
        left_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_title_sub.set_font_size('14')
        center_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_title_sub.set_font_size('14')
        #################################################################################
        header_table = workbook.add_format({'valign': 'vcenter', 'align': 'center', 'font_color': '#FFFFFF'})
        header_table.set_font_size('12')
        header_table.set_bg_color('#02569C')
        header_table.set_text_wrap()
        header_table.set_border()
        #################################################################################
        center_table = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_table.set_font_size('11')
        center_table.set_border()
        #################################################################################
        left_table = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_table.set_font_size('11')
        left_table.set_text_wrap()
        left_table.set_border()
        #################################################################################
        numb_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_table.set_font_size('11')
        numb_table.set_border()
        #################################################################################
        left_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_footer.set_font_size('12')
        left_footer.set_border()
        #################################################################################
        right_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer.set_font_size('12')
        right_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('12')
        numb_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 15)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:C', 25)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 2)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 10)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 15)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 15)
        worksheet1.set_column('N:N', 15)
        worksheet1.set_column('O:O', 15)
        worksheet1.set_column('P:P', 15)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AP - Invoice Standard"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'Invoice Detail of Account Payable', left_title_sub)
        i = 3
        if self.is_date_range:
            worksheet1.write(i, 0, 'Period', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d-%b-%Y") + ' to ' + \
                             datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"), left_title_sub)
        else:
            worksheet1.write(i, 0, 'As of Period', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, dict(self._fields['month'].selection).get(self.month) + '-' + self.year,
                             left_title_sub)

        worksheet1.write(i, 4, 'Print Date', left_title_sub)
        worksheet1.write(i, 5, ':', center_title_sub)
        worksheet1.write(i, 6, datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                         left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'Account', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, 'All' if self.all_account else self.get_account(), left_title_sub)
        worksheet1.write(i, 4, 'User', left_title_sub)
        worksheet1.write(i, 5, ':', center_title_sub)
        worksheet1.write(i, 6, self.env.user.name, left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'Vendor Id', header_table)
        worksheet1.write(i, 2, 'Vendor Name', header_table)
        worksheet1.write(i, 3, 'Nomor Invoice', header_table)
        worksheet1.merge_range(i, 4, i, 5, 'Description', header_table)
        worksheet1.write(i, 6, 'Tgl Invoice', header_table)
        worksheet1.write(i, 7, 'Currency', header_table)
        worksheet1.write(i, 8, 'Exchange Rate', header_table)
        worksheet1.write(i, 9, 'Amount', header_table)
        worksheet1.write(i, 10, 'Amount Remaining', header_table)
        worksheet1.write(i, 11, 'Voucher Number', header_table)
        worksheet1.write(i, 12, 'Payment Status', header_table)
        worksheet1.write(i, 13, 'Status', header_table)
        worksheet1.write(i, 14, 'Account', header_table)
        i += 1

        query = """ 
                    SELECT mv.id
                        FROM account_move_line AS mvl
                            INNER JOIN account_move mv ON mv.id=mvl.move_id
                    WHERE mv.partner_id IS NOT NULL AND mv.company_id=%s AND mv.move_type='in_invoice' AND mv.state='posted'
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

        if not self.all_account:
            query += ' AND mvl.account_id IN %s'
            params += (tuple(self.account_ids.ids),)
        query += ' GROUP BY mv.id ORDER BY mv.invoice_date asc'

        self._cr.execute(query, params)

        data_vals = []

        bills_ids = self.env['account.move'].browse([r[0] for r in self._cr.fetchall()])
        for bill in bills_ids:
            data_vals.append({
                'invoice_id': bill.id,
                'invoice_number': bill.name,
                'payment_reference': bill.payment_reference if bill.payment_reference else '',
                'partner_id': bill.partner_id.id,
                'partner_number': bill.partner_id.partner_no if bill.partner_id.partner_no else '',
                'partner_name': bill.partner_id.name,
                'invoice_date': bill.invoice_date,
                'accounting_date': bill.date,
                'description': bill.ref if bill.ref else '',
                'voucher_number': bill.voucher_no if bill.voucher_no else '',
                'account_id': bill.account_ap_id.id,
                'account_code': bill.account_ap_id.code,
                'account_name': bill.account_ap_id.name,
                'currency_id': bill.currency_id.id,
                'currency_name': bill.currency_id.name,
                'currency_rate': bill.currency_id.actual_rate,
                'amount_total': bill.amount_total,
                'amount_outstanding': bill.amount_residual,
                'amount_payment': bill.amount_total - bill.amount_residual,
                'payment_state': dict(bill._fields['payment_state'].selection).get(bill.payment_state),
                'state': dict(bill._fields['state'].selection).get(bill.state),
            })

        grouped = collections.defaultdict(list)
        for item in data_vals:
            grouped[item['currency_id']].append(item)

        for curr, items in grouped.items():
            currency_id = self.env['res.currency'].sudo().browse(curr)

            for item in items:
                worksheet1.merge_range(i, 0, i, 1, item['partner_number'] if item['partner_number'] else '', left_table)
                worksheet1.write(i, 2, item['partner_name'] if item['partner_name'] else '', left_table)
                worksheet1.write(i, 3, item['payment_reference'] if item['payment_reference'] else '', left_table)
                worksheet1.merge_range(i, 4, i, 5, item['description'], left_table)
                worksheet1.write(i, 6,
                                 datetime.strptime(str(item['invoice_date']), "%Y-%m-%d").strftime("%d-%b-%y") if item[
                                     'invoice_date'] else '', center_table)
                worksheet1.write(i, 7, item['currency_name'], center_table)
                worksheet1.write(i, 8, item['currency_rate'], numb_table)
                worksheet1.write(i, 9, item['amount_total'], numb_table)
                worksheet1.write(i, 10, item['amount_outstanding'], numb_table)
                worksheet1.write(i, 11, item['voucher_number'], left_table)
                worksheet1.write(i, 12, item['payment_state'], center_table)
                worksheet1.write(i, 13, item['state'], center_table)
                worksheet1.write(i, 14, item['account_code'], left_table)
                i += 1

            worksheet1.merge_range(i, 6, i, 7, 'TOTAL PER CURRENCY :', right_footer)
            worksheet1.write(i, 8, currency_id.name, left_footer)
            worksheet1.write(i, 9, sum(item['amount_total'] for item in items), numb_footer)
            worksheet1.write(i, 10, sum(item['amount_outstanding'] for item in items), numb_footer)

            i += 2

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ap.standard.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
