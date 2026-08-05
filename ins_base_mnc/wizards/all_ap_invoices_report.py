from calendar import monthrange
from datetime import datetime, date
from io import BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name as xlcol
from odoo import api, fields, models


# LAST_2_YEARS = datetime.now().year - 2
# NEXT_2_YEARS = datetime.now().year + 2
# CURRENT_YEAR = datetime.now().year
# YEARS = [(str(year), str(year)) for year in range(LAST_2_YEARS, NEXT_2_YEARS)]


class AllAPInvoicesReport(models.TransientModel):
    _name = 'wizard.all.ap.invoices.report'
    _description = 'All AP Invoices Report'

    date = fields.Date('Print Date', default=date.today())

    def _prepare_report_data(self):
        """ function to prepare report data containing list of dict """
        result = []

        # get invoices (account.move)
        # VALID_TYPES = ('in_invoice')
        domain = [
            ('move_type', '=', 'in_invoice'),
        ]
        # ('move_id.company_id', '=', self.env.company.id),
        moves = self.env['account.move'].search(domain)

        for move in moves:
            partner = move.partner_id
            date_invoice = (move.invoice_date).strftime('%d-%b-%y') if move.invoice_date else ''
            date_gl = (move.date).strftime('%d-%b-%y') if move.date else ''
            pay_state = dict(move._fields['payment_state'].selection).get(move.payment_state)

            post_status = ''
            if move.state != 'posted':
                post_status = 'N'
            else:
                post_status = 'Y'

            pph = 0.0
            ppn = 0.0
            if move.amount_tax < 0:
                pph = move.amount_tax
            else:
                ppn = move.amount_tax

            paid_amount = 0.0
            if move.state != 'draft':
                paid_amount = move.amount_total - move.amount_residual

            data = {
                'name': partner.name,
                'invoice_date': date_invoice,
                'gl_date': date_gl,
                'invoice_type': move.bill_type,
                'invoice_number': move.name,
                'currency': move.currency_id.name,
                'dpp': move.amount_untaxed,
                'pph': pph,
                'ppn': ppn,
                'invoice_amount': move.amount_total,
                'amount_paid': paid_amount,
                'payment_status': pay_state,
                'posting_status': post_status,
                'approval_status': 'APPROVED',
            }
            result.append(data)

        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        # name = 'Standard AP Detail %s' % (self.year)
        name = 'All AP Invoices'
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_xlsx(self, response, data={}):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('All AP Invoices')

        # styles
        white_bg = wb.add_format({'bg_color': 'white'})

        # title: bold 14 center
        s_title = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 14, 'font_name': 'Arial',
            'valign': 'vcenter',
        })

        # header: 8 bold border center
        s_header = wb.add_format({
            'bold': 1, 'align': 'center', 'font_name': 'Arial', 'font_size': 8,
            'valign': 'vcenter', 'num_format': '#,###', 'border': 1,
        })

        # normal: 8 border
        s_normal = wb.add_format({
            'font_name': 'Arial', 'font_size': 8, 'num_format': '#,###',
            'border': 1,
        })

        # normal_bold: 8 border bold
        s_normal_bold = wb.add_format({
            'font_name': 'Arial', 'font_size': 8, 'num_format': '#,###',
            'border': 1, 'bold': 1,
        })

        # set column width
        widths = [30, 15, 15, 20, 20, 10, 20, 20, 20, 20, 20,
                  15, 10, 20]
        for idx, width in enumerate(widths):
            ws.set_column(idx, idx, width, white_bg)

        row = col = 0

        # period = date(int(self.year), int(self.month), 1)
        # str_year = period.strftime('%y')
        # period = period.strftime('%b %Y')
        ws.merge_range('A1:N1', 'REPORT AP ALL INVOICES', s_title)

        # headers are directly generated due to the fixed nature
        ws.write('A3', 'Supplier Name', s_header)
        ws.write('B3', 'Invoice Date', s_header)
        ws.write('C3', 'GL Date', s_header)
        ws.write('D3', 'Invoice Type', s_header)
        ws.write('E3', 'Invoice Number', s_header)
        ws.write('F3', 'Currency', s_header)
        ws.write('G3', 'DPP', s_header)
        ws.write('H3', 'PPH', s_header)
        ws.write('I3', 'PPN', s_header)
        ws.write('J3', 'Invoice Amount', s_header)
        ws.write('K3', 'Amount Paid', s_header)
        ws.write('L3', 'Payment Status', s_header)
        ws.write('M3', 'Posting Status', s_header)
        ws.write('N3', 'Approval Status', s_header)

        row += 3

        start_row = row + 1  # real row
        for dt in data:
            for idx, value in enumerate(dt.values()):
                ws.write(row, col + idx, value, s_normal)
            row += 1

        end_row = row  # real row

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
