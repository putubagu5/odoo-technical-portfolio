from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class TrialBalanceReportXlsx(models.AbstractModel):
    _name = 'report.mnc_reporting.purchase_requisition_list_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, wizard):

        data = []
        detail = []
        pr_obj = self.env['purchase.request'].sudo()
        po_obj = self.env['purchase.order'].sudo()
        pr_ids = pr_obj.search([
            ('date_start', '>=', wizard.date_start),
            ('date_start', '<=', wizard.date_end),
            ('company_id', '=', wizard.company_id.id),
            ('requested_by', '=', wizard.users_ids.ids),
            ('line_ids.analytic_account_id', 'in', [x.id for x in wizard.analytic_account_ids]),
        ])
        print("DATA PR ----->>>>>>", pr_ids)
        user_list = pr_ids.mapped('requested_by.id')
        print('User LIIIIST', user_list)
        total_amount = 0
        subtotal = 0
        amount_pr = 0
        for user in user_list:
            for pr in pr_ids.filtered(lambda x: x.requested_by.id == user):
                po_ids = po_obj.search([('origin', 'in', pr.mapped('name'))])
                po_lines = po_ids.mapped('order_line')
                amount_pr = pr.estimated_cost
                detail.append({
                    'amount_pr': float(amount_pr),
                    'pr': pr,
                    'purchase_orders': po_ids,
                    'purchase_order_lines': po_lines,
                })
            data.append({
                'requested_by': self.env['res.users'].browse(user),
                'requisition_ids': detail,
            })
        return data

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Purchase Requisition List')
        sheet.hide_gridlines(2)

        # Style
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
        string_right.set_align('vcenter')

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
        sheet.set_column('C:C', 80)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:F', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 50)
        sheet.set_column('I:I', 100)
        sheet.set_column('J:J', 35)
        sheet.set_column('K:K', 10)
        sheet.set_column('L:O', 20)
        sheet.set_column('P:P', 50)
        sheet.set_column('Q:Q', 30)
        sheet.set_column('R:V', 20)

        row = 1
        sheet.merge_range(0, 0, 0, 21, 'Purchase Requisition List Report', company_header_style)
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
            sheet.write(row, 0, 'PR Number', string_center)
            sheet.write(row, 1, 'Creation Date', string_center)
            sheet.write(row, 2, 'Description', string_center)
            sheet.write(row, 3, 'Status PR', string_center)
            sheet.write(row, 4, 'Total Amount', string_center)
            sheet.write(row, 5, 'Line Number', string_center)
            sheet.write(row, 6, 'Item Code', string_center)
            sheet.write(row, 7, 'Item Name', string_center)
            sheet.write(row, 8, 'Item Description', string_center)
            sheet.write(row, 9, 'Cost Center', string_center)
            sheet.write(row, 10, 'Quantity', string_center)
            sheet.write(row, 11, 'Price', string_center)
            sheet.write(row, 12, 'PR Amount', string_center)
            sheet.write(row, 13, 'PO Number', string_center)
            sheet.write(row, 14, 'Creation Date', string_center)
            sheet.write(row, 15, 'Vendor Name', string_center)
            sheet.write(row, 16, 'Vendor Site', string_center)
            sheet.write(row, 17, 'Currency', string_center)
            sheet.write(row, 18, 'Amount', string_center)
            sheet.write(row, 19, 'Matched Amount', string_center)
            sheet.write(row, 20, 'Buyer', string_center)
            sheet.write(row, 21, 'Closure Status', string_center)
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
                        sheet.merge_range((row + line_count) - 1, 2, row, 2, pr['pr'].description or '', string)
                        sheet.merge_range((row + line_count) - 1, 3, row, 3,
                                          dict(pr['pr']._fields['state'].selection).get(pr['pr'].state).upper() or '',
                                          string)
                        sheet.merge_range((row + line_count) - 1, 4, row, 4, pr['amount_pr'] or '', string_right)

                    for line in pr['pr'].line_ids:
                        sheet.write(row, 5, line.line_number, string_center)
                        sheet.write(row, 6, line.product_id.default_code or '', string)
                        sheet.write(row, 7, line.product_id.name or '', string)
                        sheet.write(row, 8, line.name or '', string)
                        sheet.write(row, 9, line.analytic_account_id.name or '', string)
                        sheet.write(row, 10, line.product_qty or 0, string_center)
                        sheet.write(row, 11, line.original_price or 0, string_right)
                        sheet.write(row, 12, line.estimated_cost or 0, string_right)
                        # sheet.write(row, 13, pr['pr'].po_numbers or '', string)  # po_numbers
                        sheet.write(row, 17, pr['pr'].currency_id.name or '', string)
                        sheet.write(row, 18, line.estimated_cost or 0, string_right)
                        for po in pr['purchase_orders']:
                            sheet.write(row, 13, po.name or '', string)  # po_numbers
                            sheet.write(row, 14, po.create_date.strftime('%d-%b-%y') or '', string)  # creation_date
                            sheet.write(row, 15, po.partner_id.name or '', string)  # vendor_name
                            sheet.write(row, 16, po.sites_id.name or '', string)  # vendor_site
                            for po_line in po.order_line:
                                sheet.write(row, 19, po_line.price_subtotal or '', string_right)  # matched_amount
                            sheet.write(row, 20, po.request_user_id.name or '', string)
                            sheet.write(row, 21, dict(po._fields['state'].selection).get(po.state).upper(),
                                        string)  # closure_status

                        row += 1
                        no += 1
            row += 1
