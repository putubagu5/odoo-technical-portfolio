from datetime import date
from io import BytesIO
import xlsxwriter
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StandardAPDetailReport(models.TransientModel):
    _name = 'wizard.standard.ap.detail.report'
    _description = 'Standard AP Detail Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_to < self.date_from:
            raise ValidationError('Date From could not be later than Date To')

    def _prepare_report_data(self):
        """ function to prepare report data containing list of dict """
        result = []

        # get invoices (account.move)
        VALID_TYPES = ('entry', 'in_invoice', 'in_refund', 'in_receipt')
        domain = [
            ('payment_id', '!=', False),
            ('payment_id.state', 'not in', ('draft',)),
            ('move_id.move_type', 'in', VALID_TYPES),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
        ]
        # ('move_id.company_id', '=', self.env.company.id),
        payments = self.env['account.payment.invoice'].search(domain)
        no = 1

        for line in payments:
            move = line.move_id
            payment = line.payment_id
            partner = move.partner_id
            date_invoice = (move.invoice_date).strftime('%d-%b-%y') if move.invoice_date else ''
            date_gl = (move.date).strftime('%d-%b-%y') if move.date else ''
            date_pmt = (payment.date).strftime('%d-%b-%y') if payment.date else ''

            post_status = ''
            if move.state != 'posted':
                post_status = 'N'
            else:
                post_status = 'Y'

            payment_status = ''
            if payment.is_matched is True:
                payment_status = 'Reconciled'
            else:
                payment_status = 'Unreconciled'

            data = {
                'no': no,
                'company': '30001',
                'account_dist': partner.property_account_payable_id.code,
                'cost_center': '000',
                'wilayah': '0000',
                'supplier_name': partner.name,
                'supplier_id': partner.partner_no,
                'supplier_site': payment.site_id.name or '',
                'employee_supplier': '-',
                'invoice_number': move.name,
                'invoice_reference': move.payment_reference,
                'invoice_date': date_invoice,
                'gl_date': date_gl,
                'description': move.ref,
                'voucher_num': '',
                'curr': move.currency_id.name,
                'approval_status': 'APPROVED',
                'posted_flag': post_status,
                'exchange_rate': move.currency_id.rate,
                'invoice_amount': move.amount_total,
                'appl_gl_date': '-',
                'appl_voucher_num': '-',
                'appl_invoice_num': '-',
                'appl_invoice_amount': '-',
                'check_voucher_num': payment.multi_payment_reference or '',
                'payment_date': date_pmt,
                'supplier_for_filter': payment.partner_id.name or '',
                'check_number': payment.multi_payment_reference or '',
                'payment_amount': payment.amount or 0,
                'status': payment_status,
                'check_remit_status': '-',
                'amount_remaining': move.amount_residual,
                'paid_amount_remaining': '-',
                'remit_status': '-',
            }
            no += 1
            result.append(data)

        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'Standard AP Detail'
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_xlsx(self, response, data={}):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('Standard AP Detail')

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

        date_print = date.today().strftime('%d-%b-%y').upper()
        date_from = self.date_from.strftime('%d-%b-%y').upper()
        date_to = self.date_to.strftime('%d-%b-%y').upper()

        # set column width
        widths = [15, 10, 15, 10, 10, 30, 15, 15, 15, 30, 30, 10,
                  10, 100, 10, 5, 15, 10, 10, 15, 10, 30, 15, 15,
                  15, 15, 30, 15, 15, 15, 15, 15, 20, 15]
        for idx, width in enumerate(widths):
            ws.set_column(idx, idx, width, white_bg)

        row = col = 0

        ws.merge_range('A1:AG1', 'RINCIAN AP STANDARD', s_title)
        ws.write('A3', 'Period')
        ws.write('A4', 'Company')
        ws.write('A5', 'Currency')
        ws.write('A6', 'Supplier')
        ws.write('A7', 'Account')
        ws.write('A8', 'Outstanding')
        ws.write('B3', ':')
        ws.write('B4', ':')
        ws.write('B5', ':')
        ws.write('B6', ':')
        ws.write('B7', ':')
        ws.write('B8', ':')
        ws.write('C3', date_from + ' to ' + date_to)
        ws.write('C4', 'ALL COMPANY')
        ws.write('C5', 'ALL CURRENCY')
        ws.write('C6', 'ALL SUPPLIER')
        ws.write('C7', 'ALL ACCOUNT')
        ws.write('C8', 'YES')
        ws.write('U5', 'Print Date : %s' % date_print)
        ws.write('U6', 'User : %s' % self.env.user.name or '')
        ws.write('U7', 'Page : 1 of 1')

        # headers are directly generated due to the fixed nature
        ws.write('A10', '', s_header)
        ws.merge_range('B10:T10', 'Invoice Standard', s_header)
        ws.merge_range('U10:X10', 'Applied Invoice', s_header)
        ws.merge_range('Y10:AE10', 'Payment', s_header)
        ws.merge_range('AF10:AF11', 'Amount Remaining', s_header)
        ws.merge_range('AG10:AG11', 'Paid Amount Remaining', s_header)
        ws.merge_range('AH10:AH11', 'Remit Status', s_header)
        ws.write('A11', 'No', s_header)
        ws.write('B11', 'Company', s_header)
        ws.write('C11', 'Account Dist.', s_header)
        ws.write('D11', 'Cost Center', s_header)
        ws.write('E11', 'Wilayah', s_header)
        ws.write('F11', 'Supplier Name', s_header)
        ws.write('G11', 'Supplier ID', s_header)
        ws.write('H11', 'Supplier Site', s_header)
        ws.write('I11', 'Employee / Supplier', s_header)
        ws.write('J11', 'Invoice Number', s_header)
        ws.write('K11', 'Invoice Reference', s_header)
        ws.write('L11', 'Invoice Date', s_header)
        ws.write('M11', 'GL Date', s_header)
        ws.write('N11', 'Description', s_header)
        ws.write('O11', 'Voucher Num', s_header)
        ws.write('P11', 'Curr', s_header)
        ws.write('Q11', 'Approval Status', s_header)
        ws.write('R11', 'Posted Flag', s_header)
        ws.write('S11', 'Exchange Rate', s_header)
        ws.write('T11', 'Invoice Amount', s_header)
        ws.write('U11', 'GL Date', s_header)
        ws.write('V11', 'Voucher Num', s_header)
        ws.write('W11', 'Invoice Num', s_header)
        ws.write('X11', 'Invoice Amount', s_header)
        ws.write('Y11', 'Check Voucher Num', s_header)
        ws.write('Z11', 'Payment Date', s_header)
        ws.write('AA11', 'Supplier For Filter', s_header)
        ws.write('AB11', 'Check Number', s_header)
        ws.write('AC11', 'Payment Amount', s_header)
        ws.write('AD11', 'Status', s_header)
        ws.write('AE11', 'Check Remit Status', s_header)

        row += 11

        start_row = row + 1  # real row
        for dt in data:
            for idx, value in enumerate(dt.values()):
                ws.write(row, col + idx, value, s_normal)
            row += 1

        end_row = row  # real row
        # total columns
        ws.merge_range('A%s:S%s' % (row + 1, row + 1), 'TOTAL:', s_normal)
        ws.write('T%s' % (row + 1), '=SUM(T%s:T%s)' % (start_row, end_row), s_normal)
        ws.merge_range('U%s:AB%s' % (row + 1, row + 1), '', s_normal)
        ws.write('AC%s' % (row + 1), '=SUM(AC%s:AC%s)' % (start_row, end_row), s_normal)
        ws.merge_range('AD%s:AE%s' % (row + 1, row + 1), '', s_normal)
        ws.write('AF%s' % (row + 1), '=SUM(AF%s:AF%s)' % (start_row, end_row), s_normal)
        ws.merge_range('AG%s:AH%s' % (row + 1, row + 1), '', s_normal)

        row += 3

        ws.write(row, col + 21, 'Currency', s_header)
        ws.write(row + 1, col + 21, 'EUR', s_normal)
        ws.write(row + 2, col + 21, 'HKD', s_normal)
        ws.write(row + 3, col + 21, 'IDR', s_normal)
        ws.write(row + 4, col + 21, 'SGD', s_normal)
        ws.write(row + 5, col + 21, 'USD', s_normal)
        ws.write(row, col + 22, 'Total Amount', s_header)
        ws.write(row + 1, col + 22, '=SUMIF(P%s:P%s,"EUR", T%s:T%s)' % (start_row, end_row, start_row, end_row), s_normal)
        ws.write(row + 2, col + 22, '=SUMIF(P%s:P%s,"HKD", T%s:T%s)' % (start_row, end_row, start_row, end_row), s_normal)
        ws.write(row + 3, col + 22, '=SUMIF(P%s:P%s,"IDR", T%s:T%s)' % (start_row, end_row, start_row, end_row), s_normal)
        ws.write(row + 4, col + 22, '=SUMIF(P%s:P%s,"SGD", T%s:T%s)' % (start_row, end_row, start_row, end_row), s_normal)
        ws.write(row + 5, col + 22, '=SUMIF(P%s:P%s,"USD", T%s:T%s)' % (start_row, end_row, start_row, end_row), s_normal)

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
