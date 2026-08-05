from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class PurchaseOrderListReportXlsx(models.AbstractModel):
    _name = 'report.mnc_fzn_reporting.purchase_order_list_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, wizard):
        data = []
        detail = []
        domain = [('date_order', '>=', wizard.date_start),
                  ('date_order', '<=', wizard.date_end),
                  ('company_id', '=', self.env.user.company_id.id)]

        if wizard.partner_id and wizard.buyer_id:
            domain += [('partner_id', '=', wizard.partner_id.ids)]

        if wizard.buyer_id:
            domain = [('buyer_id', '=', wizard.buyer_id.ids),
                      ('state', '=', 'purchase')]

        po_obj = self.env['purchase.order'].sudo()
        po_ids = po_obj.search(domain)

        pr_obj = self.env['purchase.request']
        pr_ids = pr_obj.search([('po_numbers', '=', 'name')], limit=1)

        for rec in pr_ids:
            detail = rec.date_start

        return po_ids

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Purchase Order List')
        sheet.hide_gridlines(2)

        # Style
        company_header_style = workbook.add_format({'bold': True, 'font_color': 'black'})
        company_header_style.set_font_size(16)
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

        sheet.set_column('A:C', 20)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:H', 20)
        sheet.set_column('I:I', 30)
        sheet.set_column('J:J', 25)
        sheet.set_column('K:N', 55)
        sheet.set_column('M:M', 100)

        row = 1
        sheet.merge_range(0, 0, 0, 12, 'MNC PO - List Purchase Order', company_header_style)
        sheet.write(1, 0, 'Start Period', string_left)
        sheet.write(1, 1, ': ' + wizard.date_start.strftime('%d %B %Y'), string_left)
        sheet.write(1, 2, 'End Period', string_left)
        sheet.write(1, 3, ': ' + wizard.date_end.strftime('%d %B %Y'), string_left)
        sheet.write(2, 0, 'Supplier', string_left)
        sheet.write(2, 1, ': ' + wizard.get_partner_name() if wizard.partner_id else ": ALL SUPPLIER",
                    string_left)
        sheet.write(3, 0, 'Buyer', string_left)
        sheet.write(3, 1, ': ' + wizard.get_buyer_name() if wizard.buyer_id else ": ALL BUYER", string_left)
        # sheet.write(4, 0, 'Type PR', string_left)
        # sheet.write(4, 1, ': ', string_left)
        purchase_order = self.get_data(wizard)
        row = 7

        # header
        sheet.write(6, 0, 'Number', string_center)
        sheet.write(6, 1, 'No PO', string_center)
        sheet.write(6, 2, 'Tanggal PO', string_center)
        sheet.write(6, 3, 'Supplier', string_center)
        sheet.write(6, 4, 'No PR', string_center)
        sheet.write(6, 5, 'Tipe PR', string_center)
        sheet.write(6, 6, 'Tanggal PR', string_center)
        sheet.write(6, 7, 'IDR', string_center)
        sheet.write(6, 8, 'Lokasi', string_center)
        sheet.write(6, 9, 'TOP', string_center)
        sheet.write(6, 10, 'NOV', string_center)
        sheet.write(6, 11, 'Additional Info', string_center)
        sheet.write(6, 12, 'Keterangan', string_center)
        no = 1

        for po in purchase_order:
            sheet.write(row, 0, no, string_number)
            sheet.write(row, 1, po.name or "", string)
            sheet.write(row, 2, po.date_order.strftime('%d-%b-%y') or "", string)
            sheet.write(row, 3, po.partner_id.alias_name or "", string)
            sheet.write(row, 4, po.pr_numbers or "", string)

            # for line in po['po'].order_line:
            sheet.write(row, 5, "", string)
            sheet.write(row, 6, "", string)
            sheet.write(row, 7, po.amount_total or "", string_right)
            sheet.write(row, 8, "", string)
            sheet.write(row, 9, po.payment_term_id.name or "", string)
            sheet.write(row, 10, "", string)
            sheet.write(row, 11, "", string)
            sheet.write(row, 12, po.po_description or "", string)
            row += 1
            no += 1
