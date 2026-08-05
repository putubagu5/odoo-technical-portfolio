from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncArStatementAccountReport(models.TransientModel):
    _name = 'wizard.mnc.ar.statement.account.report'

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
    all_partner = fields.Boolean(string="All Customer", default=True)
    partner_ids = fields.Many2many("res.partner", string="Customer")
    month = fields.Selection([
        ('01', 'Jan'),
        ('02', 'Feb'),
        ('03', 'Mar'),
        ('04', 'Apr'),
        ('05', 'May'),
        ('06', 'Jun'),
        ('07', 'Jul'),
        ('08', 'Aug'),
        ('09', 'Sep'),
        ('10', 'Oct'),
        ('11', 'Nov'),
        ('12', 'Dec')
    ], string="Month")
    year = fields.Selection(
        selection="get_year_selection",
        default=get_this_year,
        string="Year"
    )
    file = fields.Binary("File")

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

    def button_print_excel(self):
        self.ensure_one()

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        left_title = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title.set_font_size('15')
        left_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_title_sub.set_font_size('13')
        #################################################################################
        header_table = workbook.add_format({'valign': 'vcenter', 'align': 'center', 'font_color': '#FFFFFF'})
        header_table.set_font_size('12')
        header_table.set_bg_color('#02569C')
        header_table.set_border()
        header_table.set_text_wrap()
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
        int_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0'})
        int_table.set_font_size('11')
        int_table.set_border()
        #################################################################################
        right_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer.set_font_size('12')
        right_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('12')
        numb_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 20)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 100)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 20)
        worksheet1.set_column('I:I', 20)
        worksheet1.set_column('J:J', 20)
        worksheet1.set_column('K:K', 20)
        worksheet1.set_column('L:L', 20)
        worksheet1.set_column('M:M', 20)
        worksheet1.set_column('N:N', 20)
        worksheet1.set_column('O:O', 20)
        worksheet1.set_column('P:P', 20)
        worksheet1.set_column('Q:Q', 20)
        worksheet1.set_column('R:R', 20)
        worksheet1.set_column('S:S', 20)
        worksheet1.set_column('T:T', 20)
        worksheet1.set_column('U:U', 20)
        worksheet1.set_column('V:V', 20)
        worksheet1.set_column('W:W', 20)
        worksheet1.set_column('X:X', 20)
        worksheet1.set_column('Y:Y', 20)
        worksheet1.set_column('Z:Z', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AR - Statement of Account Report for Collector"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'STATEMENT OF ACCOUNT REPORT FOR COLLECTOR', left_title)
        i = 3
        worksheet1.write(i, 0, 'Customer', left_title_sub)
        worksheet1.write(i, 1, ': ' + ('All' if self.all_partner else self.get_partner()), left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'Period', left_title_sub)
        worksheet1.write(i, 1, ': ' + dict(self._fields['month'].selection).get(self.month) + '-' + self.year,
                         left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'INVOICE NUMBER', header_table)
        worksheet1.write(i, 1, 'ORIGINAL INVOICE NUMBER', header_table)
        worksheet1.write(i, 2, 'INVOICE DATE', header_table)
        worksheet1.write(i, 3, 'GL DATE', header_table)
        worksheet1.write(i, 4, 'INVOICE DUE DATE', header_table)
        worksheet1.write(i, 5, 'DESCRIPTION', header_table)
        worksheet1.write(i, 6, 'PO NUMBER', header_table)
        worksheet1.write(i, 7, 'MO NUMBER', header_table)
        worksheet1.write(i, 8, 'STASIUN', header_table)
        worksheet1.write(i, 9, 'BRAND', header_table)
        worksheet1.write(i, 10, 'ADVERTISER', header_table)
        worksheet1.write(i, 11, 'RECEIPT/CN-DN NUMBER', header_table)
        worksheet1.write(i, 12, 'RECEIPT/CN-DN DATE', header_table)
        worksheet1.write(i, 13, 'APPLY DATE', header_table)
        worksheet1.write(i, 14, 'CLEARED DATE', header_table)
        worksheet1.write(i, 15, 'RECEIPT DUE DATE', header_table)
        worksheet1.write(i, 16, 'INVOICE AFTER PPH AMOUNT', header_table)
        worksheet1.write(i, 17, 'PPH AMOUNT', header_table)
        worksheet1.write(i, 18, 'PPN AMOUNT', header_table)
        worksheet1.write(i, 19, 'TOTAL INVOICE AMOUNT', header_table)
        worksheet1.write(i, 20, 'APPLIED AMOUNT', header_table)
        worksheet1.write(i, 21, 'OUTSTANDING AMOUNT', header_table)
        worksheet1.write(i, 22, 'ADJUSTMENT', header_table)
        worksheet1.write(i, 23, 'PPh 23', header_table)
        worksheet1.write(i, 24, 'DISCOUNT', header_table)
        worksheet1.write(i, 25, 'UMUR PIUTANG', header_table)
        i += 1

        move_vals = []

        end_day = calendar.monthrange(int(self.year), int(self.month))[1]
        end_period = datetime.strptime(str(self.year) + '-' + str(self.month) + '-' + str(end_day), "%Y-%m-%d")

        query = """ 
                    SELECT mv.id
                        FROM account_move AS mv
                    WHERE mv.invoice_date IS NOT NULL AND mv.company_id=%s AND mv.move_type='out_invoice' AND mv.invoice_date <= %s AND mv.state='posted'
                """
        params = (self.company_id.id, end_period,)
        if not self.all_partner:
            query += ' AND mv.partner_id IN %s'
            params += (tuple(self.partner_ids.ids),)

        query += ' ORDER BY mv.invoice_date asc'
        self._cr.execute(query, params)

        move_ids = self.env['account.move'].sudo().browse([r[0] for r in self._cr.fetchall()])
        for move in move_ids:
            move_vals.append({
                'move_id': move.id,
                'invoice_date': move.invoice_date,
                'myear': datetime.strptime(str(move.invoice_date), "%Y-%m-%d").strftime("%b-%Y")
            })

        grouped = collections.defaultdict(list)
        for item in move_vals:
            grouped[item['myear']].append(item)

        for myear, items in grouped.items():
            amount_invoice_after_pph = 0
            amount_pph = 0
            amount_ppn = 0
            amount_invoice = 0
            amount_payment = 0
            amount_outstanding = 0
            amount_adjustment = 0
            amount_pph23 = 0
            amount_dicount = 0
            for item in items:
                move_id = self.env['account.move'].sudo().browse(item['move_id'])

                if move_id.is_pph_amount_info == True:
                    invoice_after_pph = move_id.amount_total - move_id.pph_amount
                else:
                    invoice_after_pph = 0

                aged_day = 0
                if move_id.amount_residual > 0 and move_id.invoice_date_due:
                    aged_day = int((end_period - datetime.strptime(str(move_id.invoice_date_due), "%Y-%m-%d")).days)

                worksheet1.write(i, 0, move_id.name, left_table)
                worksheet1.write(i, 1, move_id.payment_reference if move_id.payment_reference else '', left_table)
                worksheet1.write(i, 2, datetime.strptime(str(move_id.invoice_date), "%Y-%m-%d").strftime(
                    "%d-%b-%Y") if move_id.invoice_date else '', left_table)
                worksheet1.write(i, 3, datetime.strptime(str(move_id.invoice_date), "%Y-%m-%d").strftime(
                    "%d-%b-%Y") if move_id.invoice_date else '', left_table)
                worksheet1.write(i, 4, datetime.strptime(str(move_id.invoice_date_due), "%Y-%m-%d").strftime(
                    "%d-%b-%Y") if move_id.invoice_date_due else '', left_table)
                worksheet1.write(i, 5, move_id.ref if move_id.ref else '', left_table)
                worksheet1.write(i, 6, move_id.po_numbers_gen21 if move_id.po_numbers_gen21 else '', left_table)
                worksheet1.write(i, 7, move_id.mo_numbers_gen21 if move_id.mo_numbers_gen21 else '', left_table)
                worksheet1.write(i, 8, '', left_table)
                worksheet1.write(i, 9, move_id.product_gen21 if move_id.product_gen21 else '', left_table)
                worksheet1.write(i, 10, move_id.advertiser_gen21 if move_id.advertiser_gen21 else '', left_table)
                worksheet1.write(i, 11,
                                 move_id.applied_misc_ids[0].misc_id.receipt_number if move_id.applied_misc_ids else '',
                                 left_table)
                worksheet1.write(i, 12,
                                 datetime.strptime(str(move_id.applied_misc_ids[0].misc_id.date), "%Y-%m-%d").strftime(
                                     "%d-%b-%Y") if move_id.applied_misc_ids else '', left_table)
                worksheet1.write(i, 13, datetime.strptime(str(move_id.applied_misc_ids[0].date), "%Y-%m-%d").strftime(
                    "%d-%b-%Y") if move_id.applied_misc_ids else '', left_table)
                worksheet1.write(i, 14, datetime.strptime(str(move_id.applied_misc_ids[0].date), "%Y-%m-%d").strftime(
                    "%d-%b-%Y") if move_id.applied_misc_ids else '', left_table)
                # worksheet1.write(i, 14, datetime.strptime(str(move_id.applied_misc_ids.filtered(lambda m: m.misc_id.is_matched == True).date), "%Y-%m-%d").strftime("%d-%b-%Y") if move_id.applied_misc_ids else '', left_table)
                worksheet1.write(i, 15, move_id.invoice_payment_term_id.name or '', left_table)
                worksheet1.write(i, 16, invoice_after_pph, numb_table)
                worksheet1.write(i, 17, move_id.pph_amount, numb_table)
                worksheet1.write(i, 18, move_id.amount_tax, numb_table)
                worksheet1.write(i, 19, move_id.amount_total, numb_table)
                worksheet1.write(i, 20, move_id.amount_total - move_id.amount_residual, numb_table)
                worksheet1.write(i, 21, move_id.amount_residual, numb_table)
                worksheet1.write(i, 22, move_id.adjustment_amount, numb_table)
                worksheet1.write(i, 23, 0, numb_table)
                worksheet1.write(i, 24, 0, numb_table)
                worksheet1.write(i, 25, aged_day, int_table)

                amount_invoice_after_pph += invoice_after_pph
                amount_pph += move_id.pph_amount
                amount_ppn += move_id.amount_tax
                amount_invoice += move_id.amount_total
                amount_payment += move_id.amount_total - move_id.amount_residual
                amount_outstanding += move_id.amount_residual
                amount_adjustment += move_id.adjustment_amount
                amount_pph23 += 0
                amount_dicount += 0
                i += 1

            worksheet1.merge_range(i, 0, i, 15, 'Total ' + str(myear), right_footer)
            worksheet1.write(i, 16, amount_invoice_after_pph, numb_footer)
            worksheet1.write(i, 17, amount_pph, numb_footer)
            worksheet1.write(i, 18, amount_ppn, numb_footer)
            worksheet1.write(i, 19, amount_invoice, numb_footer)
            worksheet1.write(i, 20, amount_payment, numb_footer)
            worksheet1.write(i, 21, amount_outstanding, numb_footer)
            worksheet1.write(i, 22, amount_adjustment, numb_footer)
            worksheet1.write(i, 23, amount_pph23, numb_footer)
            worksheet1.write(i, 24, amount_dicount, numb_footer)
            worksheet1.write(i, 25, '', right_footer)
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ar.statement.account.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
