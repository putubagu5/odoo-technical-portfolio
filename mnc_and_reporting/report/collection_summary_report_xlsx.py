import pytz
from datetime import datetime, date
from odoo import models, _


class CollectionSummaryReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.collection_summary_report_xlsx'
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
            'table_header_index': workbook.add_format \
                ({'valign': 'center', 'align': 'center', 'border': 1}),
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
        sheet.set_column('B:B', 35)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:E', 25)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')
        sheet.merge_range(header_row, 0, header_row, 4, 'Print date: %s' % print_date, style['print_date_format'])
        header_row += 1

        sheet.merge_range(header_row, 0, header_row, 10, 'COLLECTION SUMMARY REPORT', style['title_style'])
        header_row += 1

        period = ''
        start_date = wizard.start_date.strftime('%b-%y').capitalize()
        if wizard.date_type and wizard.date_type == 'as_of_date':
            period = 'As of Date : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'current_date':
            period = 'Date : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%b-%y').capitalize()
            period = '{start_date} - {end_date}'.format(start_date=start_date, end_date=end_date)
        sheet.merge_range(header_row, 0, header_row, 10, period, style['title_style'])
        header_row += 1

        sheet.write(header_row, 0, wizard.company_id.name, style['bold_align_left'])

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'No', 'Customer Name', 'Amount Residual', 'Receipt Amount',
            'Outstanding Amount'
        ]

        header_row = 6
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        summary_data = self.get_receipt_by_query(arguments)
        if not summary_data:
            return

        data_row = 7
        index = 1
        total_invoice_amount = 0
        total_amount_residual = 0
        total_applied_amount = 0
        for data in summary_data:
            data_col = 0
            sheet.write(data_row, data_col, index, style['table_header_index'])
            data_col += 1

            sheet.write(data_row, data_col, \
                        data.get('customer_name', ''), style['table_normal_align_left'])
            data_col += 1

            if data.get('invoice_amount', 0):
                sheet.write(data_row, data_col, \
                            data['invoice_amount'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_invoice_amount += data.get('invoice_amount', 0)
            data_col += 1

            if data.get('applied_amount', 0):
                sheet.write(data_row, data_col, \
                            data.get('applied_amount', 0), style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_applied_amount += data.get('applied_amount', 0)
            data_col += 1

            if data.get('amount_residual', 0):
                sheet.write(data_row, data_col, data['amount_residual'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_amount_residual += data.get('amount_residual', 0)
            data_col += 1

            data_row += 1
            index += 1

        grand_total_col = 0
        sheet.write(data_row, grand_total_col, '', style['table_bold_align_right'])
        grand_total_col += 1

        sheet.write(data_row, grand_total_col, 'Total', style['table_bold_align_left'])
        grand_total_col += 1

        if total_invoice_amount:
            sheet.write(data_row, grand_total_col, total_invoice_amount, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_applied_amount:
            sheet.write(data_row, grand_total_col, total_applied_amount, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])
        grand_total_col += 1

        if total_amount_residual:
            sheet.write(data_row, grand_total_col, total_amount_residual, style['table_num'])
        else:
            sheet.write(data_row, grand_total_col, 0, style['table_normal_align_right'])

    def get_receipt_by_query(self, arguments):
        results = []
        where_clause = self.get_receipt_where_clause(arguments)
        query = """
            SELECT
                rp.name as customer_name,
                sum((mm.applied_amount + am.amount_residual)) as invoice_amount,
                sum(mm.applied_amount) as applied_amount,
                sum(am.amount_residual) as amount_residual
            FROM miscellaneous_miscellaneous mm
            LEFT JOIN account_move am on am.id = mm.move_id
            LEFT JOIN res_partner rp on rp.id = am.partner_id 
            %s
            GROUP BY rp.id
            ORDER BY rp.name ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_receipt_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE mm.company_id = %s
        """ % wizard.company_id.id

        if wizard.customer_type == 'specific' and \
                wizard.customer_ids and len(wizard.customer_ids) > 1:
            customer_ids = wizard.customer_ids.ids
            where_clause += ' AND rp.id in {customer_ids}'. \
                format(customer_ids=tuple(customer_ids))
        elif wizard.customer_type == 'specific' and \
                wizard.customer_ids and len(wizard.customer_ids) == 1:
            customer_id = wizard.customer_ids[0].id
            where_clause += ' AND rp.id = {customer_id}'. \
                format(customer_id=customer_id)

        start_date = wizard.start_date.strftime('%Y-%m-%d')
        if wizard.date_type == 'range_of_date' and wizard.start_date and wizard.end_date:
            end_date = wizard.end_date.strftime('%Y-%m-%d')
            where_clause += """
                AND am.date >= '%s' AND am.date <= '%s'
            """ % (start_date, end_date)
        elif wizard.date_type == 'current_date' and wizard.start_date:
            where_clause += " AND am.date = '%s'" % start_date
        elif wizard.date_type == 'as_of_date' and wizard.start_date:
            where_clause += " AND am.date <= '%s'" % start_date

        return where_clause
