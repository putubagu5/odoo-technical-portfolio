from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar


class WizardMncArReceiptInvoiceReport(models.TransientModel):
    _name = 'wizard.mnc.ar.receipt.invoice.report'

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
    is_date_range = fields.Boolean(string="Custom Date Range", default=False)
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
    currency_id = fields.Many2one(comodel_name="res.currency", default=_get_default_currency_id, string="Currency")
    file = fields.Binary('File')

    @api.onchange('company_id')
    def onchange_company_id(self):
        return {'domain': {
            'company_id': [
                ('id', 'in', self.env.user.company_ids.ids),
            ]
        }
        }

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
        header_table.set_border()
        #################################################################################
        center_table = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_table.set_font_size('11')
        center_table.set_border()
        #################################################################################
        left_table = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_table.set_font_size('11')
        left_table.set_border()
        #################################################################################
        numb_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_table.set_font_size('11')
        numb_table.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 15)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 30)
        worksheet1.set_column('E:E', 15)
        worksheet1.set_column('F:F', 2)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 15)
        worksheet1.set_column('L:L', 15)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AR - Receipt to Invoice Report"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'REPORT RECEIPT - INVOICE AR DETAIL', left_title_sub)
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
        worksheet1.write(i, 0, 'Currency Code', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, self.currency_id.name, left_title_sub)
        worksheet1.write(i, 4, 'User', left_title_sub)
        worksheet1.write(i, 5, ':', center_title_sub)
        worksheet1.write(i, 6, self.env.user.name, left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'MONTH', header_table)
        worksheet1.write(i, 2, 'CUSTOMER NUMBER', header_table)
        worksheet1.write(i, 3, 'CUSTOMER NAME', header_table)
        worksheet1.merge_range(i, 4, i, 5, 'RECEIPT NUMBER', header_table)
        worksheet1.write(i, 6, 'RECEIPT DATE', header_table)
        worksheet1.write(i, 7, 'RECEIPT AMOUNT', header_table)
        worksheet1.write(i, 8, 'INVOICE NUMBER', header_table)
        worksheet1.write(i, 9, 'INVOICE DATE', header_table)
        worksheet1.write(i, 10, 'INVOICE AMOUNT', header_table)
        worksheet1.write(i, 11, 'COA INVOICE', header_table)
        i += 1

        query = """ 
                    SELECT inv.id
                        FROM applied_invoices AS inv
                            INNER JOIN miscellaneous_miscellaneous misc ON misc.id=inv.misc_id
                            INNER JOIN account_move move ON move.id=misc.move_id
                    WHERE misc.company_id=%s AND move.state='posted'
                """
        params = (self.company_id.id,)
        if self.is_date_range:
            query += ' AND move.date >= %s AND move.date <= %s'
            params += (self.start_date, self.end_date,)
        else:
            end_day = calendar.monthrange(int(self.year), int(self.month))[1]
            end_period = datetime.strptime(str(self.year) + '-' + str(self.month) + '-' + str(end_day), "%Y-%m-%d")

            query += " AND move.date <= %s"
            params += (end_period,)

        if self.currency_id:
            query += ' AND misc.currency_id = %s'
            params += (self.currency_id.id,)
        query += ' ORDER BY move.date asc'

        self._cr.execute(query, params)

        applied_invoice_ids = self.env['applied.invoices'].browse([r[0] for r in self._cr.fetchall()])
        for inv in applied_invoice_ids:
            worksheet1.merge_range(i, 0, i, 1, datetime.strptime(str(inv.misc_id.date), "%Y-%m-%d").strftime(
                "%b-%y") if inv.misc_id.date else '', left_table)
            worksheet1.write(i, 2, inv.misc_id.misc_partner_id.partner_no, left_table)
            worksheet1.write(i, 3, inv.misc_id.misc_partner_id.alias_name, left_table)
            worksheet1.merge_range(i, 4, i, 5, inv.misc_id.receipt_number, left_table)
            worksheet1.write(i, 6, datetime.strptime(str(inv.misc_id.date), "%Y-%m-%d").strftime(
                "%d-%b-%y") if inv.misc_id.date else '', left_table)
            worksheet1.write(i, 7, inv.misc_id.amount, numb_table)
            worksheet1.write(i, 8, inv.invoice_id.name, left_table)
            worksheet1.write(i, 9, datetime.strptime(str(inv.invoice_id.invoice_date), "%Y-%m-%d").strftime(
                "%d-%b-%y") if inv.invoice_id.invoice_date else '', left_table)
            worksheet1.write(i, 10, inv.invoice_id.amount_total, numb_table)
            worksheet1.write(i, 11,
                             inv.invoice_id.transaction_type_id.account_id.code if inv.invoice_id.transaction_type_id.account_id else '',
                             left_table)
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ar.receipt.invoice.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
