import pytz
from datetime import datetime, date
from odoo import models, _


class PurchaseRequisitionListReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.purchase_requisition_list_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet( \
            '%s' % wizard.company_id.name)
        arguments = {
            'workbook': workbook,
            'sheet': sheet,
            'wizard': wizard,
        }
        sheet.hide_gridlines(2)
        self.set_column_width(sheet)
        self.set_header_data(arguments)
        self.set_table_header_data(arguments)
        self.set_table_body_data(arguments)

    def get_workbook_style(self, workbook):
        return {
            'title_style': workbook.add_format \
                ({'bold': True, 'font_size': 12, 'align': 'center'}),
            'header_style_align_left': workbook.add_format \
                ({'bold': True, 'font_size': 11, 'align': 'left'}),
            'print_date_format': workbook.add_format({'font_size': 8, 'align': 'right'}),
            'period_format': workbook.add_format({'font_size': 11, 'align': 'center'}),
            'num_bold': workbook.add_format({'font_size': 11, 'align': 'right', \
                                             'bold': True, 'num_format': '#,##'}),
            'normal_align_right': workbook.add_format(
                {'font_size': 11, 'valign': 'top', 'align': 'right', 'text_wrap': True}),
            'normal_align_left': workbook.add_format(
                {'font_size': 11, 'valign': 'top', 'align': 'left', 'text_wrap': True}),
            'bold_align_right': workbook.add_format({'font_size': 11, 'valign': 'top', 'align': 'right', 'bold': True}),
            'bold_align_left': workbook.add_format({'font_size': 11, 'valign': 'top', 'align': 'left', 'bold': True}),
            'grand_total': workbook.add_format({'font_size': 11, 'align': 'right', 'bold': True}),
            'table_header': workbook.add_format \
                ({'bold': True, 'valign': 'center', 'align': 'center', 'border': 1}),
            'table_header_no_border_bottom': workbook.add_format \
                ({'bold': True, 'align': 'center', 'top': 1, 'left': 1, 'right': 1}),
            'table_header_no_border_top': workbook.add_format \
                ({'bold': True, 'align': 'center', 'bottom': 1, 'left': 1, 'right': 1}),
            'table_bold_align_left': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'left', 'border': 1, 'text_wrap': True}),
            'table_bold_align_right': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'border': 1, 'text_wrap': True}),
            'table_normal_align_left': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'left', 'border': 1, 'text_wrap': True}),
            'table_normal_align_right': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'right', 'border': 1, 'text_wrap': True}),
            'table_num': workbook.add_format \
                ({'valign': 'top', 'align': 'right', 'num_format': '#,##', 'border': 1, 'text_wrap': True}),
            'table_num_bold': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1,
                  'text_wrap': True}),
            'table_bold_align_left_italic': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'left', 'border': 1, 'text_wrap': True, 'italic': True}),
            'table_bold_align_right_italic': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'border': 1, 'text_wrap': True, 'italic': True}),
        }

    def set_column_width(self, sheet):
        sheet.set_column('A:B', 15)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:J', 50)
        sheet.set_column('K:K', 10)
        sheet.set_column('L:M', 20)
        sheet.set_column('N:O', 15)
        sheet.set_column('P:P', 45)
        sheet.set_column('Q:Q', 35)
        sheet.set_column('R:T', 20)
        sheet.set_column('U:U', 30)
        sheet.set_column('V:V', 20)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])
        header_row = 0
        # sheet.write(header_row, 0, \
        #             'Purchase Requisition List Report', style['title_style'])
        sheet.merge_range('A1:V1', 'Purchase Requisition List Report', style['title_style'])
        header_row += 1

        start_date = wizard.start_date.strftime('%d-%b-%y').upper()
        if wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%d-%b-%y').upper()
            sheet.write(header_row, 0, \
                        'Periode: %s S/D %s' % (start_date, end_date), style['header_style_align_left'])
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            sheet.write(header_row, 0, \
                        'Periode: S/D %s' % (start_date), style['header_style_align_left'])
        elif wizard.date_type and wizard.date_type == 'current_date':
            sheet.write(header_row, 0, \
                        'Periode: %s' % (start_date), style['header_style_align_left'])

        # supplier = ""
        # if wizard.supplier_type == 'specific' and wizard.supplier_ids:
        #     supplier = ", ".join(supplier.name for supplier in wizard.supplier_ids)
        # elif wizard.supplier_type == 'all':
        #     supplier = "All"
        # sheet.write(header_row, 0, 'Supplier: %s' % supplier, style['header_style_align_left'])
        # header_row += 1

        # buyer = ""
        # if wizard.buyer_type == 'specific' and wizard.buyer_ids:
        #     buyer = ", ".join(buyer.name for buyer in wizard.buyer_ids)
        # elif wizard.buyer_type == 'all':
        #     buyer = "All"
        # sheet.write(header_row, 0, 'Buyer: %s' % buyer, style['header_style_align_left'])
        # header_row += 1

        # type = ""
        # if wizard.type_pr == 'specific' and wizard.type_pr_ids:
        #     type = ", ".join(buyer.name for buyer in wizard.type_pr_ids)
        # elif wizard.type_pr == 'all':
        #     type = "All"
        # sheet.write(header_row, 0, 'Type: %s' % type, style['header_style_align_left'])
        # header_row += 1

        # item = ""
        # if wizard.item_id == 'specific' and wizard.item_ids:
        #     item = ", ".join(buyer.name for buyer in wizard.item_ids)
        # elif wizard.item_id == 'all':
        #     item = "All"
        # sheet.write(header_row, 0, 'Item: %s' % item, style['header_style_align_left'])
        # header_row += 1

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'PR Number', 'Creation Date', 'Description', 'Status PR', 'Total Amount', 'Line Number', 'Item Code', 'Item Name',
            'Item Description', 'Cost Center', 'Quantity', 'Price', 'PR Amount', 'PO Number', 'Creation Date', 'Vendor Name',
            'Vendor Site', 'Currency', 'Amount', 'Matched Amount', 'Buyer', 'Closure Status'
        ]

        header_row = 4
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        purchase_order_datas = self.get_purchase_order_data_by_query(arguments)
        if not purchase_order_datas:
            return

        data_row = 5
        index = 1
        for data in purchase_order_datas:
            data_col = 0
            sheet.write(data_row, data_col, index, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('purchase_order_name', ''), \
                        style['table_normal_align_right'])
            data_col += 1

            po_date_order = ''
            if data.get('purchase_order_date', False):
                po_date_order = data['purchase_order_date'].strftime('%d-%b-%y')
            sheet.write(data_row, data_col, po_date_order, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('purchase_order_partner_name', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('purchase_request_name', ''), \
                        style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('type_pr_name', ''), \
                        style['table_normal_align_right'])  # tipe_pr
            data_col += 1

            pr_date_start = ''
            if data.get('purchase_request_date_start', False):
                pr_date_start = data['purchase_request_date_start'].strftime('%d-%b-%y')
            sheet.write(data_row, data_col, pr_date_start, style['table_normal_align_right'])
            data_col += 1

            if data.get('purchase_order_amount_total', 0):
                sheet.write(data_row, data_col, data['purchase_order_amount_total'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('vendor_site_name', ''),
                        style['table_normal_align_right'])  # lokasi
            data_col += 1

            sheet.write(data_row, data_col, data.get('purchase_order_payment_term_name', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])  # nov
            data_col += 1

            sheet.write(data_row, data_col, data.get('term_of_payment', ''), \
                        style['table_normal_align_right'])  # additional_info
            data_col += 1

            sheet.write(data_row, data_col, data.get('purchase_order_description', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            index += 1
            data_row += 1

    def get_purchase_order_data_by_query(self, arguments):
        results = []
        where_clause = self.get_purchase_order_where_clause(arguments)
        query = """
            SELECT
                po."name" AS purchase_order_name,
                po.date_order AS purchase_order_date,
                po.partner_id AS purchase_order_partner_id,
                po.term_of_payment AS term_of_payment,
                rp.name AS purchase_order_partner_name,
                pr."name" AS purchase_request_name,
                pt.name AS type_pr_name,
                pr.date_start AS purchase_request_date_start,
                po.amount_total AS purchase_order_amount_total,
                po.payment_term_id AS purchase_order_payment_term_id,
                rs.name AS vendor_site_name,
                apt."name" AS purchase_order_payment_term_name,
                po.po_description AS purchase_order_description
            FROM purchase_request_purchase_order_line_rel prpolr
            LEFT JOIN purchase_order_line pol ON pol.id = prpolr.purchase_order_line_id
            LEFT JOIN purchase_order po ON po.id = pol.order_id
            LEFT JOIN purchase_request_line prl ON prl.id = prpolr.purchase_request_line_id
            LEFT JOIN purchase_request pr ON pr.id = prl.request_id
            LEFT JOIN res_partner rp ON rp.id = po.partner_id
            LEFT JOIN account_payment_term apt ON apt.id = po.payment_term_id
            LEFT JOIN res_buyer rb ON rb.id = po.buyer_id
            LEFT JOIN res_sites rs ON rs.id = po.sites_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN purchase_request_type_second pt ON pt.id = pr.pr_type_second_id
            %s
            GROUP BY pr.id, po.id, rp.id, apt.id, rs.id, pt.id, pp.id
            ORDER BY rp.id DESC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_purchase_order_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE po.company_id = %s
        """ % wizard.company_id.id

        start_date = wizard.start_date.strftime('%Y-%m-%d')
        if wizard.date_type == 'range_of_date' and wizard.start_date and wizard.end_date:
            end_date = wizard.end_date.strftime('%Y-%m-%d')
            where_clause += """
                AND po.date_order >= '%s' AND po.date_order <= '%s'
            """ % (start_date, end_date)
        elif wizard.date_type == 'current_date' and wizard.start_date:
            where_clause += " AND po.date_order = '%s'" % start_date
        elif wizard.date_type == 'as_of_date' and wizard.start_date:
            where_clause += " AND po.date_order <= '%s'" % start_date

        return where_clause

        # if wizard.supplier_type == 'specific' \
        #         and wizard.supplier_ids and len(wizard.supplier_ids) == 1:
        #     where_clause += " AND rp.id = {0}".format(wizard.supplier_ids.id)
        # elif wizard.supplier_type == 'specific' \
        #         and wizard.supplier_ids and len(wizard.supplier_ids) > 1:
        #     where_clause += " AND rp.id in {0}".format(tuple(wizard.supplier_ids.ids))
        #
        # if wizard.buyer_type == 'specific' \
        #         and wizard.buyer_ids and len(wizard.buyer_ids) == 1:
        #     where_clause += " AND rb.id = {0}".format(wizard.buyer_ids.id)
        # elif wizard.buyer_type == 'specific' \
        #         and wizard.buyer_ids and len(wizard.buyer_ids) > 1:
        #     where_clause += " AND rb.id in {0}".format(tuple(wizard.buyer_ids.ids))
        #
        # if wizard.type_pr == 'specific' \
        #         and wizard.type_pr_ids and len(wizard.type_pr_ids) == 1:
        #     where_clause += " AND pt.id = {0}".format(wizard.type_pr_ids.id)
        # elif wizard.type_pr == 'specific' \
        #         and wizard.type_pr_ids and len(wizard.type_pr_ids) > 1:
        #     where_clause += " AND pt.id in {0}".format(tuple(wizard.type_pr_ids.ids))
        #
        # if wizard.item_id == 'specific' \
        #         and wizard.item_ids and len(wizard.item_ids) == 1:
        #     where_clause += " AND pp.id = {0}".format(wizard.item_ids.id)
        # elif wizard.item_id == 'specific' \
        #         and wizard.item_ids and len(wizard.item_ids) > 1:
        #     where_clause += " AND pp.id in {0}".format(tuple(wizard.item_ids.ids))