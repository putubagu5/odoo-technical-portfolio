from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class TrialBalanceReportXlsx(models.AbstractModel):
    _name = 'report.mnc_gln_reporting.purchase_requisition_list_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, wizard):

        data = []
        detail = []
        pr_obj = self.env['purchase.request'].sudo()
        pr_ids = pr_obj.search([
            ('date_start', '>=', wizard.date_start),
            ('date_start', '<=', wizard.date_end),
            ('company_id', '=', self.env.user.company_id.id),
        ])
        user_list = pr_ids.mapped('requested_by.id')
        print('User LIIIIST', user_list)
        total_amount = 0
        subtotal = 0
        amount_pr = 0
        for user in user_list:
            for pr in pr_ids.filtered(lambda x: x.requested_by.id == user):
                amount_pr = pr.estimated_cost
                detail.append({
                    'amount_pr': float(amount_pr),
                    'pr': pr,
                })
            data.append({
                'requested_by': self.env['res.users'].browse(user),
                'requisition_ids': detail,
            })
        return data

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Purchase Requisition List')
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

        string_right = workbook.add_format({'num_format': '#,##0'})
        string_right.set_border(1)
        string_right.set_align('right')

        string_center = workbook.add_format({'bold': False, 'font_color': 'black'})
        string_center.set_align('center')
        string_center.set_border(1)
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
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 100)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:F', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:H', 30)
        sheet.set_column('I:I', 150)
        sheet.set_column('J:V', 20)

        row = 1
        sheet.merge_range(0, 0, 0, 16, 'Purchase Requisition List Report', company_header_style)
        sheet.write(1, 0, 'Start Period', string_left)
        sheet.write(1, 1, ': ' + wizard.date_start.strftime('%d %B %Y'), string_left)
        sheet.write(2, 0, 'End Period', string_left)
        sheet.write(2, 1, ': ' + wizard.date_end.strftime('%d %B %Y'), string_left)
        purchase_requisitions = self.get_data(wizard)
        row = 4
        for user in purchase_requisitions:
            sheet.write(row, 0, 'Preparer Name', string_left)
            sheet.write(row, 1, ': ' + user['requested_by'].name, string_left)
            row += 1
            # header
            sheet.write(row, 0, 'Number', string)
            sheet.write(row, 1, 'Creation Date', string)
            sheet.write(row, 2, 'Description', string)
            sheet.write(row, 3, 'Status PR', string)
            sheet.write(row, 4, 'Total Amount', string)
            sheet.write(row, 5, 'Line Num', string)
            sheet.write(row, 6, 'Item Code', string)
            sheet.write(row, 7, 'Item Name', string)
            sheet.write(row, 8, 'Item Description', string)
            sheet.write(row, 9, 'Cost Center', string)
            sheet.write(row, 10, 'Quantity', string)
            sheet.write(row, 11, 'Price', string)
            sheet.write(row, 12, 'PR Amount', string)
            sheet.write(row, 13, 'Number', string)
            sheet.write(row, 14, 'Creation Date', string)
            sheet.write(row, 15, 'Vendor Name', string)
            sheet.write(row, 16, 'Vendor Site', string)
            sheet.write(row, 17, 'Currency', string)
            sheet.write(row, 18, 'Amount', string)
            sheet.write(row, 19, 'Matched Amount', string)
            sheet.write(row, 20, 'Buyer', string)
            sheet.write(row, 21, 'Closure Status', string)
            row += 1
            col = 4
            no = 1
            for pr in user['requisition_ids']:
                if pr['pr'].requested_by.id == user['requested_by'].id:
                    line_count = len(pr['pr'].line_ids)
                    if line_count == 1:
                        sheet.write(row, 0, pr['pr'].name or '', string)
                        sheet.write(row, 1, pr['pr'].date_start.strftime('%d-%b-%y') or '', string)
                        sheet.write(row, 2, pr['pr'].description or '', string)
                        sheet.write(row, 3, dict(pr['pr']._fields['state'].selection).get(pr['pr'].state).upper(),
                                    string)
                        sheet.write(row, 4, pr['amount_pr'], string_right)
                    else:
                        sheet.merge_range((row + line_count) - 1, 0, row, 0, pr['pr'].name or '', string)
                        sheet.merge_range((row + line_count) - 1, 1, row, 1,
                                          pr['pr'].create_date.strftime('%d-%b-%y') or '', string)
                        sheet.merge_range((row + line_count) - 1, 2, row, 2, pr['pr'].origin or '' or '', string)
                        sheet.merge_range((row + line_count) - 1, 3, row, 3,
                                          dict(pr['pr']._fields['state'].selection).get(pr['pr'].state).upper() or '',
                                          string)
                        sheet.merge_range((row + line_count) - 1, 4, row, 4, pr['amount_pr'] or '', string)

                    for line in pr['pr'].line_ids:
                        sheet.write(row, 5, no, string_center)
                        sheet.write(row, 6, line.product_id.default_code or '', string)
                        sheet.write(row, 7, line.product_id.name or '', string)
                        sheet.write(row, 8, line.name or '', string)
                        sheet.write(row, 9, line.analytic_account_id.name or '', string)
                        sheet.write(row, 10, line.product_qty or 0, string_center)
                        sheet.write(row, 11, line.original_price or 0, string_right)
                        sheet.write(row, 12, line.estimated_cost or 0, string_right)
                        sheet.write(row, 13, '', string)
                        sheet.write(row, 14, '', string)
                        sheet.write(row, 15, '', string)
                        sheet.write(row, 16, '', string)
                        sheet.write(row, 17, pr['pr'].currency_id.name or '', string)
                        sheet.write(row, 18, line.estimated_cost or 0, string_right)
                        sheet.write(row, 19, '', string)
                        sheet.write(row, 20, '', string)
                        sheet.write(row, 21, '', string)
                        row += 1
                        no += 1
            row += 1

        # for res in self.get_data(wizard)['result']:
        #     sheet.write(row, 0, 'Account',string_left)
        #     sheet.write(row, 1, res['account_id'].code,string_left)
        #     row+=1
        #     sheet.write(row, 0, 'Begin Balance',string_left)
        #     sheet.write(row, 1, res['begin_balance'],string_left)
        #     row+=1
        #     sheet.write(row, 0, 'Ending Balance',string_left)
        #     sheet.write(row, 1, res['ending_balance'],string_left)
        #     row+=2

        #     # Table Header
        #     sheet.write(row, 0, 'Effective Date',table_header_style)
        #     sheet.write(row, 1, 'Source',table_header_style)
        #     sheet.write(row, 2, 'Category',table_header_style)
        #     sheet.write(row, 3, 'Invoice Type',table_header_style)
        #     sheet.write(row, 5, 'Account',table_header_style)
        #     sheet.write(row, 5, 'Header',table_header_style) #belum
        #     sheet.write(row, 6, 'Customer/Supplier',table_header_style)
        #     sheet.write(row, 7, 'Name',table_header_style)
        #     sheet.write(row, 8, 'Descriptions',table_header_style)
        #     sheet.write(row, 9, 'Faktur Pajak',table_header_style)
        #     sheet.write(row, 10, 'PR Number',table_header_style)
        #     sheet.write(row, 11, 'PO Number',table_header_style)
        #     sheet.write(row, 12, 'Invoice Number',table_header_style)
        #     sheet.write(row, 13, 'Voucher Number',table_header_style)
        #     sheet.write(row, 15, 'JV Number',table_header_style)
        #     sheet.write(row, 15, 'Debits',table_header_style)
        #     sheet.write(row, 16, 'Credits',table_header_style)
        #     sheet.write(row, 17, 'Ending Balance',table_header_style)
        #     row+=1
        #     for line in res['detail']:
        #         ending_balance = 0
        #         begin_balance = 0
        #         if line['inv_line'].account_id.id == res['account_id'].id:
        #             sheet.write(row, 0, line['inv_line'].date.strftime('%d-%m-%Y'),string)
        #             sheet.write(row, 1, line['inv_line'].move_id.journal_id.type or "",string)
        #             sheet.write(row, 2, line['inv_line'].move_id.journal_id.type or "",string)
        #             sheet.write(row, 3, line['inv_line'].move_id.bill_type,string)
        #             sheet.write(row, 4, self.env.user.company_id.company_code + '.'+ line['inv_line'].account_id.code + '.' + line['inv_line'].analytic_account_id.name  + '.000' if self.env.user.company_id.company_code and line['inv_line'].account_id.code and line['inv_line'].analytic_account_id.name else ' ' ,string)
        #             sheet.write(row, 5, "",string)
        #             sheet.write(row, 6, line['inv_line'].partner_id.name or "",string)
        #             sheet.write(row, 7, line['inv_line'].partner_id.name or "",string)
        #             sheet.write(row, 8, line['inv_line'].name,string)
        #             sheet.write(row, 9, line['inv_line'].tax_invoice_id.name or "",string)
        #             sheet.write(row, 10, "",string)
        #             sheet.write(row, 11, line['inv_line'].purchase_order_id.name or "",string)
        #             sheet.write(row, 12, line['inv_line'].move_id.name or "",string)
        #             sheet.write(row, 13, line['inv_line'].move_id.voucher_no or "",string)
        #             sheet.write(row, 14, "",string)
        #             sheet.write(row, 15, line['inv_line'].debit,table_header_style)
        #             sheet.write(row, 16, line['inv_line'].credit,table_header_style)
        #             ending_balance = line['inv_line'].debit - line['inv_line'].credit
        #             sheet.write(row, 17, ending_balance,table_header_style)
        #             row+=1
        #     row+=2
