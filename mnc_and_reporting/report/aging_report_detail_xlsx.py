import pytz
from datetime import datetime, date
from odoo import models, _


class AgingReportDetailXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.aging_report_detail_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet(wizard.company_id.name)
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
            'bold_align_right': workbook.add_format({'font_size': 11, 'align': 'right', 'bold': True}),
            'bold_align_left': workbook.add_format({'font_size': 11, 'align': 'left', 'bold': True}),
            'grand_total': workbook.add_format({'font_size': 11, 'align': 'right', 'bold': True}),
            'table_header': workbook.add_format \
                ({'bold': True, 'valign': 'center', 'align': 'center', 'border': 1}),
            'table_header_no_border_bottom': workbook.add_format \
                ({'bold': True, 'align': 'center', 'top': 1, 'left': 1, 'right': 1}),
            'table_header_no_border_top': workbook.add_format \
                ({'bold': True, 'align': 'center', 'bottom': 1, 'left': 1, 'right': 1}),
            'table_bold_align_left': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'left', 'border': 1}),
            'table_bold_align_right': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'border': 1}),
            'table_normal_align_left': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'left', 'border': 1}),
            'table_normal_align_right': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'right', 'border': 1}),
            'table_num': workbook.add_format \
                ({'valign': 'top', 'align': 'right', 'num_format': '#,##', 'border': 1}),
            'table_percent_with_decimal': workbook.add_format \
                ({'valign': 'top', 'align': 'right', 'num_format': '#,##%', 'border': 1}),
            'table_percent_no_decimal': workbook.add_format \
                ({'valign': 'top', 'align': 'right', 'num_format': '#%', 'border': 1}),
            'table_num_bold': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1}),
        }

    def set_column_width(self, sheet):
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 30)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 25)
        sheet.set_column('I:I', 25)
        sheet.set_column('J:J', 25)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 20)
        sheet.set_column('S:S', 20)
        sheet.set_column('T:T', 20)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')
        sheet.merge_range(header_row, 0, header_row, 10, 'Print date: %s' % print_date, style['print_date_format'])
        header_row += 1

        sheet.merge_range(header_row, 0, header_row, 10, 'Aging Account Receivable Per Customer Summary',
                          style['title_style'])
        header_row += 1

        period = ''
        start_date = wizard.start_date.strftime('%Y/%m/%d %H:%M:%S')
        if wizard.date_type and wizard.date_type == 'as_of_date':
            period = 'As of Date : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'current_date':
            period = 'Date : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%Y/%m/%d %H:%M:%S')
            period = '{start_date} - {end_date}'.format(start_date=start_date, end_date=end_date)
        sheet.merge_range(header_row, 0, header_row, 10, period, style['title_style'])
        header_row += 1

        sheet.write(header_row, 0, wizard.company_id.name, style['bold_align_left'])

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'Product', 'PO Number', 'Account Number', 'PO Type', 'Transaction Type', 'Advertiser',
            'Sales Name', 'Invoice Number', 'Due Date', 'Period Tayang',
            'Invoice Amount', 'Pembayaran', 'Age', 'Outstanding Amount', 'Current Amount',
            'Bucket', 'Bucket', 'Bucket', 'Bucket', 'Bucket'
        ]

        header_bucket = ['(1 - 30)', '(31 - 60)', '(61 - 90)', '(91 - 365)', '(> 365)']

        header_row = 6
        header_col = 0
        for header in headers:
            if header != 'Bucket':
                header_style = style['table_header_no_border_bottom']
                header_style.set_align('vcenter')
                sheet.merge_range(header_row, header_col, \
                                  header_row + 1, header_col, header, \
                                  style['table_header_no_border_bottom'])
            else:
                sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

        bukcet_col = 15
        bucket_row = header_row + 1
        for bucket in header_bucket:
            sheet.write(bucket_row, bukcet_col, bucket, style['table_header_no_border_top'])
            bukcet_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        detail_data = self.get_invoice_data(arguments)
        if not detail_data:
            return

        data_row = 8
        total_amount_all = 0
        total_applied_amount = 0
        total_amount_residual = 0
        total_current_amount = 0
        total_bucket_1 = 0
        total_bucket_2 = 0
        total_bucket_3 = 0
        total_bucket_4 = 0
        total_bucket_5 = 0
        for data in detail_data:
            total_amount_all_per_customer = 0
            total_applied_amount_per_customer = 0
            total_amount_residual_per_customer = 0
            total_current_amount_per_customer = 0
            total_bucket_1_per_customer = 0
            total_bucket_2_per_customer = 0
            total_bucket_3_per_customer = 0
            total_bucket_4_per_customer = 0
            total_bucket_5_per_customer = 0

            customer_col = 0
            customer = data['customer']
            sheet.write(data_row, customer_col, 'Customer Name :', style['table_bold_align_left'])
            customer_col += 1

            sheet.write(data_row, customer_col, customer.name or '', style['table_bold_align_left'])
            customer_col += 1

            sheet.write(data_row, customer_col, '', style['table_bold_align_left'])
            customer_col += 1

            sheet.write(data_row, customer_col, '', style['table_bold_align_left'])
            customer_col += 1

            sheet.write(data_row, customer_col, 'Customer ID : {0}'. \
                        format(customer.partner_no), style['table_bold_align_left'])
            customer_col += 1

            for index in range(0, 15):
                sheet.write(data_row, customer_col, '', style['table_bold_align_left'])
                customer_col += 1

            data_row += 1
            for inv_data in data['invoices']:
                data_col = 0
                invoice = inv_data['invoice']

                # product = self.env['product.product']
                # inv_line_with_product = invoice.invoice_line_ids. \
                #     filtered(lambda line: line.product_id)
                # if inv_line_with_product:
                #     product = inv_line_with_product[0].product_id
                # sheet.write(data_row, data_col, product.name or '', style['table_normal_align_right'])
                # data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.product_gen21 or '', style['table_normal_align_right'])
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.po_numbers_gen21 or '', style['table_normal_align_right'])
                data_col += 1

                account = self.env['account.account']
                line_with_account = invoice.line_ids. \
                    filtered(lambda line: line.account_id)
                if line_with_account:
                    account = line_with_account[0].account_id
                sheet.write(data_row, data_col, \
                            account.code or '', style['table_normal_align_right'])  # account_number
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.po_type_gen21 or '', style['table_normal_align_right'])
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.transaction_type_id.name or '', style['table_normal_align_right'])
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.advertiser_gen21 or '', style['table_normal_align_right'])
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.sales_person_gen21 or '', style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.payment_reference or '', style['table_normal_align_left'])
                data_col += 1

                invoice_date_due = ''
                if invoice and invoice.invoice_date_due:
                    invoice_date_due = invoice.invoice_date_due.strftime('%d-%b-%y')
                sheet.write(data_row, data_col, \
                            invoice_date_due or '', style['table_normal_align_right'])
                data_col += 1

                sheet.write(data_row, data_col, \
                            invoice.periode_gen21 or '', style['table_normal_align_left'])  # period_tayang
                data_col += 1

                if invoice.amount_total:
                    sheet.write(data_row, data_col, invoice.amount_total, style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_amount_all_per_customer += invoice.amount_total
                data_col += 1

                applied_amount = 0
                valid_applied_misc = invoice.applied_misc_ids. \
                    filtered(lambda misc: misc.applied_amount)
                for applied_misc in valid_applied_misc:
                    applied_amount += applied_misc.applied_amount
                if applied_amount:
                    sheet.write(data_row, data_col, applied_amount, style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_applied_amount_per_customer += applied_amount
                data_col += 1

                sheet.write(data_row, data_col, \
                            inv_data['age'] or '', style['table_normal_align_right'])
                data_col += 1

                if invoice.amount_residual:
                    sheet.write(data_row, data_col, invoice.amount_residual, style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_amount_residual_per_customer += invoice.amount_residual
                data_col += 1

                current_amount = invoice.amount_total - applied_amount
                if current_amount:
                    sheet.write(data_row, data_col, current_amount, style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_current_amount_per_customer += current_amount
                data_col += 1

                if inv_data.get('bucket_1', 0):
                    sheet.write(data_row, data_col, inv_data['bucket_1'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_bucket_1_per_customer += inv_data.get('bucket_1', 0)
                data_col += 1

                if inv_data.get('bucket_2', 0):
                    sheet.write(data_row, data_col, inv_data['bucket_2'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_bucket_2_per_customer += inv_data.get('bucket_2', 0)
                data_col += 1

                if inv_data.get('bucket_3', 0):
                    sheet.write(data_row, data_col, inv_data['bucket_3'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_bucket_3_per_customer += inv_data.get('bucket_3', 0)
                data_col += 1

                if inv_data.get('bucket_4', 0):
                    sheet.write(data_row, data_col, inv_data['bucket_4'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_bucket_4_per_customer += inv_data.get('bucket_4', 0)
                data_col += 1

                if inv_data.get('bucket_5', 0):
                    sheet.write(data_row, data_col, inv_data['bucket_5'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_bucket_5_per_customer += inv_data.get('bucket_5', 0)
                data_col += 1
                data_row += 1

            subtotal_per_customer_col = 0
            for index in range(0, 12):
                sheet.write(data_row, subtotal_per_customer_col, '', style['table_normal_align_left'])
                subtotal_per_customer_col += 1

            sheet.write(data_row, subtotal_per_customer_col, 'Sub Total', style['table_bold_align_right'])
            subtotal_per_customer_col += 1

            if total_amount_residual_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, \
                            total_amount_residual_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_amount_residual += total_amount_all_per_customer
            subtotal_per_customer_col += 1

            if total_current_amount_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, \
                            total_current_amount_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_current_amount += total_current_amount_per_customer
            subtotal_per_customer_col += 1

            if total_bucket_1_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, total_bucket_1_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_bucket_1 += total_bucket_1_per_customer
            subtotal_per_customer_col += 1

            if total_bucket_2_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, total_bucket_2_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_bucket_2 += total_bucket_2_per_customer
            subtotal_per_customer_col += 1

            if total_bucket_3_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, total_bucket_3_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_bucket_3 += total_bucket_3_per_customer
            subtotal_per_customer_col += 1

            if total_bucket_4_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, total_bucket_4_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_bucket_4 += total_bucket_4_per_customer
            subtotal_per_customer_col += 1

            if total_bucket_5_per_customer:
                sheet.write(data_row, subtotal_per_customer_col, total_bucket_5_per_customer, style['table_num'])
            else:
                sheet.write(data_row, subtotal_per_customer_col, 0, style['table_normal_align_right'])
            total_bucket_5 += total_bucket_5_per_customer
            subtotal_per_customer_col += 1

            data_row += 1

            percentage_per_customer_col = 0
            for index in range(0, 12):
                sheet.write(data_row, percentage_per_customer_col, '', style['table_normal_align_left'])
                percentage_per_customer_col += 1

            sheet.write(data_row, percentage_per_customer_col, \
                        'Persentase', style['table_bold_align_right'])
            percentage_per_customer_col += 1

            sheet.write(data_row, percentage_per_customer_col, \
                        1, style['table_percent_no_decimal'])
            percentage_per_customer_col += 1

            current_amount_percent_per_cust = 0
            if total_amount_all_per_customer:
                current_amount_percent_per_cust = \
                    (total_current_amount_per_customer / total_amount_all_per_customer)
                if current_amount_percent_per_cust < 0:
                    current_amount_percent_per_cust = 0
            if current_amount_percent_per_cust:
                sheet.write(data_row, percentage_per_customer_col, \
                            current_amount_percent_per_cust, style['table_percent_with_decimal'])
            else:
                sheet.write(data_row, percentage_per_customer_col, \
                            '0,00%', style['table_normal_align_right'])
            percentage_per_customer_col += 1

            bucket_1_percent_per_cust = 0
            if total_amount_residual_per_customer:
                bucket_1_percent_per_cust = \
                    (total_bucket_1_per_customer / total_amount_residual_per_customer)
            if bucket_1_percent_per_cust:
                sheet.write(data_row, percentage_per_customer_col, \
                            bucket_1_percent_per_cust, style['table_percent_with_decimal'])
            else:
                sheet.write(data_row, percentage_per_customer_col, \
                            '0,00%', style['table_normal_align_right'])
            percentage_per_customer_col += 1

            bucket_2_percent_per_cust = 0
            if total_amount_residual_per_customer:
                bucket_2_percent_per_cust = \
                    (total_bucket_2_per_customer / total_amount_residual_per_customer)
            if bucket_2_percent_per_cust:
                sheet.write(data_row, percentage_per_customer_col, \
                            bucket_2_percent_per_cust, style['table_percent_with_decimal'])
            else:
                sheet.write(data_row, percentage_per_customer_col, \
                            '0,00%', style['table_normal_align_right'])
            percentage_per_customer_col += 1

            bucket_3_percent_per_cust = 0
            if total_amount_residual_per_customer:
                bucket_3_percent_per_cust = \
                    (total_bucket_3_per_customer / total_amount_residual_per_customer)
            if bucket_3_percent_per_cust:
                sheet.write(data_row, percentage_per_customer_col, \
                            bucket_3_percent_per_cust, style['table_percent_with_decimal'])
            else:
                sheet.write(data_row, percentage_per_customer_col, \
                            '0,00%', style['table_normal_align_right'])
            percentage_per_customer_col += 1

            bucket_4_percent_per_cust = 0
            if total_amount_residual_per_customer:
                bucket_4_percent_per_cust = \
                    (total_bucket_4_per_customer / total_amount_residual_per_customer)
            if bucket_4_percent_per_cust:
                sheet.write(data_row, percentage_per_customer_col, \
                            bucket_4_percent_per_cust, style['table_percent_with_decimal'])
            else:
                sheet.write(data_row, percentage_per_customer_col, \
                            '0,00%', style['table_normal_align_right'])
            percentage_per_customer_col += 1

            bucket_5_percent_per_cust = 0
            if total_amount_residual_per_customer:
                bucket_5_percent_per_cust = \
                    (total_bucket_5_per_customer / total_amount_residual_per_customer)
            if bucket_5_percent_per_cust:
                sheet.write(data_row, percentage_per_customer_col, \
                            bucket_5_percent_per_cust, style['table_percent_with_decimal'])
            else:
                sheet.write(data_row, percentage_per_customer_col, \
                            '0,00%', style['table_normal_align_right'])
            percentage_per_customer_col += 1

            data_row += 1

            total_amount_all += total_amount_all_per_customer
            total_applied_amount += total_applied_amount_per_customer

        empty_section_col = 0
        for index in range(0, 19):
            sheet.write(data_row, empty_section_col, '', style['table_normal_align_left'])
            empty_section_col += 1

        data_row += 1

        grand_total_col = 0
        for index in range(0, 11):
            sheet.write(data_row, grand_total_col, '', style['table_normal_align_left'])
            grand_total_col += 1

        grand_total_row = data_row
        sheet.write(grand_total_row, grand_total_col, 'Grand Total', style['table_bold_align_right'])
        grand_total_col += 1

        if total_amount_residual:
            sheet.write(grand_total_row, grand_total_col, total_amount_residual, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_current_amount:
            sheet.write(grand_total_row, grand_total_col, total_current_amount, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_1:
            sheet.write(grand_total_row, grand_total_col, total_bucket_1, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_2:
            sheet.write(grand_total_row, grand_total_col, total_bucket_2, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_3:
            sheet.write(grand_total_row, grand_total_col, total_bucket_3, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_4:
            sheet.write(grand_total_row, grand_total_col, total_bucket_4, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_5:
            sheet.write(grand_total_row, grand_total_col, total_bucket_5, style['table_num'])
        else:
            sheet.write(grand_total_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

    def get_invoice_data(self, arguments):
        Invoices = self.get_invoice_by_query(arguments)
        customers_in_invoices = Invoices.mapped('partner_id')
        detail_data = []
        for customer in customers_in_invoices:
            invoices_per_customer = Invoices. \
                filtered(lambda inv: inv.partner_id.id == customer.id)
            data_per_customer = {'customer': customer, 'invoices': []}
            for invoice in invoices_per_customer:
                bucket_1, bucket_2, bucket_3, bucket_4, bucket_5 = self. \
                    categorize_invoice_by_due_date(invoice)
                age = self.get_invoice_due_date_difference_days(invoice)
                data_per_customer['invoices'].append({
                    'invoice': invoice,
                    'age': age,
                    'bucket_1': bucket_1,
                    'bucket_2': bucket_2,
                    'bucket_3': bucket_3,
                    'bucket_4': bucket_4,
                    'bucket_5': bucket_5,
                })

            detail_data.append(data_per_customer)

        return detail_data

    def get_invoice_by_query(self, arguments):
        results = []
        where_clause = self.get_invoice_where_clause(arguments)
        query = """
            SELECT
                am.id as invoice_id
            FROM account_move am
            LEFT JOIN res_partner rp on rp.id = am.partner_id
            %s
            ORDER BY am.partner_id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.fetchall()
        raw_invoice_ids = []
        if results:
            raw_invoice_ids = [data[0] for data in results]

        return self.env['account.move'].browse(raw_invoice_ids)

    def get_invoice_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE am.company_id = %s
            AND am.move_type = 'out_invoice'
            AND am.state = 'posted'
        """ % wizard.company_id.id

        if wizard.customer_type == 'specific' and \
                wizard.customer_ids and len(wizard.customer_ids) > 1:
            customer_ids = wizard.customer_ids.ids
            where_clause += ' AND rp.id in {customer_ids}'. \
                format(customer_ids=tuple(customer_ids))
        if wizard.customer_type == 'specific' and \
                wizard.customer_ids and len(wizard.customer_ids) == 1:
            customer_id = wizard.customer_ids[0].id
            where_clause += ' AND rp.id = {customer_id}'. \
                format(customer_id=customer_id)

        start_date = wizard.start_date.strftime('%Y-%m-%d')
        if wizard.date_type == 'range_of_date' and wizard.start_date and wizard.end_date:
            end_date = wizard.end_date.strftime('%Y-%m-%d')
            where_clause += """
                AND am.invoice_date >= '%s' AND am.invoice_date <= '%s'
            """ % (start_date, end_date)
        elif wizard.date_type == 'current_date' and wizard.start_date:
            where_clause += " AND am.invoice_date = '%s'" % start_date
        elif wizard.date_type == 'as_of_date' and wizard.start_date:
            where_clause += " AND am.invoice_date <= '%s'" % start_date

        return where_clause

    def categorize_invoice_by_due_date(self, invoice):
        bucket_1 = 0
        bucket_2 = 0
        bucket_3 = 0
        bucket_4 = 0
        bucket_5 = 0

        difference_days = self.get_invoice_due_date_difference_days(invoice)
        if difference_days >= 1 and difference_days <= 30:
            bucket_1 = invoice.amount_residual
        elif difference_days >= 31 and difference_days <= 60:
            bucket_2 = invoice.amount_residual
        elif difference_days >= 61 and difference_days <= 90:
            bucket_3 = invoice.amount_residual
        elif difference_days >= 91 and difference_days <= 365:
            bucket_4 = invoice.amount_residual
        elif difference_days > 365:
            bucket_5 = invoice.amount_residual

        return bucket_1, bucket_2, bucket_3, bucket_4, bucket_5

    def get_invoice_due_date_difference_days(self, invoice):
        difference_days = 0
        current_date = date.today()
        if invoice.amount_residual and invoice.invoice_date_due \
                and current_date > invoice.invoice_date_due:
            difference_days = current_date - invoice.invoice_date_due
            difference_days = difference_days.days

        return difference_days
