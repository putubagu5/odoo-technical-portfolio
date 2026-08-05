from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncArPph23Report(models.TransientModel):
    _name = 'wizard.mnc.ar.pph23.report'

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
    file = fields.Binary("File")

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
        #################################################################################
        left_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_footer.set_font_size('11')
        left_footer.set_border()
        #################################################################################
        right_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer.set_font_size('11')
        right_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('11')
        numb_footer.set_border()
        #################################################################################
        right_footer_no_border = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer_no_border.set_font_size('11')
        #################################################################################
        numb_footer_no_border = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer_no_border.set_font_size('11')

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 5)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 20)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 20)
        worksheet1.set_column('I:I', 20)
        worksheet1.set_column('J:J', 20)
        worksheet1.set_column('K:K', 20)
        worksheet1.set_column('L:L', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AR - Bukti Potong PPh 23"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'AR PPH 23 SUMMARY REPORT', left_title)
        i = 2
        if self.is_date_range:
            worksheet1.merge_range(i, 0, i, 1, 'Dates', left_title_sub)
            worksheet1.write(i, 2,
                             ': ' + datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d/%m/%Y") + ' - ' + \
                             datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d/%m/%Y"), left_title_sub)
        else:
            worksheet1.merge_range(i, 0, i, 1, 'As of Period', left_title_sub)
            worksheet1.write(i, 2, ': ' + dict(self._fields['month'].selection).get(self.month) + '-' + self.year,
                             left_title_sub)
        i += 1
        worksheet1.merge_range(i, 0, i, 1, 'Print Date', left_title_sub)
        worksheet1.write(i, 2, ': ' + datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                         left_title_sub)
        i += 2

        worksheet1.write(i, 0, 'No', header_table)
        worksheet1.merge_range(i, 1, i, 2, 'Customer Name', header_table)
        worksheet1.write(i, 3, 'PPH23 Receipt Num', header_table)
        worksheet1.write(i, 4, 'Receipt Date', header_table)
        worksheet1.write(i, 5, 'PPH23 Receipt Amount', header_table)
        worksheet1.write(i, 6, 'GL Date', header_table)
        worksheet1.write(i, 7, 'Reference No', header_table)
        worksheet1.write(i, 8, 'Invoice Number', header_table)
        worksheet1.write(i, 9, 'PPH23 Amount Applied', header_table)
        worksheet1.write(i, 10, 'Outstanding', header_table)
        i += 1

        query = """ 
                    SELECT inv.id
                        FROM applied_invoices AS inv
                            INNER JOIN miscellaneous_miscellaneous misc ON misc.id=inv.misc_id
                            INNER JOIN account_move move ON move.id=misc.move_id
                    WHERE misc.company_id=%s AND misc.bukti_potong IS NOT NULL AND move.state='posted'
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
        query += ' ORDER BY move.date asc'

        self._cr.execute(query, params)
        data_vals = []

        applied_invoice_ids = self.env['applied.invoices'].browse([r[0] for r in self._cr.fetchall()])
        for inv in applied_invoice_ids:
            data_vals.append({
                'partner_id': inv.misc_id.misc_partner_id.id,
                'partner_name': inv.misc_id.misc_partner_id.name,
                'bukti_potong': inv.misc_id.bukti_potong,
                'transaction_date': inv.transaction_date,
                'amount': inv.misc_id.amount,
                'date': inv.misc_id.date,
                'receipt_number': inv.misc_id.receipt_number,
                'invoice_number': inv.invoice_id.name,
                'applied_amount': inv.applied_amount,
                'amount_remaining': inv.misc_id.remaining_amount
            })

        grouped = collections.defaultdict(list)
        for item in data_vals:
            grouped[item['partner_id']].append(item)

        index = 1
        for partner, items in grouped.items():
            partner_id = self.env['res.partner'].sudo().browse(partner)

            worksheet1.merge_range(i, 0, i + len(items), 0, index, center_table)
            worksheet1.merge_range(i, 1, i + len(items), 2, partner_id.name, left_table)

            for item in items:
                worksheet1.write(i, 3, item['bukti_potong'], left_table)
                worksheet1.write(i, 4, datetime.strptime(str(item['transaction_date']), "%Y-%m-%d %H:%M:%S").strftime(
                    "%d-%b-%y") if item['transaction_date'] else '', center_table)
                worksheet1.write(i, 5, item['amount'], numb_table)
                worksheet1.write(i, 6, datetime.strptime(str(item['date']), "%Y-%m-%d").strftime("%d-%b-%y") if item[
                    'date'] else '', center_table)
                worksheet1.write(i, 7, item['receipt_number'] if item['receipt_number'] else '', left_table)
                worksheet1.write(i, 8, item['invoice_number'], left_table)
                worksheet1.write(i, 9, item['applied_amount'], numb_table)
                worksheet1.write(i, 10, item['amount_remaining'], numb_table)
                i += 1

            worksheet1.merge_range(i, 3, i, 4, 'Subtotal', right_footer)
            worksheet1.write(i, 5, sum(item['amount'] for item in items), numb_footer)
            worksheet1.write(i, 6, '', right_footer)
            worksheet1.write(i, 7, '', right_footer)
            worksheet1.write(i, 8, '', right_footer)
            worksheet1.write(i, 9, sum(item['applied_amount'] for item in items), numb_footer)
            worksheet1.write(i, 10, sum(item['amount_remaining'] for item in items), numb_footer)

            index += 1
            i += 1

        worksheet1.merge_range(i, 3, i, 4, 'Grand Total', right_footer_no_border)
        worksheet1.write(i, 5, sum(item['amount'] for item in data_vals), numb_footer_no_border)
        worksheet1.write(i, 6, '', right_footer_no_border)
        worksheet1.write(i, 7, '', right_footer_no_border)
        worksheet1.write(i, 8, '', right_footer_no_border)
        worksheet1.write(i, 9, sum(item['applied_amount'] for item in data_vals), numb_footer_no_border)
        worksheet1.write(i, 10, sum(item['amount_remaining'] for item in data_vals), numb_footer_no_border)

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ar.pph23.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
