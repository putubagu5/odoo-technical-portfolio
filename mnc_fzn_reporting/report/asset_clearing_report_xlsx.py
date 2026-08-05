from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class PurchaseOrderListReportXlsx(models.AbstractModel):
    _name = 'report.mnc_fzn_reporting.asset_clearing_report_xlsx'
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

        sheet.set_column('A:B', 20)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 80)
        sheet.set_column('F:X', 30)

        row = 1
        sheet.merge_range(0, 0, 0, 12, 'RINCIAN FIXED ASSET CLEARING', company_header_style)
        sheet.write(1, 0, 'Detail list saldo', string_left)
        sheet.write(1, 1, ': ' + wizard.date_start.strftime('%d %B %Y'), string_left)
        sheet.write(1, 2, 's/d' + ': ' + wizard.date_end.strftime('%d %B %Y'), string_left)
        # sheet.write(2, 1, ': ' + wizard.date_end.strftime('%d %B %Y'), string_left)
        for res in self.get_data(wizard)['result']:
            sheet.write(2, 0, 'Account', string_left)
            sheet.write(2, 1, ': ' + res['account_id'].code, string_left)
            # purchase_order = self.get_data(wizard)
            row = 6

            # header
            sheet.write(5, 0, 'PO Number', string_center)
            sheet.write(5, 1, 'Company', string_center)
            sheet.write(5, 2, 'Supplier Name', string_center)
            sheet.write(5, 3, 'Line PO', string_center)
            sheet.write(5, 4, 'Description', string_center)
            sheet.write(5, 5, 'Amount PO', string_center)
            sheet.write(5, 6, 'Amount PO IDR', string_center)
            sheet.write(5, 7, 'No RR', string_center)
            sheet.write(5, 8, 'Line RCV', string_center)
            sheet.write(5, 9, 'Tgl RR', string_center)
            sheet.write(5, 10, 'Create Accounting RR', string_center)
            sheet.write(5, 11, 'AP Matching Date', string_center)
            sheet.write(5, 12, 'Invoice Number', string_center)
            sheet.write(5, 13, 'Create Accounting AP', string_center)
            sheet.write(5, 14, 'Asset Number', string_center)
            sheet.write(5, 15, 'Create MA', string_center)
            sheet.write(5, 16, 'Amount Mass Addition', string_center)
            sheet.write(5, 17, 'Post MA Create', string_center)
            sheet.write(5, 18, 'Create Accounting FA', string_center)
            sheet.write(5, 19, 'Amount Post MA', string_center)
            sheet.write(5, 20, 'Sum PO (IDR)', string_center)
            sheet.write(5, 21, 'Adjustment', string_center)
            sheet.write(5, 22, 'Sum Post MA', string_center)
            sheet.write(5, 23, 'Outstanding', string_center)
            # no = 1

            for line in res['detail']:
                ending_balance = 0
                begin_balance = 0
                if line['inv_line'].account_id.id == res['account_id'].id:
                    sheet.write(row, 0, line['inv_line'].move_id.purchase_id.name or '', string)  # po_number
                    sheet.write(row, 1, '1239001', string)  # company_code
                    sheet.write(row, 2, line['inv_line'].partner_id.name or '', string)  # supplier_name
                    sheet.write(row, 3, line['inv_line'].purchase_line_number or '', string)  # line_po
                    sheet.write(row, 4, line['inv_line'].name or '', string)  # description
                    sheet.write(row, 5, line['inv_line'].move_id.purchase_id.order_line.price_unit or '',
                                string)  # amount_po
                    sheet.write(row, 6, line['inv_line'].move_id.purchase_id.order_line.price_unit or '',
                                string)  # amount_po_idr
                    sheet.write(row, 7, line['inv_line'].move_id.purchase_id.rr_numbers or '', string)  # no_rr
                    sheet.write(row, 8, '', string)  # line_rcv
                    sheet.write(row, 9, '', string)  # tgl_rr
                    sheet.write(row, 10, '', string)  # create_accounting_rr
                    sheet.write(row, 11, line['inv_line'].move_id.invoice_date or '', string)  # ap_matching_date
                    sheet.write(row, 12, line['inv_line'].move_id.payment_reference or '', string)  # invoice_number
                    sheet.write(row, 13, line['inv_line'].move_id.date.strftime('%d-%b-%y') or '',
                                string)  # create_accounting_ap
                    sheet.write(row, 14, '', string)  # asset_number
                    sheet.write(row, 15, '', string)  # create_ma
                    sheet.write(row, 16, '', string)  # amount_mass_addition
                    sheet.write(row, 17, '', string)  # post_ma_create
                    sheet.write(row, 18, '', string)  # create_accounting_fa
                    sheet.write(row, 19, '', string)  # amount_post_ma
                    sheet.write(row, 20, line['inv_line'].move_id.purchase_id.order_line.price_unit or '',
                                string)  # sum_po
                    sheet.write(row, 21, '', string)  # addjusment
                    sheet.write(row, 22, '', string)  # sum_post_ma
                    sheet.write(row, 23, '', string)  # outstanding
                    row += 1
            row += 2
