from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar


class WizardMncAccountCollectorReport(models.TransientModel):
    _name = 'wizard.account.collector.report'

    @api.model
    def _get_default_company_id(self):
        return self.env.user.company_id.id

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

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=_get_default_company_id)
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
    file = fields.Binary("File")

    @api.onchange('company_id')
    def onchange_company_id(self):
        return {'domain': {
            'company_id': [
                ('id', 'in', self.env.user.company_ids.ids),
            ]
        }
        }

    def get_partner_name(self):
        self.ensure_one()

        partner_name = ''
        for partner in self.partner_ids:
            if partner_name == '':
                partner_name = partner.name
            else:
                partner_name += ', ' + partner.name

        return partner_name

    def get_account_transaction(self):
        self.ensure_one()

        account_transaction = ''
        for account in self.account_transaction_ids:
            if account_transaction == '':
                account_transaction = account.name
            else:
                account_transaction += ', ' + account.name

        return account_transaction

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
        left_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_footer.set_font_size('12')
        # left_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 25)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:C', 28)
        worksheet1.set_column('D:D', 25)
        worksheet1.set_column('E:E', 2)
        worksheet1.set_column('F:G', 25)
        worksheet1.set_column('H:H', 35)
        worksheet1.set_column('G:L', 30)
        worksheet1.set_column('M:P', 25)
        worksheet1.set_column('Q:Y', 30)
        worksheet1.set_column('Z:AB', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AR - Statement of Account for Collector"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'Statement Of Account For Collection Report', left_title_sub)
        i = 3
        worksheet1.write(i, 0, 'Customer Name', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, 'All Customer' if self.all_partner else self.get_partner_name(), left_title_sub)
        worksheet1.write(i, 3, 'Print Date', left_title_sub)
        worksheet1.write(i, 4, ':', center_title_sub)
        worksheet1.write(i, 5, datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                         left_title_sub)
        i += 1
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
        worksheet1.write(i, 3, 'User', left_title_sub)
        worksheet1.write(i, 4, ':', center_title_sub)
        worksheet1.write(i, 5, self.env.user.name, left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'INVOICE NUMBER', header_table)
        worksheet1.write(i, 2, 'ORIGINAL INVOICE NUMBER', header_table)
        worksheet1.merge_range(i, 3, i, 4, 'INVOICE DATE', header_table)
        worksheet1.write(i, 5, 'GL DATE', header_table)
        worksheet1.write(i, 6, 'INVOICE DUE DATE', header_table)
        worksheet1.write(i, 7, 'DESCRIPTION', header_table)
        worksheet1.write(i, 8, 'PO NUMBER', header_table)
        worksheet1.write(i, 9, 'MO NUMBER', header_table)
        worksheet1.write(i, 10, 'STASIUN', header_table)
        worksheet1.write(i, 11, 'BRAND', header_table)
        worksheet1.write(i, 12, 'ADVERTISER', header_table)
        worksheet1.write(i, 13, 'RECEIPT/CN-DN NUMBER', header_table)
        worksheet1.write(i, 14, 'RECEIPT/CN-DN DATE', header_table)
        worksheet1.write(i, 15, 'APPLY DATE', header_table)
        worksheet1.write(i, 16, 'CLEARED DATE', header_table)
        worksheet1.write(i, 17, 'RECEIPT DUE DATE', header_table)
        worksheet1.write(i, 18, 'INVOICE AFTER PPH AMOUNT', header_table)
        worksheet1.write(i, 19, 'PPH AMOUNT', header_table)
        worksheet1.write(i, 20, 'PPN AMOUNT', header_table)
        worksheet1.write(i, 21, 'TOTAL INVOICE AMOUNT', header_table)
        worksheet1.write(i, 22, 'APPLIED AMOUNT', header_table)
        worksheet1.write(i, 23, 'OUTSTANDING AMOUNT', header_table)
        worksheet1.write(i, 24, 'ADJUSMENT', header_table)
        worksheet1.write(i, 25, 'PPh 23', header_table)
        worksheet1.write(i, 26, 'DISCOUNT', header_table)
        worksheet1.write(i, 27, 'UMUR PIUTANG', header_table)
        i += 1

        query = """ 
                    SELECT rp.id
                        FROM account_move AS mv
                            INNER JOIN res_partner rp ON rp.id=mv.partner_id
                    WHERE mv.partner_id IS NOT NULL AND mv.move_type='out_invoice' AND mv.state='posted'
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

        query += ' GROUP BY rp.id ORDER BY rp.name asc'

        self._cr.execute(query, params)

        bills_ids = self.env['account.move'].browse([r[0] for r in self._cr.fetchall()])
        for bill in bills_ids:
            worksheet1.merge_range(i, 0, i, 1, bill.name if bill.name else '', left_table)  # invoice_number
            worksheet1.write(i, 2, bill.name if bill.name else '', left_table)  # original_invoice_number
            worksheet1.merge_range(i, 3, i, 4, bill.invoice_date if bill.invoice_date else '',
                                   center_table)  # invoice_date
            worksheet1.write(i, 5, "", left_table)  # gl_date
            worksheet1.write(i, 6, bill.invoice_payment_term_id.name if bill.invoice_payment_term_id.name else '',
                             left_table)  # invoice_due_date
            worksheet1.write(i, 7, bill.ref if bill.ref else '', center_table)  # description
            worksheet1.write(i, 8, bill.po_numbers if bill.po_numbers else '', center_table)  # po_number
            worksheet1.write(i, 9, "", center_table)  # mo_number
            worksheet1.write(i, 10, "", center_table)  # stasiun
            worksheet1.write(i, 11, "", center_table)  # brand
            worksheet1.write(i, 12, "", center_table)  # advertiser
            worksheet1.write(i, 13, "", center_table)  # receipt_number
            worksheet1.write(i, 14, "", center_table)  # receipt_date
            worksheet1.write(i, 15, "", center_table)  # apply_date
            worksheet1.write(i, 16, "", center_table)  # cleared_date
            worksheet1.write(i, 17, "", center_table)  # receipt_due_date
            worksheet1.write(i, 18, "", center_table)  # invoice_after_pph_amount
            worksheet1.write(i, 19, "", center_table)  # pph_amount
            worksheet1.write(i, 20, "", center_table)  # ppn_amount
            worksheet1.write(i, 21, "", center_table)  # total_invoice_amount
            worksheet1.write(i, 22, "", center_table)  # applied_amount
            worksheet1.write(i, 23, "", center_table)  # outstanding_amount
            worksheet1.write(i, 24, "", center_table)  # adjusment
            worksheet1.write(i, 25, "", center_table)  # pph23
            worksheet1.write(i, 26, "", center_table)  # discount
            worksheet1.write(i, 27, "", center_table)  # umur_piutang

            i += 1

        i += 1
        worksheet1.write(i, 2, 'Total Bulan', left_footer)
        worksheet1.write(i, 3, "", center_table)

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.account.collector.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
