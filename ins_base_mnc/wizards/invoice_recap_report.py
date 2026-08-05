from datetime import date
from io import BytesIO
import xlsxwriter
from odoo import api, fields, models, SUPERUSER_ID


class InvoiceRecapReport(models.TransientModel):
    _name = 'wizard.invoice.recap.report'
    _description = 'Invoice Recap Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    all_companies = fields.Boolean('All Companies?', default=False)
    company_ids = fields.Many2many('res.company', string='Companies')
    # all_accounts = fields.Boolean('All Accounts?', default=False)
    # account_ids = fields.Many2many('account.account', string='Accounts')

    @api.onchange('all_companies')
    def _onchange_all_companies(self):
        """ onchange function to assign all companies """
        if self.all_companies:
            cmp_ids, _ = self._get_companies()
            self.company_ids = [(6, 0, cmp_ids)]
        else:
            self.company_ids = [(3, x.id) for x in self.company_ids]

    # @api.onchange('all_accounts')
    # def _onchange_all_accounts(self):
    #     """ onchange function to assign all accounts """
    #     if self.all_accounts:
    #         acc_ids, _ = self._get_accounts()
    #         self.account_ids = [(6, 0, acc_ids)]

    def _get_companies(self):
        """ function to get the company ids in list and string """
        str_company_ids = ''
        domain = []
        if not self.all_companies:
            domain = [('id', 'in', self.company_ids.ids)]

        company = self.env['res.company'].with_user(SUPERUSER_ID).search(domain)
        cmp_ids = company.ids
        if company:
            str_company_ids = '(%s)' % ','.join(map(lambda x: str(x), company.ids))
        return cmp_ids, str_company_ids

    # def _get_accounts(self):
    #     """ function to get the account ids in list and string """
    #     str_account_ids = ''
    #     cmp_ids, _ = self._get_companies()
    #     domain = [('company_id', 'in', cmp_ids)]
    #     if not self.all_accounts:
    #         domain += [('id', 'in', self.account_ids.ids)]

    #     account = self.env['account.account'].with_user(SUPERUSER_ID).search(domain)
    #     acc_ids = account.ids
    #     if account:
    #         str_account_ids = '(%s)' % ','.join(map(lambda x: str(x), account.ids))
    #     return acc_ids, str_account_ids

    def _prepare_report_data(self):
        """ function to prepare report data containing list of dict """
        result = []

        move = self.env['account.move']
        inv_state = dict(move._fields['state']._description_selection(self.env))
        pmt_state = dict(move._fields['payment_state']._description_selection(self.env))

        # take debit, remove account filters and add description in invoice
        domain = [
            ('move_id.invoice_date', '>=', self.date_from),
            ('move_id.invoice_date', '<=', self.date_to),
            ('move_id.move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt')),
            ('move_id.company_id', 'in', self.company_ids.ids),
            ('exclude_from_invoice_tab', '=', False),
        ]
        lines = self.env['account.move.line'].search(domain)

        for line in lines:
            inv = line.move_id
            data = {
                'company': inv.company_id.name,
                'customer_code': inv.partner_id.partner_no or '',
                'customer_name': inv.partner_id.name,
                'date_gl': inv.date.strftime('%d/%m/%Y') if inv.date else '',
                'date_invoice': inv.invoice_date.strftime('%d/%m/%Y') if inv.invoice_date else '',
                'invoice_no': inv.name,
                'invoice_type': inv.transaction_type_id.name or '',
                'date_due': inv.invoice_date_due.strftime('%d/%m/%Y') if inv.invoice_date_due else '',
                'print': '-',
                'currency': inv.currency_id.name,
                'dpp': line.price_subtotal,
                'ppn': line.price_total - line.price_subtotal,
                'amount': line.price_total,
                'faktur': inv.tax_invoice_id.name or '',
                'npwp': '-',
                'station': '-',
                'period': '-',
                'advertiser': '-',
                'product': line.product_id.name or line.name,
                'mo': '-',
                'description': inv.ref or '',
                'account': line.account_id.name or '',
                'cost_center': line.analytic_account_id.name or '',
                'ae': '-',
                'status': inv_state.get(inv.state),
                'payment_status': pmt_state.get(inv.payment_state),
            }
            result.append(data)

        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'Rekapitulasi Invoice %s - %s' % (self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def _generate_header(self):
        """ function to generate headers """
        headers = [
            'Company', 'Customer Code', 'Customer Name', 'GL Date',
            'Date Invoice', 'No. Invoice', 'Type Invoice', 'Tgl Jatuh Tempo',
            'Cetak', 'Curr', 'DPP AR', 'PPN AR', 'Amount AR',
            'No. Faktur Pajak', 'NPWP', 'Stasiun Tayang', 'Periode Tayang',
            'Advertiser', 'Product/Brand', 'No. MO', 'Description', 'COA AR',
            'Cost Center', 'AE', 'Status', 'Payment Status',
        ]
        return headers

    def get_xlsx(self, response, data=None):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('Rekapitulasi Invoice')

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

        headers = self._generate_header()
        date_print = date.today().strftime('%d-%b-%Y').upper()
        date_from = self.date_from.strftime('%d-%b-%Y').upper()
        date_to = self.date_to.strftime('%d-%b-%Y').upper()
        company_names = [x.name for x in self.company_ids]
        company_names = ', '.join(company_names)
        # account_names = [x.name for x in self.account_ids]
        # account_names = ', '.join(account_names)

        row = col = 0

        # title, merge to len(headers)
        ws.merge_range(row, col, row, col + len(headers),
                       'REKAPITULASI INVOICE', s_title)

        # info: left part A and B
        row += 1
        ws.write(row, col, 'From Date', s_normal)
        ws.write(row + 1, col, 'To Date', s_normal)
        ws.write(row + 2, col, 'Company', s_normal)
        # ws.write(row + 3, col, 'COA', s_normal)
        ws.write(row, col + 1, date_from, s_normal)
        ws.write(row + 1, col + 1, date_to, s_normal)
        ws.write(row + 2, col + 1, company_names, s_normal)
        # ws.write(row + 3, col + 1, account_names, s_normal)

        # info: right part M to O, merge, right justify
        ws.merge_range(row + 1, col + 12, row + 1, col + 14,
                       'Print Date: %s' % date_print, s_right)
        ws.merge_range(row + 2, col + 12, row + 2, col + 14,
                       'User: %s' % self.env.user.name or '', s_right)
        ws.merge_range(row + 3, col + 12, row + 3, col + 14,
                       'Page', s_right)

        # table headers
        row += 4
        for idx, header in enumerate(headers):
            ws.write(row, col + idx, header, s_header_border)

        # table contents
        row += 1
        start_row = row + 1  # real row
        for dt in data:
            for idx, value in enumerate(dt.values()):
                ws.write(row, col + idx, value, s_normal_border)
            row += 1

        end_row = row  # real row
        # total columns in J, K, L only
        # merge A to I and M to X
        ws.merge_range('A%s:I%s' % (row + 1, row + 1), 'TOTAL:', s_right_bold_border)
        ws.write('J%s' % (row + 1), '=SUM(J%s:J%s)' % (start_row, end_row), s_normal_border)
        ws.write('K%s' % (row + 1), '=SUM(K%s:K%s)' % (start_row, end_row), s_normal_border)
        ws.write('L%s' % (row + 1), '=SUM(L%s:L%s)' % (start_row, end_row), s_normal_border)
        ws.merge_range('M%s:X%s' % (row + 1, row + 1), '', s_normal_border)

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
