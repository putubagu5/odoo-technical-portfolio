from datetime import date
from io import BytesIO
import xlsxwriter
from odoo import fields, models


class PaymentRecapReport(models.TransientModel):
    _name = 'wizard.payment.recap.report'
    _description = 'Payment Recap Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    all_companies = fields.Boolean('All Companies?', default=False)
    company_ids = fields.Many2many('res.company', string='Companies')
    all_accounts = fields.Boolean('All Accounts?', default=False)
    account_ids = fields.Many2many('account.account', string='Accounts')
    all_banks = fields.Boolean('All Banks?', default=False)
    bank_ids = fields.Many2many('res.bank', string='Banks')
    # TODO all branches and bank accounts
    all_currencies = fields.Boolean('All Currencies?', default=False)
    currency_ids = fields.Many2many('res.currency', string='Currencies')
    reconcile_state = fields.Selection([
        ('all', 'All'),
        ('reconciled', 'Reconciled'),
        ('unreconciled', 'Unreconciled'),
    ], 'Reconciled Status', default='all')

    def _prepare_report_data(self):
        """ function to prepare report data containing list of dict """
        result = []
        # take data from account.payment.invoice with payment_id, and the
        # payment_id.partner_type is supplier, with same company for move
        # and vendor bills only
        move = self.env['account.move']
        inv_state = dict(move._fields['state']._description_selection(self.env))
        pay_state = dict(self.env['account.payment.invoice']._fields['invoice_payment_state']._description_selection(self.env))
        VALID_TYPES = ('entry', 'in_invoice', 'in_refund', 'in_receipt')
        domain = [
            ('payment_id', '!=', False),
            ('payment_id.state', 'not in', ('draft', 'cancel')),
            ('move_id.move_type', 'in', VALID_TYPES),
            ('move_id.company_id', '=', self.env.company.id),
            ('payment_id.date', '>=', self.date_from),
            ('payment_id.date', '<=', self.date_to),
        ]
        payments = self.env['account.payment.invoice'].search(domain)
        for p in payments:
            pmt = p.payment_id
            acc_name = pmt.journal_id.bank_account_id.acc_holder_name or pmt.journal_id.bank_id.name
            acc_name = pmt.journal_id.name or ''
            # pmt_date = pmt.date.strftime('%d/%m/%y') if pmt.date else ''
            pmt_date = pmt.date
            rate = pmt.manual_currency_rate if pmt.manual_currency_rate_active else pmt.rate
            # date_gl = p.date_accounting.strftime('%d/%m/%y') if p.date_accounting else ''
            date_gl = p.date_accounting
            # date_recon = pmt.reconciliation_date.strftime('%d/%m/%y') if pmt.reconciliation_date else ''
            date_recon = pmt.reconciliation_date
            line = pmt.move_id.line_ids.filtered(lambda x: x.debit)
            check = pmt.check_id
            pdoc = pmt.payment_doc_id
            giro = pmt.giro_id
            method = check or pdoc or giro  # take one existing
            # date_cleared is taken from reconciled_statement_ids, but take only one
            stmt = pmt.reconciled_statement_ids.filtered(lambda x: x.date)
            # date_invoice = (p.move_id.invoice_date).strftime('%d/%m/%y') if p.move_id.invoice_date else ''
            date_invoice = p.move_id.invoice_date
            # date_cleared = (stmt[0].date).strftime('%d/%m/%y') if stmt and stmt.date else ''
            date_cleared = stmt[0].date if stmt and stmt.date else ''

            # NOTE: here we force-filter the status, if reconciled but no stmt
            # then just skip. Same thing applies if unreconciled and stmt exists
            if self.reconcile_state == 'reconciled' and not stmt:
                continue

            if self.reconcile_state == 'unreconciled' and stmt:
                continue

            # NOTE: sept 2022 combine cancel payment into reconciled status
            # and payment_doc_no to take series and journal name
            recon_status = 'Reconciled' if date_cleared or pmt.is_matched else 'In Payment'
            recon_status = 'Cancelled' if pmt.cancel_reversal else recon_status
            # payment_doc = '%s %s' % (pmt.payment_doc_master_id.name or '', pmt.journal_id.name)
            payment_doc = '%s %s' % (acc_name, pmt.payment_doc_master_id.name or pmt.giro_master_id.name or pmt.check_master_id.name or '')

            data = {
                'company': pmt.company_id.name,
                'bank_name': pmt.journal_id.bank_id.name,
                'branch': '',
                'account_name': acc_name or '',
                'account_no': pmt.journal_id.bank_account_id.acc_number or '',
                'date_check': pmt_date,
                'check_no': pmt.multi_payment_reference,
                'voucher_no': '',
                'payment_doc_no': payment_doc,
                'currency': p.currency_id.name,
                'rate': rate,
                'vendor': pmt.partner_id.name,
                'description': p.description or '',
                'amount': pmt.amount,
                # 'status': inv_state.get(p.move_id.state, ''),
                # 'reconcile_status': pay_state.get(p.move_id.payment_state, ''),
                'reconcile_status': recon_status,
                # 'cancel_payment': 'Voided' if pmt.cancel_reversal else '',
                'date_cancel': pmt.reverse_date if pmt.reverse_date else '',
                'date_cleared': date_cleared,
                'vendor_site': pmt.site_id.name or '',
                # 'payment_state': pay_state.get(p.invoice_payment_state, ''),
                'invoice_no': p.payment_reference,
                'bill_no': p.name,
                'amount_invoice': p.move_id.amount_total,
                'date_invoice': date_invoice,
                'date_gl': date_gl,
                'amount_payment': p.amount,
                'amount_payment_idr': sum(line.mapped('debit')),
            }
            result.append(data)

        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'AP Payment Recapitulation %s - %s' % (self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def _generate_header(self):
        """ function to generate headers """
        headers = [
            'Company', 'Bank Name', 'Bank Branch Name', 'Bank Account Name',
            'Bank Account Num', 'Check Date', 'Check Number', 'Voucher Num',
            'Payment Document Name', 'Currency', 'Rate', 'Vendor Name',
            'Description', 'Amount', 'Reconcile Status', 'Cancel Date',
            'Cleared Date', 'Vendor Site', 'Invoice Number', 'Bill Number',
            'Invoice Amount', 'Invoice Date', 'GL Date', 'Payment Amount',
            'Payment Amount IDR',
        ]
        return headers

    def get_xlsx(self, response, data=None):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('AP Payment Recapitulation')

        # styles
        # title: bold 12 center
        s_title = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 12, 'font_name': 'Arial',
        })

        # header_border: bold 10 border
        s_header_border = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })

        # right: 10 right
        s_right = wb.add_format({
            'align': 'right', 'font_size': 10, 'font_name': 'Arial',
        })

        # right_bold: bold 10 right
        s_right_bold_border = wb.add_format({
            'bold': 1, 'align': 'right', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })

        # normal: 10
        s_normal = wb.add_format({
            'font_name': 'Arial', 'font_size': 10, 'num_format': '#,###',
        })

        # normal_border: 10 border
        s_normal_border = wb.add_format({
            'font_name': 'Arial', 'font_size': 10, 'num_format': '#,###',
            'border': 1,
        })

        s_normal_date_border = wb.add_format({
            'font_name': 'Arial', 'font_size': 10, 'num_format': 'dd/mm/yy',
            'border': 1,
        })

        headers = self._generate_header()
        date_print = date.today().strftime('%d-%b-%Y').upper()
        date_from = self.date_from.strftime('%d-%b-%Y').upper()
        date_to = self.date_to.strftime('%d-%b-%Y').upper()

        row = col = 0

        ws.write(row, col, 'AP REKAP PAYMENT', s_title)

        # info left part A and B
        row += 2
        # TODO add me
        ws.write(row, col, 'Period', s_normal)
        ws.write(row + 1, col, 'Company', s_normal)
        ws.write(row + 2, col, 'Bank', s_normal)
        ws.write(row + 3, col, 'Branch', s_normal)
        ws.write(row + 4, col, 'Bank Account', s_normal)
        ws.write(row + 5, col, 'Payment Status', s_normal)
        ws.write(row + 6, col, 'Currency', s_normal)
        ws.write(row, col + 1, ': %s - %s' % (date_from, date_to), s_normal)
        ws.write(row + 1, col + 1, ': ', s_normal)
        ws.write(row + 2, col + 1, ': ', s_normal)
        ws.write(row + 3, col + 1, ': ', s_normal)
        ws.write(row + 4, col + 1, ': ', s_normal)
        ws.write(row + 5, col + 1, ': ', s_normal)
        ws.write(row + 6, col + 1, ': ', s_normal)

        # info right part L
        ws.write(row + 1, col + 11, 'Print Date: %s' % date_print, s_right)
        ws.write(row + 2, col + 11, 'User: %s' % self.env.user.name or '', s_right)
        ws.write(row + 3, col + 11, 'Page', s_right)

        # table headers
        row += 9
        for idx, header in enumerate(headers):
            ws.write(row, col + idx, header, s_header_border)

        # table contents
        row += 1
        for dt in data:
            for idx, (k, v) in enumerate(dt.items()):
                stl = s_normal_date_border if 'date' in k else s_normal_border
                ws.write(row, col + idx, v, stl)
            row += 1

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
