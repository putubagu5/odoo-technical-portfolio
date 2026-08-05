from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class TrialBalanceReportXlsx(models.AbstractModel):
    _name = 'report.mnc_gln_reporting.trial_balance_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, wizard):
        detail = []
        result = []
        move_line_obj = self.env['account.move.line']
        move_lines = move_line_obj.sudo().search([
            ('date', '<=', wizard.date_end),
            ('company_id', '=', self.env.user.company_id.id),
            ('account_id', 'in', [x.id for x in wizard.account_ids]),
            ('move_id.state', '=', 'posted'),
        ])

        account_list = move_lines.mapped('account_id.id')
        for account in account_list:
            ending_balance = 0
            begin_balance = 0
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
                    'ending_balance': ending_balance,
                    'begin_balance': begin_balance,
                })
        return {
            'result': result,
            'move_lines': move_lines
        }

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Overtime Summary Report')
        sheet.hide_gridlines(2)

        ##Style
        company_header_style = workbook.add_format({'bold': True, 'font_color': 'black'})
        company_header_style.set_font_size(16)
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

        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:F', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:H', 25)
        sheet.set_column('I:I', 100)
        sheet.set_column('J:S', 20)

        row = 1
        sheet.write(0, 0, 'Period', string_left)
        sheet.write(0, 1, ': ' + wizard.date_start.strftime('%d %B %Y'), string_left)
        sheet.write(0, 2, 'To', string_center)
        sheet.write(0, 3, wizard.date_end.strftime('%d %B %Y'), string_left)
        for res in self.get_data(wizard)['result']:
            sheet.write(row, 0, 'Account', string_left)
            sheet.write(row, 1, res['account_id'].code, string_left)
            row += 1
            sheet.write(row, 0, 'Begin Balance', string_left)
            sheet.write(row, 1, res['begin_balance'], string_left)
            row += 1
            sheet.write(row, 0, 'Ending Balance', string_left)
            sheet.write(row, 1, res['ending_balance'], string_left)
            row += 2

            # Table Header
            sheet.write(row, 0, 'Effective Date', table_header_style)
            sheet.write(row, 1, 'Source', table_header_style)
            sheet.write(row, 2, 'Category', table_header_style)
            sheet.write(row, 3, 'Invoice Type', table_header_style)
            sheet.write(row, 4, 'Account', table_header_style)
            sheet.write(row, 5, 'Header', table_header_style)  # belum
            sheet.write(row, 6, 'Customer/Supplier', table_header_style)
            sheet.write(row, 7, 'Name', table_header_style)
            sheet.write(row, 8, 'Descriptions', table_header_style)
            sheet.write(row, 9, 'Faktur Pajak', table_header_style)
            sheet.write(row, 10, 'PR Number', table_header_style)
            sheet.write(row, 11, 'PO Number', table_header_style)
            sheet.write(row, 12, 'Invoice Number', table_header_style)
            sheet.write(row, 13, 'Voucher Number', table_header_style)
            sheet.write(row, 14, 'JV Number', table_header_style)
            sheet.write(row, 15, 'Debits', table_header_style)
            sheet.write(row, 16, 'Credits', table_header_style)
            sheet.write(row, 17, 'Ending Balance', table_header_style)
            row += 1
            for line in res['detail']:
                ending_balance = 0
                begin_balance = 0
                if line['inv_line'].account_id.id == res['account_id'].id:
                    sheet.write(row, 0, line['inv_line'].date.strftime('%d-%m-%Y'), string)
                    sheet.write(row, 1, line['inv_line'].move_id.journal_id.type or "", string)
                    sheet.write(row, 2, line['inv_line'].move_id.journal_id.type or "", string)
                    sheet.write(row, 3, line['inv_line'].move_id.bill_type, string)
                    sheet.write(row, 4,
                                self.env.user.company_id.company_code + '.' + line['inv_line'].account_id.code + '.' +
                                line[
                                    'inv_line'].analytic_account_id.name + '.000' if self.env.user.company_id.company_code and
                                                                                     line[
                                                                                         'inv_line'].account_id.code and
                                                                                     line[
                                                                                         'inv_line'].analytic_account_id.name else ' ',
                                string)
                    sheet.write(row, 5, "", string)
                    sheet.write(row, 6, line['inv_line'].partner_id.name or "", string)
                    sheet.write(row, 7, line['inv_line'].partner_id.name or "", string)
                    sheet.write(row, 8, line['inv_line'].name, string)
                    sheet.write(row, 9, line['inv_line'].tax_invoice_id.name or "", string)
                    sheet.write(row, 10, "", string)
                    sheet.write(row, 11, line['inv_line'].purchase_order_id.name or "", string)
                    sheet.write(row, 12, line['inv_line'].move_id.name or "", string)
                    sheet.write(row, 13, line['inv_line'].move_id.voucher_no or "", string)
                    sheet.write(row, 14, "", string)
                    sheet.write(row, 15, line['inv_line'].debit, table_header_style)
                    sheet.write(row, 16, line['inv_line'].credit, table_header_style)
                    ending_balance = line['inv_line'].debit - line['inv_line'].credit
                    sheet.write(row, 17, ending_balance, table_header_style)
                    row += 1
            row += 2
