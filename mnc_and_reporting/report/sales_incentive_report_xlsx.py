import pytz
from datetime import datetime, date
from odoo import models, _


class SalesIncentiveReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.sales_incentive_report_xlsx'
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
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 35)
        sheet.set_column('F:F', 35)
        sheet.set_column('G:G', 40)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 25)
        sheet.set_column('J:J', 25)
        sheet.set_column('K:K', 25)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')
        sheet.merge_range(header_row, 0, header_row, 10, 'Print date: %s' % print_date, style['print_date_format'])
        header_row += 1

        sheet.merge_range(header_row, 0, header_row, 10, 'SALES INCENTIVE REPORT', style['title_style'])
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
            'Trx Number', 'Trx Date', 'Invoice Amount', 'Advertiser',
            'Brand', 'Sales', 'Receipt Number', 'Age', 'Receipt Amount',
            'Tot. Receipt Amount', 'Outstanding Amount',
        ]

        header_row = 6
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        applied_invoices_data = self.get_applied_invoices_by_query(arguments)
        if not applied_invoices_data:
            return

        customer_row = 7
        data_row = 8
        data_tax_invoice_id_row = 8
        data_index = 0
        total_amount_residual = 0
        total_applied_amount = 0
        looped_customer_ids = []
        looped_tax_invoice_ids = []
        count_data_per_tax_invoice_id = 0

        data_tax_invoice_id_to_write = {}
        for data in applied_invoices_data:
            customer_col = 0
            new_customer = False
            if not looped_customer_ids and data.get('partner_id', False):
                looped_customer_ids.append(data['partner_id'])
                customer_name = data.get('partner_name', '')

                sheet.write(customer_row, customer_col, \
                            'Customer : {customer_name}'.format(customer_name=customer_name), \
                            style['table_bold_align_left'])
                customer_col += 1

                empty_fill_index = 0
                while empty_fill_index <= 9:
                    sheet.write(customer_row, customer_col, '', style['table_bold_align_left'])
                    customer_col += 1
                    empty_fill_index += 1
            elif looped_customer_ids and data.get('partner_id', False) \
                    and data['partner_id'] not in looped_customer_ids:
                customer_row = data_row
                space_between_customer_index = 0
                while space_between_customer_index <= 10:
                    sheet.write(customer_row, customer_col, '', style['table_bold_align_left'])
                    customer_col += 1
                    space_between_customer_index += 1
                customer_row += 1
                data_row += 1

                looped_customer_ids.append(data['partner_id'])

                customer_col = 0
                customer_name = data.get('partner_name', '')
                sheet.write(customer_row, customer_col - 1, '', style['table_bold_align_left'])
                sheet.write(customer_row, customer_col, \
                            'Customer : {customer_name}'.format(customer_name=customer_name), \
                            style['table_bold_align_left'])
                customer_col += 1

                empty_fill_index = 0
                while empty_fill_index <= 9:
                    sheet.write(data_row, customer_col, '', style['table_bold_align_left'])
                    customer_col += 1
                    empty_fill_index += 1

                data_row += 1
                new_customer = True

            # Invoice Tax ID Section
            data_tax_invoice_id_to_write = {}
            if not looped_tax_invoice_ids and data.get('tax_invoice_id', False) and not data_index:
                looped_tax_invoice_ids.append(data['tax_invoice_id'])
            elif not looped_tax_invoice_ids and data.get('tax_invoice_id', False) and data_index:
                looped_tax_invoice_ids.append(data['tax_invoice_id'])
                data_tax_invoice_id_to_write = applied_invoices_data[data_index - 1]
            elif not looped_tax_invoice_ids and not data.get('tax_invoice_id', False) and data_index:
                data_tax_invoice_id_to_write = applied_invoices_data[data_index - 1]
            elif looped_tax_invoice_ids and not data.get('tax_invoice_id', False) and data_index:
                data_tax_invoice_id_to_write = applied_invoices_data[data_index - 1]
            elif looped_tax_invoice_ids and data.get('tax_invoice_id', False) \
                    and data['tax_invoice_id'] not in looped_tax_invoice_ids:
                looped_tax_invoice_ids.append(data['tax_invoice_id'])
                data_tax_invoice_id_to_write = applied_invoices_data[data_index - 1]
            elif looped_customer_ids and data.get('tax_invoice_id', False) \
                    and data['tax_invoice_id'] in looped_tax_invoice_ids \
                    and new_customer and data_index \
                    and applied_invoices_data[data_index - 1].get('tax_invoice_id', False) \
                    and data['tax_invoice_id'] == applied_invoices_data[data_index - 1]['tax_invoice_id']:
                data_tax_invoice_id_to_write = applied_invoices_data[data_index - 1]

            data_col = 3
            sheet.write(data_row, data_col, data.get('advertiser_gen21', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('product_gen21', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('sales_person_gen21', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('receipt_number', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            current_date = date.today()
            age = ''
            if data.get('invoice_date', False) and current_date > data['invoice_date']:
                age = current_date - data['invoice_date']
                age = age.days
            sheet.write(data_row, data_col, age, style['table_normal_align_right'])
            data_col += 1

            if data.get('applied_amount', 0):
                sheet.write(data_row, data_col, data['applied_amount'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_num'])
            total_applied_amount += data.get('applied_amount', 0)
            data_col += 1

            total_amount_residual += data.get('amount_residual', 0)
            if data_tax_invoice_id_to_write:
                data_tax_invoice_id_col = 0
                if count_data_per_tax_invoice_id > 1:
                    sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                      data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                      data_tax_invoice_id_col, \
                                      data_tax_invoice_id_to_write.get('tax_invoice_id', ''),
                                      style['table_normal_align_right'])
                else:
                    sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                data_tax_invoice_id_to_write.get('tax_invoice_id', ''),
                                style['table_normal_align_right'])
                data_tax_invoice_id_col += 1

                invoice_date = data_tax_invoice_id_to_write.get('invoice_date', '')
                if invoice_date:
                    invoice_date = invoice_date.strftime('%d-%b-%y')
                if count_data_per_tax_invoice_id > 1:
                    sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                      data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                      data_tax_invoice_id_col, \
                                      invoice_date or '', style['table_normal_align_right'])
                else:
                    sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                invoice_date or '', style['table_normal_align_right'])
                data_tax_invoice_id_col += 1

                if total_amount_residual:
                    total_amount_residual -= data.get('amount_residual', 0)
                if total_amount_residual:
                    if count_data_per_tax_invoice_id > 1:
                        sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                          data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                          data_tax_invoice_id_col, \
                                          total_amount_residual, style['table_num'])
                    else:
                        sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                    total_amount_residual, style['table_num'])
                else:
                    if count_data_per_tax_invoice_id > 1:
                        sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                          data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                          data_tax_invoice_id_col, \
                                          0, style['table_normal_align_right'])
                    else:
                        sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, 0, \
                                    style['table_normal_align_right'])
                data_tax_invoice_id_col += 7

                if total_applied_amount:
                    total_applied_amount -= data.get('applied_amount', 0)
                if total_applied_amount:
                    if count_data_per_tax_invoice_id > 1:
                        sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                          data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                          data_tax_invoice_id_col, \
                                          total_applied_amount, style['table_num'])
                    else:
                        sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                    total_applied_amount, style['table_num'])
                else:
                    if count_data_per_tax_invoice_id > 1:
                        sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                          data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                          data_tax_invoice_id_col, \
                                          0, style['table_normal_align_right'])
                    else:
                        sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, 0, \
                                    style['table_normal_align_right'])
                data_tax_invoice_id_col += 1

                if total_amount_residual:
                    if count_data_per_tax_invoice_id > 1:
                        sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                          data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                          data_tax_invoice_id_col, \
                                          total_amount_residual, style['table_num'])
                    else:
                        sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                    total_amount_residual, style['table_num'])
                else:
                    if count_data_per_tax_invoice_id > 1:
                        sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                          data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                          data_tax_invoice_id_col, \
                                          0, style['table_normal_align_right'])
                    else:
                        sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, 0, \
                                    style['table_normal_align_right'])

                total_applied_amount = data.get('applied_amount', 0)
                total_amount_residual = data.get('amount_residual', 0)
                data_tax_invoice_id_row += count_data_per_tax_invoice_id

                if data.get('partner_id', False) \
                        and data_tax_invoice_id_to_write.get('partner_id', False) \
                        and data['partner_id'] != data_tax_invoice_id_to_write['partner_id']:
                    data_tax_invoice_id_row += 2

                count_data_per_tax_invoice_id = 0

            count_data_per_tax_invoice_id += 1
            data_index += 1
            data_row += 1

        data_tax_invoice_id_col = 0
        if count_data_per_tax_invoice_id > 1:
            sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                              data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1), data_tax_invoice_id_col, \
                              data.get('tax_invoice_id', ''), style['table_normal_align_right'])
        else:
            sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                        data.get('tax_invoice_id', ''), style['table_normal_align_right'])
        data_tax_invoice_id_col += 1

        invoice_date = data.get('invoice_date', '')
        if invoice_date:
            invoice_date = invoice_date.strftime('%d-%b-%y')
        if count_data_per_tax_invoice_id > 1:
            sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                              data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1), data_tax_invoice_id_col, \
                              invoice_date or '', style['table_normal_align_right'])
        else:
            sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                        invoice_date or '', style['table_normal_align_right'])
        data_tax_invoice_id_col += 1

        if total_amount_residual:
            if count_data_per_tax_invoice_id > 1:
                sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                  data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                  data_tax_invoice_id_col, \
                                  total_amount_residual, style['table_num'])
            else:
                sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                            total_amount_residual, style['table_num'])
        else:
            if count_data_per_tax_invoice_id > 1:
                sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                  data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                  data_tax_invoice_id_col, \
                                  0, style['table_normal_align_right'])
            else:
                sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, 0, \
                            style['table_normal_align_right'])
        data_tax_invoice_id_col += 7

        data_before = applied_invoices_data[data_index - 1]
        if data.get('partner_id', False) and data_before.get('partner_id', False) \
                and data.get('tax_invoice_id', False) and data_before.get('tax_invoice_id', False) \
                and data['partner_id'] == data_before['partner_id'] \
                and data['tax_invoice_id'] != data_before['tax_invoice_id']:
            total_applied_amount -= data.get('applied_amount')

        if total_applied_amount:
            if count_data_per_tax_invoice_id > 1:
                sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                  data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                  data_tax_invoice_id_col, \
                                  total_applied_amount, style['table_num'])
            else:
                sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                            total_applied_amount, style['table_num'])
        else:
            if count_data_per_tax_invoice_id > 1:
                sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                  data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                  data_tax_invoice_id_col, \
                                  0, style['table_normal_align_right'])
            else:
                sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, 0, \
                            style['table_normal_align_right'])
        data_tax_invoice_id_col += 1

        if total_amount_residual:
            if count_data_per_tax_invoice_id > 1:
                sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                  data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                  data_tax_invoice_id_col, \
                                  total_amount_residual, style['table_num'])
            else:
                sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                            total_amount_residual, style['table_num'])
        else:
            if count_data_per_tax_invoice_id > 1:
                sheet.merge_range(data_tax_invoice_id_row, data_tax_invoice_id_col, \
                                  data_tax_invoice_id_row + (count_data_per_tax_invoice_id - 1),
                                  data_tax_invoice_id_col, \
                                  0, style['table_normal_align_right'])
            else:
                sheet.write(data_tax_invoice_id_row, data_tax_invoice_id_col, 0, \
                            style['table_normal_align_right'])
        total_applied_amount = data.get('applied_amount', 0)
        data_tax_invoice_id_row += count_data_per_tax_invoice_id
        count_data_per_tax_invoice_id = 0

    def get_applied_invoices_by_query(self, arguments):
        results = []
        where_clause = self.get_applied_invoices_where_clause(arguments)
        query = """
            SELECT
                rp.id AS partner_id,
                rp.name AS partner_name,
                am.tax_invoice_id AS tax_invoice_id,
                am.date AS invoice_date,
                am.amount_residual AS amount_residual,
                am.advertiser_gen21 AS advertiser_gen21,
                am.product_gen21 AS product_gen21,
                am.sales_person_gen21 AS sales_person_gen21,
                mm.id AS receipt_id,
                mm.receipt_number AS receipt_number,
                ai.applied_amount AS applied_amount
            FROM applied_invoices ai
            LEFT JOIN miscellaneous_miscellaneous mm on mm.id = ai.misc_id
            LEFT JOIN account_move am on am.id = ai.move_id
            LEFT JOIN res_partner rp on rp.id = am.partner_id
            %s
            ORDER BY
                rp.id ASC,
                am.tax_invoice_id ASC,
                mm.id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_applied_invoices_where_clause(self, arguments):
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
