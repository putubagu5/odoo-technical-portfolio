from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar


class WizardTrialBalanceReport(models.TransientModel):
    _name = 'wizard.trial.balance.report'

    @api.model
    def _get_default_company_id(self):
        return self.env.user.company_id.id

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

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=_get_default_company_id)
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
    all_account = fields.Boolean(string="All Account", default=True)
    account_ids = fields.Many2many('account.account', string="Account")

    @api.onchange('company_id')
    def onchange_company_id(self):
        return {'domain': {
            'company_id': [
                ('id', 'in', self.env.user.company_ids.ids),
            ]}}

    def get_analytic_account(self):
        self.ensure_one()

        analytic_account = ''
        for account in self.analytic_account_ids:
            if analytic_account == '':
                analytic_account = account.display_name
            else:
                analytic_account += ', ' + account.display_name

        return analytic_account

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
        # header_table.set_border()
        #################################################################################
        center_table = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_table.set_font_size('11')
        # center_table.set_border()
        #################################################################################
        left_table = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_table.set_font_size('11')
        # left_table.set_border()
        #################################################################################
        numb_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_table.set_font_size('11')
        # numb_table.set_border()
        #################################################################################
        left_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_footer.set_font_size('12')
        # left_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('12')
        # numb_table.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 40)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:D', 25)
        worksheet1.set_column('E:E', 2)
        worksheet1.set_column('F:G', 25)
        worksheet1.set_column('H:H', 2)
        worksheet1.set_column('I:K', 25)
        worksheet1.set_column('L:L', 40)
        worksheet1.set_column('M:P', 20)
        worksheet1.set_column('Q:Q', 40)
        worksheet1.set_column('R:AD', 20)
        worksheet1.set_column('AE:AE', 40)
        worksheet1.set_column('AF:AG', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " - Trial Balance"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'SUB LEDGER DETAIL', left_title_sub)
        i = 3
        if self.is_date_range:
            worksheet1.write(i, 0, 'Dates', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d/%m/%Y") + ' - ' + \
                             datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d/%m/%Y"), left_title_sub)
        else:
            worksheet1.write(i, 0, 'As of Period', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, dict(self._fields['month'].selection).get(self.month) + '-' + self.year,
                             left_title_sub)

        # worksheet1.write(i, 3, 'Area', left_title_sub)
        # worksheet1.write(i, 4, ':', center_title_sub)
        # worksheet1.write(i, 5, 'All', left_title_sub)
        worksheet1.write(i, 6, 'Date of Print', left_title_sub)
        worksheet1.write(i, 7, ':', center_title_sub)
        worksheet1.write(i, 8, datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                         left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'Cost Center', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, 'All' if self.all_analytic_account else self.get_analytic_account(), left_title_sub)
        worksheet1.write(i, 6, 'User', left_title_sub)
        worksheet1.write(i, 7, ':', center_title_sub)
        worksheet1.write(i, 8, self.env.user.name, left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'Area', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, 'All', left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'Account', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, 'All' if self.all_account else self.get_account(), left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'COA', header_table)
        worksheet1.write(i, 2, 'ACCOUNT', header_table)
        worksheet1.merge_range(i, 3, i, 4, 'COST CENTER', header_table)
        worksheet1.write(i, 5, 'AREA', header_table)
        worksheet1.merge_range(i, 6, i, 7, 'JOURNAL NAME', header_table)
        worksheet1.write(i, 8, 'SOURCE', header_table)
        worksheet1.write(i, 9, 'CATEGORY', header_table)
        worksheet1.write(i, 10, 'GL DATE', header_table)
        worksheet1.write(i, 11, 'DESCRIPTION', header_table)
        worksheet1.write(i, 12, 'BEGINING BALANCE', header_table)
        worksheet1.write(i, 13, 'DEBIT', header_table)
        worksheet1.write(i, 14, 'CREDIT', header_table)
        worksheet1.write(i, 15, 'ENDING BALANCE', header_table)
        worksheet1.write(i, 16, 'CUSTOMER/SUPPLIER', header_table)
        worksheet1.write(i, 17, 'PROJECT NUMBER', header_table)
        worksheet1.write(i, 18, 'PO NUMBER', header_table)
        worksheet1.write(i, 19, 'INVOICE NUMBER', header_table)
        worksheet1.write(i, 20, 'GL DATE INVOICE', header_table)
        worksheet1.write(i, 21, 'TYPE', header_table)
        worksheet1.write(i, 22, 'MO NUMBER', header_table)
        worksheet1.write(i, 23, 'VOUCHER NUMBER', header_table)
        worksheet1.write(i, 24, 'GL DATE VOUCHER', header_table)
        worksheet1.write(i, 25, 'CURR CODE', header_table)
        worksheet1.write(i, 26, 'CURR TYPE', header_table)
        worksheet1.write(i, 27, 'CURR RATE', header_table)
        worksheet1.write(i, 28, 'VALAS', header_table)
        worksheet1.write(i, 29, 'BATCH', header_table)
        worksheet1.write(i, 30, 'DESCRIPTION LINE JOURNAL', header_table)
        worksheet1.write(i, 31, 'FAKTUR PAJAK', header_table)
        worksheet1.write(i, 32, 'DATE FAKTUR', header_table)
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
            query += ' AND mv.account_ap_id IN %s'
            params += (tuple(self.account_ids.ids),)
        if not self.all_operating_unit:
            query += ' AND mvl.operating_unit_id IN %s'
            params += (tuple(self.operating_unit_ids.ids),)
        if not self.all_analytic_account:
            query += ' AND mvl.analytic_account_id IN %s'
            params += (tuple(self.analytic_account_ids.ids),)
        query += ' GROUP BY mv.id ORDER BY mv.invoice_date asc'

        self._cr.execute(query, params)

        bills_ids = self.env['account.move'].browse([r[0] for r in self._cr.fetchall()])
        for bill in bills_ids:
            for line in bill.line_ids:
                worksheet1.merge_range(i, 0, i, 1, line.account_id.code + '-' + line.account_id.name or "", left_table)  # coa
                worksheet1.write(i, 2, line.account_id.code or "", left_table)  # account
                worksheet1.merge_range(i, 3, i, 4, line.analytic_account_id.code or "", left_table)  # cost_center
                worksheet1.write(i, 5, "-", center_table)  # area
                worksheet1.merge_range(i, 6, i, 7, line.move_id.name or "", center_table)  # journal_name
                worksheet1.write(i, 8, "-", left_table)  # source
                worksheet1.write(i, 9, "-", center_table)  # category
                worksheet1.write(i, 10, datetime.strptime(str(line.date), "%Y-%m-%d").strftime("%d-%b-%y") if bill.invoice_date else "", left_table)  # gl_date
                worksheet1.write(i, 11, line.name or "", numb_table)  # description
                worksheet1.write(i, 13, line.debit or "", numb_table)  # debit
                worksheet1.write(i, 14, line.credit or "", numb_table)  # credit
                worksheet1.write(i, 15, "-", numb_table)  # ending_balance
                worksheet1.write(i, 16, line.partner_id.name or "", numb_table)  # customer_supplier
                worksheet1.write(i, 17, "-", numb_table)  # project_number
                worksheet1.write(i, 18, "-", numb_table)  # po_number
                worksheet1.write(i, 19, "-", numb_table)  # invoice_number
                worksheet1.write(i, 20, datetime.strptime(str(line.date), "%Y-%m-%d").strftime("%d-%b-%y") if line.date else "", left_table)  # gl_date_invoice
                worksheet1.write(i, 21, "-", numb_table)  # type
                worksheet1.write(i, 22, "-", numb_table)  # mo_number
                worksheet1.write(i, 23, "-", numb_table)  # voucher_number
                worksheet1.write(i, 24, "-", left_table)  # gl_date_voucher
                worksheet1.write(i, 25, line.currency_id.name or "", numb_table)  # curr_code
                worksheet1.write(i, 26, "-", numb_table)  # curr_type
                worksheet1.write(i, 27, line.currency_id.actual_rate or "", numb_table)  # curr_rate
                worksheet1.write(i, 28, "-", numb_table)  # valas
                worksheet1.write(i, 29, "-", numb_table)  # batch
                worksheet1.write(i, 30, "-", numb_table)  # description_line_journal
                worksheet1.write(i, 31, "-", numb_table)  # faktur_pajak
                worksheet1.write(i, 32, "-", left_table)  # date_faktur
            i += 1

            # for item in bill.line_ids:
            #     worksheet1.write(i, 12, item.balance, numb_table)
            #     worksheet1.write(i, 13, item.account_id.code, left_table)
            #     worksheet1.write(i, 14, '', center_table)
            #     worksheet1.write(i, 15, item.name if item.name else '', left_table)
            #     worksheet1.write(i, 16, bill.payment_reference if bill.payment_reference else '', left_table)
            #     i += 1
            #
            # worksheet1.write(i, 11, 'Sub Total', left_table)
            # worksheet1.write(i, 12, sum(item.balance for item in bill.line_ids), numb_table)
            # i += 1

        i += 1

        # worksheet1.write(i, 10, 'Grand Total', left_footer)
        # worksheet1.write(i, 11, sum(bill.amount_total for bill in bills_ids), numb_table)

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.trial.balance.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
