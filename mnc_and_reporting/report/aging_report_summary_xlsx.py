import pytz
from datetime import datetime, date
from odoo import models, _


class AgingReportSummaryXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.aging_report_summary_xlsx'
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
            'table_num_bold': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1}),
        }

    def set_column_width(self, sheet):
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 40)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)

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
            'No', 'Account Number', 'Customer Name', 'Customer Type', 'Customer ID', 'Outstanding Amount',
            'Current Amount',
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

        bukcet_col = 7
        bucket_row = header_row + 1
        for bucket in header_bucket:
            sheet.write(bucket_row, bukcet_col, bucket, style['table_header_no_border_top'])
            bukcet_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        summary_data = self.get_invoice_summary_data(arguments)
        if not summary_data:
            return

        data_row = 8
        index = 1
        total_amount_residual = 0
        total_current_amount = 0
        total_bucket_1 = 0
        total_bucket_2 = 0
        total_bucket_3 = 0
        total_bucket_4 = 0
        total_bucket_5 = 0
        for data in summary_data:
            data_col = 0
            sheet.write(data_row, data_col, index, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            customer = data['customer']
            sheet.write(data_row, data_col, customer.name or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, \
                        customer.partner_type_id.display_name or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, \
                        customer.partner_no or '', style['table_normal_align_left'])
            data_col += 1

            if data.get('amount_residual', 0):
                sheet.write(data_row, data_col, \
                            data['amount_residual'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_amount_residual += data.get('amount_residual', 0)
            data_col += 1

            if data.get('current_amount', 0):
                sheet.write(data_row, data_col, \
                            data.get('current_amount', 0), style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_current_amount += data.get('current_amount', 0)
            data_col += 1

            if data.get('bucket_1', 0):
                sheet.write(data_row, data_col, data['bucket_1'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_bucket_1 += data.get('bucket_1', 0)
            data_col += 1

            if data.get('bucket_2', 0):
                sheet.write(data_row, data_col, data['bucket_2'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_bucket_2 += data.get('bucket_2', 0)
            data_col += 1

            if data.get('bucket_3', 0):
                sheet.write(data_row, data_col, data['bucket_3'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_bucket_3 += data.get('bucket_3', 0)
            data_col += 1

            if data.get('bucket_4', 0):
                sheet.write(data_row, data_col, data['bucket_4'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_bucket_4 += data.get('bucket_4', 0)
            data_col += 1

            if data.get('bucket_5', 0):
                sheet.write(data_row, data_col, data['bucket_5'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_bucket_5 += data.get('bucket_5', 0)
            data_col += 1

            data_row += 1

            index += 1

        grand_total_col = 0
        sheet.merge_range(data_row, grand_total_col, data_row, \
                          grand_total_col + 4, 'Grand Total', style['table_bold_align_right'])
        grand_total_col += 5

        if total_amount_residual:
            sheet.write(data_row, grand_total_col, total_amount_residual, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_current_amount:
            sheet.write(data_row, grand_total_col, total_current_amount, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_1:
            sheet.write(data_row, grand_total_col, total_bucket_1, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_2:
            sheet.write(data_row, grand_total_col, total_bucket_2, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_3:
            sheet.write(data_row, grand_total_col, total_bucket_3, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_4:
            sheet.write(data_row, grand_total_col, total_bucket_4, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_bucket_5:
            sheet.write(data_row, grand_total_col, total_bucket_5, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])

    def get_invoice_summary_data(self, arguments):
        Invoices = self.get_invoice_by_query(arguments)
        customers_in_invoices = Invoices.mapped('partner_id')
        summary_data = []
        for customer in customers_in_invoices:
            invoices_per_customer = Invoices. \
                filtered(lambda inv: inv.partner_id.id == customer.id)
            total_payment_invoice_per_cust = 0
            for applied_misc in invoices_per_customer.mapped('applied_misc_ids'). \
                    filtered(lambda misc: misc.applied_amount):
                total_payment_invoice_per_cust += applied_misc.applied_amount

            total_inv_amount_residual = sum(invoices_per_customer.mapped('amount_residual'))
            total_inv_amount_total = sum(invoices_per_customer.mapped('amount_total'))
            total_inv_current_amount = total_inv_amount_total - total_payment_invoice_per_cust
            bucket_1, bucket_2, bucket_3, bucket_4, bucket_5 = self. \
                categorize_invoices_by_due_date(invoices_per_customer)

            summary_data.append({
                'customer': customer,
                'amount_residual': total_inv_amount_residual,
                'current_amount': total_inv_current_amount,
                'bucket_1': bucket_1,
                'bucket_2': bucket_2,
                'bucket_3': bucket_3,
                'bucket_4': bucket_4,
                'bucket_5': bucket_5
            })

        return summary_data

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

    def categorize_invoices_by_due_date(self, invoices):
        bucket_1 = 0
        bucket_2 = 0
        bucket_3 = 0
        bucket_4 = 0
        bucket_5 = 0

        current_date = date.today()
        for invoice in invoices:
            if invoice.amount_residual and invoice.invoice_date_due \
                    and current_date > invoice.invoice_date_due:
                difference_day = current_date - invoice.invoice_date_due
                difference_day = difference_day.days

                if difference_day >= 1 and difference_day <= 30:
                    bucket_1 += invoice.amount_residual
                elif difference_day >= 31 and difference_day <= 60:
                    bucket_2 += invoice.amount_residual
                elif difference_day >= 61 and difference_day <= 90:
                    bucket_3 += invoice.amount_residual
                elif difference_day >= 91 and difference_day <= 365:
                    bucket_4 += invoice.amount_residual
                elif difference_day > 365:
                    bucket_5 += invoice.amount_residual

        return bucket_1, bucket_2, bucket_3, bucket_4, bucket_5
