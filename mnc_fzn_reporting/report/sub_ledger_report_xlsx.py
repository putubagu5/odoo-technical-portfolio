from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class SubLedgerReportXlsx(models.AbstractModel):
    _name = 'report.mnc_fzn_reporting.sub_ledger_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, wizard):
        detail = []
        result = []
        move_line_obj = self.env['account.move.line']
        move_lines = move_line_obj.sudo().search([
            ('date', '>=', wizard.date_start),
            ('date', '<=', wizard.date_end),
            ('company_id', '=', self.env.user.company_id.id),
            ('account_id', 'in', [x.id for x in wizard.account_id]),
            ('move_id.state', '=', 'posted'),
        ])

        account_list = move_lines.mapped('account_id.id')
        for account in account_list:
            begin_balance = 0
            ending_balance = 0
            for rec in move_lines.filtered(lambda x: x.account_id.id == account):
                ending_balance += rec.debit - rec.credit
                detail.append({
                    'inv_line': rec,
                })
            for rec in move_lines.filtered(lambda x: x.account_id.id == account and x.date <= wizard.date_start):
                begin_balance += rec.debit - rec.credit
            if detail:
                result.append({
                    'account_id': self.env['account.account'].browse(account),
                    'detail': detail,
                    'begin_balance': begin_balance,
                    'ending_balance': ending_balance,
                    'company_id': wizard.company_id,
                })
        return {
            'result': result,
            'move_lines': move_lines
        }

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Sub Ledger Detail')
        sheet.hide_gridlines(2)

        # Style
        company_header_style = workbook.add_format({'bold': True, 'font_color': 'black'})
        company_header_style.set_font_size(13)
        company_header_style.set_align('center')

        subtitle_style = workbook.add_format({'bold': True, 'font_color': 'black'})
        subtitle_style.set_align('center')

        report_label_header_style = workbook.add_format({'bold': True, 'font_color': '#000080'})
        report_label_header_style.set_font_size(26)
        report_label_header_style.set_align('center')

        string = workbook.add_format({'bold': False, 'font_color': 'black'})
        string.set_border(1)
        string.set_align('left')
        string.set_align('vcenter')

        string_left = workbook.add_format({'bold': False, 'font_color': 'black'})
        string_left.set_align('left')
        string_left.set_align('vcenter')

        string_right = workbook.add_format({'bold': False, 'font_color': 'black'})
        string_right.set_border(1)
        string_right.set_align('right')
        string_right.set_align('vcenter')

        string_center = workbook.add_format({'bold': False, 'font_color': 'black'})
        string_center.set_align('center')
        string_center.set_align('vcenter')

        number = workbook.add_format({'bold': False, 'font_color': 'black'})
        number.set_num_format('#,##0.00;(#,##0.00)')
        number.set_align('vcenter')
        number.set_border(1)

        number_center = workbook.add_format({'bold': False, 'font_color': 'black', 'valign': 'middle'})
        number_center.set_num_format('#,##0.00;(#,##0.00)')
        number_center.set_border(1)
        number_center.set_align('center')
        number_center.set_align('vcenter')

        number_bold = workbook.add_format({'bold': True, 'font_color': '#000080'})
        number_bold.set_num_format('#,##0.00;(#,##0.00)')

        table_header_style = workbook.add_format({'bold': True, 'font_color': '#000000'})
        table_header_style.set_align('center')
        table_header_style.set_border(1)

        sheet.show_grid = 0
        sheet.panes_frozen = True
        sheet.remove_splits = True
        sheet.portrait = 0  # Landscape
        sheet.fit_width_to_pages = 1

        sheet.set_column('A:A', 50)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:F', 30)
        sheet.set_column('G:H', 25)
        sheet.set_column('I:I', 100)
        sheet.set_column('J:N', 40)
        sheet.set_column('O:O', 50)
        sheet.set_column('P:AA', 30)
        sheet.set_column('AB:AB', 100)
        sheet.set_column('AC:AC', 40)
        sheet.set_column('AD:AE', 30)

        row = 1
        sheet.merge_range('A1:AD1', wizard.company_id.name, company_header_style)
        sheet.merge_range('A2:AD2', 'SUB LEDGER DETAIL ', company_header_style)
        sheet.write(2, 0, 'Period', string_left)
        sheet.write(2, 1, ': ' + wizard.date_start.strftime('%d %B %Y'), string_left)
        sheet.write(2, 2, 'To', string_center)
        sheet.write(2, 3, ': ' + wizard.date_end.strftime('%d %B %Y'), string_left)
        sheet.write(3, 0, 'Company', string_left)
        sheet.write(3, 1, ': ' + wizard.company_id.name, string_left)
        sheet.write(4, 0, 'Cost Center', string_left)
        sheet.write(4, 1, ': ', string_left)
        # sheet.write(4, 1, ': ' + wizard.cost_center.code + wizard.cost_center.name, string_left)

        # sheet.write(5, 0, 'Area', string_left)
        # sheet.write(5, 1, ': ' + 'ALL Area', string_left)
        # sheet.write(6, 0, 'Future 1', string_left)
        # sheet.write(6, 1, ': ' + 'All Future 1', string_left)
        # sheet.write(7, 0, 'Future 2', string_left)
        # sheet.write(7, 1, ': ' + 'All Future 2', string_left)
        for res in self.get_data(wizard)['result']:
            # sheet.write(row, 3, 'Company', string_left)
            # sheet.write(row, 2, ': ' + res['company_id'].name, string_left)
            # sheet.write(row, 4, 'Cost Center', string_left)
            # sheet.write(row, 2, ': ' + res['cost_center'].name, string_left)
            # sheet.write(row, 5, 'Area', string_left)
            # sheet.write(row, 2, ': ', string_left)
            # sheet.write(row, 6, 'Future 1', string_left)
            # sheet.write(row, 2, ': ', string_left)
            # sheet.write(row, 7, 'Future 2', string_left)
            # sheet.write(row, 2, ': ', string_left)
            sheet.write(row, 8, 'Account', string_left)
            sheet.write(row, 2, ': ' + res['account_id'].code, string_left)
            row = 7

            # Table Header
            sheet.write(row, 0, 'COA', table_header_style)
            sheet.write(row, 1, 'Account', table_header_style)
            sheet.write(row, 2, 'Cost Center', table_header_style)
            sheet.write(row, 3, 'Area', table_header_style)
            sheet.write(row, 4, 'Journal Name', table_header_style)
            sheet.write(row, 5, 'Source', table_header_style)
            sheet.write(row, 6, 'Category', table_header_style)
            sheet.write(row, 7, 'Gl Date', table_header_style)
            sheet.write(row, 8, 'Descriptions', table_header_style)
            sheet.write(row, 9, 'Begining Balance', table_header_style)
            sheet.write(row, 10, 'Debit', table_header_style)
            sheet.write(row, 11, 'Credit', table_header_style)
            sheet.write(row, 12, 'Ending Balance', table_header_style)
            sheet.write(row, 13, 'Customer/Supplier', table_header_style)
            sheet.write(row, 14, 'Project Number', table_header_style)
            sheet.write(row, 15, 'PO Number', table_header_style)
            sheet.write(row, 16, 'Invoice Number', table_header_style)
            sheet.write(row, 17, 'Gl Date Invoice', table_header_style)
            sheet.write(row, 18, 'Type', table_header_style)
            sheet.write(row, 19, 'MO Number', table_header_style)
            sheet.write(row, 20, 'Voucher Number', table_header_style)
            sheet.write(row, 21, 'Gl Date Voucher', table_header_style)
            sheet.write(row, 22, 'Curr Code', table_header_style)
            sheet.write(row, 23, 'Curr Type', table_header_style)
            sheet.write(row, 24, 'Curr Rate', table_header_style)
            sheet.write(row, 25, 'Valas', table_header_style)
            sheet.write(row, 26, 'Batch', table_header_style)
            sheet.write(row, 27, 'Description Line Journal', table_header_style)
            sheet.write(row, 28, 'Faktur Pajak', table_header_style)
            sheet.write(row, 29, 'Date Faktur', table_header_style)
            row += 1

            for line in res['detail']:
                ending_balance = 0
                begin_balance = 0
                if line['inv_line'].account_id.id == res['account_id'].id:
                    sheet.write(row, 0, line['inv_line'].account_id.name or "", string)  # coa
                    sheet.write(row, 1, line['inv_line'].account_id.code or "", string)  # account
                    sheet.write(row, 2, line['inv_line'].analytic_account_id.code or "", string)  # cost center
                    sheet.write(row, 3, line['inv_line'].operating_unit_id.name or "", string)  # area
                    sheet.write(row, 4, line['inv_line'].journal_id.name or "", string)  # journal name
                    sheet.write(row, 5, line['inv_line'].journal_id.type or "", string)  # source
                    sheet.write(row, 6, line['inv_line'].journal_id.name or "", string)  # category
                    sheet.write(row, 7, line['inv_line'].date.strftime('%d-%b-%y') or "", string)  # gl date
                    sheet.write(row, 8, line['inv_line'].name or "", string)  # description
                    sheet.write(row, 9, "", number)  # begining balance
                    sheet.write(row, 10, line['inv_line'].debit, number)  # debit
                    sheet.write(row, 11, line['inv_line'].credit, number)  # credit
                    ending_balance = line['inv_line'].debit - line['inv_line'].credit
                    sheet.write(row, 12, ending_balance, number)  # ending balance
                    sheet.write(row, 13, line['inv_line'].partner_id.name or "", string)  # customer/supplier
                    sheet.write(row, 14, "", string)  # project number
                    sheet.write(row, 15, line['inv_line'].move_id.po_numbers or "", string)  # po number
                    sheet.write(row, 16, line['inv_line'].move_id.payment_reference or "", string)  # invoice number
                    sheet.write(row, 17, line['inv_line'].move_id.date.strftime('%d-%b-%y') or "",
                                string)  # gl date invoice
                    sheet.write(row, 18, line['inv_line'].move_id.bill_type or "", string)  # type
                    sheet.write(row, 19, "", string)  # mo number
                    sheet.write(row, 20, line['inv_line'].move_id.voucher_no or "", string)  # voucher number
                    sheet.write(row, 21, "", string)  # gl date voucher
                    sheet.write(row, 22, line['inv_line'].currency_id.name or "", string)  # curr code
                    sheet.write(row, 23, "", string)  # curr type
                    sheet.write(row, 24, line['inv_line'].currency_id.actual_rate or "", string)  # curr rate
                    sheet.write(row, 25, "", string)  # valas
                    sheet.write(row, 26, "", string)  # batch
                    sheet.write(row, 27, line['inv_line'].name or "", string)  # description line journal
                    sheet.write(row, 28, "", string)  # faktur pajak
                    sheet.write(row, 29, "", string)  # date faktur
                    row += 1
            row += 4