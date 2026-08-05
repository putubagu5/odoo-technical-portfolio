from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class UnappliedReceiptsReportXlsx(models.AbstractModel):
    _name = 'report.mnc_fzn_reporting.unapplied_receipt_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, wizard):
        detail = []
        result = []
        move_line_obj = self.env['account.move.line']
        move_lines = move_line_obj.sudo().search([
            ('date', '<=', wizard.date_end),
            ('company_id', '=', self.env.user.company_id.id),
            ('account_id', 'in', [x.id for x in wizard.account_id]),
            ('move_id.state', '=', 'posted'),
        ])

        account_list = move_lines.mapped('account_id.id')
        for account in account_list:
            ending_balance = 0
            sum_balance = 0
            sum_post = 0
            outstanding = 0
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
                    'sum_balance': sum_balance,
                    'sum_post': sum_post,
                    'outstanding': outstanding,
                })
        return {
            'result': result,
            'move_lines': move_lines
        }

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Outstanding Asset Clearing')
        sheet.hide_gridlines(2)

        # Style
        company_header_style = workbook.add_format({'bold': True, 'font_color': 'black'})
        company_header_style.set_font_size(13)
        company_header_style.set_align('left')

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

        string_right = workbook.add_format({'num_format': '#,##0'})
        string_right.set_border(1)
        string_right.set_align('right')

        string_center = workbook.add_format({'bold': True, 'font_color': 'black'})
        string_center.set_align('center')
        string_center.set_border(1)
        string_center.set_align('vcenter')

        string_number = workbook.add_format({'bold': False, 'font_color': 'black'})
        string_number.set_align('center')
        string_number.set_border(1)
        string_number.set_align('vcenter')

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

        sheet.set_column('A:D', 30)
        sheet.set_column('E:G', 25)
        sheet.set_column('H:I', 35)
        sheet.set_column('J:O', 25)

        row = 1
        sheet.merge_range(0, 0, 0, 12, 'AR Unapplied Receipt Report', company_header_style)
        sheet.write(1, 0, 'Period', string_left)
        sheet.write(1, 1, ': ' + wizard.date_start.strftime('%d %B %Y'), string_left)

        row = 3

        # header
        sheet.write(4, 0, 'Company', string_center)
        sheet.write(4, 1, 'Account', string_center)
        sheet.write(4, 2, 'Customer Name', string_center)
        sheet.write(4, 3, 'Customer Number', string_center)
        sheet.write(4, 4, 'Gl Date', string_center)
        sheet.write(4, 5, 'Batch Source Name', string_center)
        sheet.write(4, 6, 'Batch Name', string_center)
        sheet.write(4, 7, 'Receipt Method', string_center)
        sheet.write(4, 8, 'Receipt Number', string_center)
        sheet.write(4, 9, 'Receipt Date', string_center)
        sheet.write(4, 10, 'Unid Flag', string_center)
        sheet.write(4, 11, 'Status', string_center)
        sheet.write(4, 12, 'On Account Amt', string_center)
        sheet.write(4, 13, 'Unapplied Amt', string_center)
        sheet.write(4, 14, 'Claim Amt', string_center)
        row += 2

        sheet.write(row, 0, '31101', string)  # company
        sheet.write(row, 1, '1151501', string)  # account
        sheet.write(row, 2, 'ACTIVATE MEDIA NUSANTARA, PT', string)  # customer_name
        sheet.write(row, 3, '5000977', string)  # customer_number
        sheet.write(row, 4, '25-Mar-14', string)  # gl_date
        sheet.write(row, 5, '', string)  # batch_source_name
        sheet.write(row, 6, '', string)  # batch_name
        sheet.write(row, 7, 'RCTI BC - Payment - GL', string)  # receipt_method
        sheet.write(row, 8, 'ORS32613', string)  # receipt_number
        sheet.write(row, 9, '07-Feb-10', string)  # receipt_date
        sheet.write(row, 10, '', string)  # unid_flag
        sheet.write(row, 11, 'CLEARED', string)  # status
        sheet.write(row, 12, '', string)  # on_account_amt
        sheet.write(row, 13, '664.320', string)  # unapplied_amt
        sheet.write(row, 14, '', string)  # claim_amt
        row += 1
        # row += 2
