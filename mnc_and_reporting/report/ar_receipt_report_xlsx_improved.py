import pytz
from datetime import datetime, date
from odoo import models, _


class ARReceiptReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.ar_receipt_report_xlsx'
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
            'period_format': workbook.add_format({'font_size': 10, 'align': 'center'}),
            'num_bold': workbook.add_format({'font_size': 11, 'align': 'right', \
                                             'bold': True, 'num_format': '#,##'}),
            'bold_align_right': workbook.add_format({'font_size': 11, 'align': 'right', 'bold': True}),
            'grand_total': workbook.add_format({'font_size': 11, 'align': 'right', 'bold': True}),
            'table_header': workbook.add_format \
                ({'bold': True, 'align': 'center', 'border': 1}),
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
        sheet.set_column('A:A', 3)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])
        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')
        sheet.merge_range('A1:I1', 'Print date: %s' % print_date, style['print_date_format'])
        sheet.merge_range('A2:I2', 'AR RECEIPT REPORT', style['title_style'])

        start_date = wizard.start_date.strftime('%d-%b-%y')
        if wizard.date_type and wizard.date_type == 'range_of_date':
            start_date = wizard.start_date.strftime('%b-%y')
            end_date = wizard.end_date.strftime('%b-%y')
            sheet.merge_range('A3:I3', \
                              'Periode: %s s/d %s' % (start_date, end_date), style['period_format'])
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            sheet.merge_range('A3:I3', 'Periode: s/d %s' % (start_date), style['period_format'])
        elif wizard.date_type and wizard.date_type == 'current_date':
            sheet.merge_range('A3:I3', 'Periode: %s' % (start_date), style['period_format'])

        sheet.merge_range('A4:I4', wizard.company_id.name, style['header_style_align_left'])

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'No', 'Customer Name', 'Receipt Number',
            'Bank Account', 'Receipt Amount', 'GL Date',
            'Invoice Number', 'Amount Applied', 'Outstanding'
        ]

        header_row = 5
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        ar_receipt_datas = self.get_ar_receipt_data_by_query(arguments)
        if not ar_receipt_datas:
            return

        invoice_per_receipt = {}
        looped_receipt_ids = []
        looped_customer_ids = []
        wrote_receipt_ids = []
        wrote_customer_ids = []

        customer_row = 6
        receipt_row = 6
        inv_row = 6

        total_invoice_applied_amount = 0
        total_receipt_amount = 0
        total_receipt_remaining_amount = 0

        grand_total_invoice_applied_amount = 0
        grand_total_receipt_amount = 0
        grand_total_receipt_remaining_amount = 0

        index_receipt = 0
        count_invoice_per_customer = 0
        count_invoice_per_receipt = 0
        index = 0
        index_customer = 1
        for data in ar_receipt_datas:
            same_receipt_id_differ_customer_id = False
            data_receipt_to_write = {}
            data_customer_to_write = {}

            if not looped_receipt_ids and data.get('receipt_id', False) \
                    and len(ar_receipt_datas) == 1:
                looped_receipt_ids.append(data['receipt_id'])
                invoice_per_receipt[data['receipt_id']] = [data]
                data_receipt_to_write = data
                count_invoice_per_receipt = 1
            elif not looped_receipt_ids and data.get('receipt_id', False):
                looped_receipt_ids.append(data['receipt_id'])
                invoice_per_receipt[data['receipt_id']] = [data]
            elif looped_receipt_ids and index and data.get('receipt_id', False) \
                    and data['receipt_id'] not in looped_receipt_ids:
                looped_receipt_ids.append(data['receipt_id'])
                invoice_per_receipt[data['receipt_id']] = [data]
                data_receipt_to_write = ar_receipt_datas[index - 1]
            elif looped_receipt_ids and data.get('receipt_id', False) \
                    and looped_customer_ids and data.get('customer_id', False) \
                    and data['receipt_id'] in looped_receipt_ids \
                    and data['customer_id'] not in looped_customer_ids:
                looped_receipt_ids.append(data['receipt_id'])
                invoice_per_receipt[data['receipt_id']] = [data]
                data_receipt_to_write = ar_receipt_datas[index - 1]
                same_receipt_id_differ_customer_id = True
            elif looped_receipt_ids and data.get('receipt_id', False) \
                    and data['receipt_id'] in looped_receipt_ids:
                if invoice_per_receipt.get(data['receipt_id'], []):
                    invoice_per_receipt[data['receipt_id']].append(data)
                else:
                    invoice_per_receipt[data['receipt_id']] = [data]

            if not looped_customer_ids and data.get('customer_id', False) \
                    and len(ar_receipt_datas) == 1:
                looped_customer_ids.append(data['customer_id'])
                data_customer_to_write = data
                count_invoice_per_customer = 1
            elif not looped_customer_ids and data.get('customer_id', False):
                looped_customer_ids.append(data['customer_id'])
            elif looped_customer_ids and index and data.get('customer_id', False) \
                    and data['customer_id'] not in looped_customer_ids:
                looped_customer_ids.append(data['customer_id'])
                data_customer_to_write = ar_receipt_datas[index - 1]
                inv_row += 2

            inv_col = 5
            gl_date = data.get('invoice_move_date', '')
            if gl_date:
                gl_date = gl_date.strftime('%d-%b-%y')

            sheet.write(inv_row, inv_col, gl_date, style['table_normal_align_right'])
            inv_col += 1

            sheet.write(inv_row, inv_col, data.get('payment_reff', ''), \
                        style['table_normal_align_right'])
            inv_col += 1

            if data.get('invoice_applied_amount', 0):
                sheet.write(inv_row, inv_col, data['invoice_applied_amount'], \
                            style['table_num'])
            else:
                sheet.write(inv_row, inv_col, data.get('invoice_applied_amount', 0), \
                            style['table_normal_align_right'])
            total_invoice_applied_amount += data.get('invoice_applied_amount', 0)
            grand_total_invoice_applied_amount += data.get('invoice_applied_amount', 0)

            if data_receipt_to_write:
                receipt_col = 2
                if count_invoice_per_receipt > 1:
                    sheet.merge_range(receipt_row, receipt_col, \
                                      receipt_row + (count_invoice_per_receipt - 1), \
                                      receipt_col, data_receipt_to_write.get('receipt_number', ''),
                                      style['table_normal_align_left'])
                else:
                    sheet.write(receipt_row, receipt_col, \
                                data_receipt_to_write.get('receipt_number', ''), style['table_normal_align_left'])
                receipt_col += 1

                if count_invoice_per_receipt > 1:
                    sheet.merge_range(receipt_row, receipt_col,
                                      receipt_row + (count_invoice_per_receipt - 1), receipt_col,
                                      data_receipt_to_write.get('bank_account', '')
                                      or data_receipt_to_write.get('journal_name', ''),
                                      style['table_normal_align_left'])
                else:
                    sheet.write(receipt_row, receipt_col, \
                                data_receipt_to_write.get('bank_account', '')
                                or data_receipt_to_write.get('journal_name', ''), style['table_normal_align_left'])
                receipt_col += 1

                if data_receipt_to_write.get('receipt_amount', 0):
                    if count_invoice_per_receipt > 1:
                        sheet.merge_range(receipt_row, receipt_col,
                                          receipt_row + (count_invoice_per_receipt - 1),
                                          receipt_col, data_receipt_to_write['receipt_amount'], style['table_num'])
                    else:
                        sheet.write(receipt_row, receipt_col, \
                                    data_receipt_to_write.get('receipt_amount', 0), style['table_num'])
                else:
                    if count_invoice_per_receipt > 1:
                        sheet.merge_range(receipt_row, receipt_col,
                                          receipt_row + (count_invoice_per_receipt - 1),
                                          receipt_col, data_receipt_to_write.get('receipt_amount', 0),
                                          style['table_normal_align_right'])
                    else:
                        sheet.write(receipt_row, receipt_col, \
                                    data_receipt_to_write.get('receipt_amount', 0), style['table_normal_align_right'])
                total_receipt_amount += data_receipt_to_write.get('receipt_amount', 0)
                grand_total_receipt_amount += data_receipt_to_write.get('receipt_amount', 0)
                receipt_col += 4

                remaining_amount = self.get_ar_receipt_remaining_amount( \
                    data_receipt_to_write, invoice_per_receipt[data_receipt_to_write['receipt_id']])
                if remaining_amount:
                    if count_invoice_per_receipt > 1:
                        sheet.merge_range(receipt_row, receipt_col,
                                          receipt_row + (count_invoice_per_receipt - 1),
                                          receipt_col, remaining_amount, style['table_num'])
                    else:
                        sheet.write(receipt_row, receipt_col, remaining_amount, style['table_num'])
                else:
                    if count_invoice_per_receipt > 1:
                        sheet.merge_range(receipt_row, receipt_col,
                                          receipt_row + (count_invoice_per_receipt - 1),
                                          receipt_col, remaining_amount, style['table_normal_align_right'])
                    else:
                        sheet.write(receipt_row, receipt_col, \
                                    remaining_amount, style['table_normal_align_right'])
                total_receipt_remaining_amount += remaining_amount
                grand_total_receipt_remaining_amount += remaining_amount

                index_receipt += 1
                receipt_row += count_invoice_per_receipt
                count_invoice_per_receipt = 0
                wrote_receipt_ids.append(data_receipt_to_write['receipt_id'])

            if data_customer_to_write:
                customer_col = 0
                sheet.merge_range(customer_row, customer_col, \
                                  customer_row + count_invoice_per_customer, \
                                  customer_col, index_customer, style['table_normal_align_right'])
                customer_col += 1

                sheet.merge_range(customer_row, customer_col, \
                                  customer_row + count_invoice_per_customer, \
                                  customer_col, data_customer_to_write.get('customer_name'),
                                  style['table_bold_align_left'])
                customer_col += 1

                sheet.write(customer_row + count_invoice_per_customer, customer_col, '', \
                            style['table_normal_align_left'])
                customer_col += 1

                sheet.write(customer_row + count_invoice_per_customer, customer_col, \
                            'Sub total', style['table_bold_align_left'])
                customer_col += 1

                if total_receipt_amount:
                    sheet.write(customer_row + count_invoice_per_customer, \
                                customer_col, total_receipt_amount, style['table_num_bold'])
                else:
                    sheet.write(customer_row + count_invoice_per_customer, \
                                customer_col, total_receipt_amount, style['table_bold_align_right'])
                customer_col += 1

                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, '', style['table_normal_align_left'])
                customer_col += 1

                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, '', style['table_normal_align_left'])
                customer_col += 1

                if total_invoice_applied_amount and len(ar_receipt_datas) > 1:
                    total_invoice_applied_amount -= data.get('invoice_applied_amount', 0)
                if total_invoice_applied_amount:
                    sheet.write(customer_row + count_invoice_per_customer, \
                                customer_col, total_invoice_applied_amount, style['table_num_bold'])
                else:
                    sheet.write(customer_row + count_invoice_per_customer, \
                                customer_col, total_invoice_applied_amount, style['table_bold_align_right'])
                customer_col += 1

                if total_receipt_remaining_amount:
                    sheet.write(customer_row + count_invoice_per_customer, \
                                customer_col, total_receipt_remaining_amount, style['table_num_bold'])
                else:
                    sheet.write(customer_row + count_invoice_per_customer, \
                                customer_col, total_receipt_remaining_amount, style['table_bold_align_right'])

                total_receipt_amount = 0
                total_receipt_remaining_amount = 0
                total_invoice_applied_amount = data.get('invoice_applied_amount', 0)

                index_customer += 1
                customer_row += count_invoice_per_customer + 2
                count_invoice_per_customer = 0

                receipt_row += 2

                wrote_customer_ids.append(data_customer_to_write['customer_id'])

                # Space between each customer
                sheet.write(customer_row - 1, 0, '', style['table_bold_align_right'])
                sheet.write(customer_row - 1, 1, '', style['table_bold_align_right'])
                sheet.merge_range(customer_row - 1, 2, customer_row - 1, 8, '', style['table_bold_align_right'])

            inv_row += 1
            index += 1
            count_invoice_per_receipt += 1
            count_invoice_per_customer += 1

        # Handle last data
        if data.get('receipt_id', False) \
                and ((wrote_receipt_ids and data['receipt_id'] not in wrote_receipt_ids) \
                     or same_receipt_id_differ_customer_id):
            data_receipt_to_write = data
            receipt_col = 2
            if count_invoice_per_receipt > 1:
                sheet.merge_range(receipt_row, receipt_col, \
                                  receipt_row + (count_invoice_per_receipt - 1), \
                                  receipt_col, data_receipt_to_write.get('receipt_number', ''),
                                  style['table_normal_align_left'])
            else:
                sheet.write(receipt_row, receipt_col, \
                            data_receipt_to_write.get('receipt_number', ''), style['table_normal_align_left'])
            receipt_col += 1

            if count_invoice_per_receipt > 1:
                sheet.merge_range(receipt_row, receipt_col,
                                  receipt_row + (count_invoice_per_receipt - 1), receipt_col,
                                  data_receipt_to_write.get('bank_account', '')
                                  or data_receipt_to_write.get('journal_name', ''), style['table_normal_align_left'])
            else:
                sheet.write(receipt_row, receipt_col, \
                            data_receipt_to_write.get('bank_account', '')
                            or data_receipt_to_write.get('journal_name', ''), style['table_normal_align_left'])
            receipt_col += 1

            if data_receipt_to_write.get('receipt_amount', 0):
                if count_invoice_per_receipt > 1:
                    sheet.merge_range(receipt_row, receipt_col,
                                      receipt_row + (count_invoice_per_receipt - 1),
                                      receipt_col, data['receipt_amount'], style['table_num'])
                else:
                    sheet.write(receipt_row, receipt_col, \
                                data_receipt_to_write.get('receipt_amount', 0), style['table_num'])
            else:
                if count_invoice_per_receipt > 1:
                    sheet.merge_range(receipt_row, receipt_col,
                                      receipt_row + (count_invoice_per_receipt - 1),
                                      receipt_col, data_receipt_to_write.get('receipt_amount', 0),
                                      style['table_normal_align_right'])
                else:
                    sheet.write(receipt_row, receipt_col, \
                                data_receipt_to_write.get('receipt_amount', 0), style['table_normal_align_right'])
            total_receipt_amount += data_receipt_to_write.get('receipt_amount', 0)
            grand_total_receipt_amount += data_receipt_to_write.get('receipt_amount', 0)
            receipt_col += 4

            remaining_amount = self.get_ar_receipt_remaining_amount( \
                data_receipt_to_write, invoice_per_receipt[data_receipt_to_write['receipt_id']])
            if remaining_amount:
                if count_invoice_per_receipt > 1:
                    sheet.merge_range(receipt_row, receipt_col,
                                      receipt_row + (count_invoice_per_receipt - 1),
                                      receipt_col, remaining_amount, style['table_num'])
                else:
                    sheet.write(receipt_row, receipt_col, remaining_amount, style['table_num'])
            else:
                if count_invoice_per_receipt > 1:
                    sheet.merge_range(receipt_row, receipt_col,
                                      receipt_row + (count_invoice_per_receipt - 1),
                                      receipt_col, remaining_amount, style['table_normal_align_right'])
                else:
                    sheet.write(receipt_row, receipt_col, \
                                remaining_amount, style['table_normal_align_right'])
            total_receipt_remaining_amount += remaining_amount
            grand_total_receipt_remaining_amount += remaining_amount

            index_receipt += 1
            receipt_row += count_invoice_per_receipt
            count_invoice_per_receipt = 0
            wrote_receipt_ids.append(data_receipt_to_write['receipt_id'])

        if data.get('customer_id', False) and wrote_customer_ids \
                and data['customer_id'] not in wrote_customer_ids:
            data_customer_to_write = data
            customer_col = 0
            sheet.merge_range(customer_row, customer_col, \
                              customer_row + count_invoice_per_customer, \
                              customer_col, index_customer, style['table_normal_align_right'])
            customer_col += 1

            sheet.merge_range(customer_row, customer_col, \
                              customer_row + count_invoice_per_customer, \
                              customer_col, data_customer_to_write.get('customer_name'), style['table_bold_align_left'])
            customer_col += 1

            sheet.write(customer_row + count_invoice_per_customer, customer_col, '', \
                        style['table_normal_align_left'])
            customer_col += 1

            sheet.write(customer_row + count_invoice_per_customer, customer_col, \
                        'Sub total', style['table_bold_align_left'])
            customer_col += 1

            if total_receipt_amount:
                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, total_receipt_amount, style['table_num_bold'])
            else:
                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, total_receipt_amount, style['table_bold_align_right'])
            customer_col += 1

            sheet.write(customer_row + count_invoice_per_customer, \
                        customer_col, '', style['table_normal_align_left'])
            customer_col += 1

            sheet.write(customer_row + count_invoice_per_customer, \
                        customer_col, '', style['table_normal_align_left'])
            customer_col += 1

            if total_invoice_applied_amount:
                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, total_invoice_applied_amount, style['table_num_bold'])
            else:
                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, total_invoice_applied_amount, style['table_bold_align_right'])
            customer_col += 1

            if total_receipt_remaining_amount:
                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, total_receipt_remaining_amount, style['table_num_bold'])
            else:
                sheet.write(customer_row + count_invoice_per_customer, \
                            customer_col, total_receipt_remaining_amount, style['table_bold_align_right'])

            total_receipt_amount = 0
            total_receipt_remaining_amount = 0
            total_invoice_applied_amount = 0

            index_customer += 1
            customer_row += count_invoice_per_customer + 2
            count_invoice_per_customer = 0

            receipt_row += 2

            wrote_customer_ids.append(data_customer_to_write['customer_id'])

            # Space between each customer
            sheet.write(customer_row - 1, 0, '', style['table_bold_align_right'])
            sheet.write(customer_row - 1, 1, '', style['table_bold_align_right'])
            sheet.merge_range(customer_row - 1, 2, customer_row - 1, 8, '', style['table_bold_align_right'])

        sheet.write(customer_row, 0, '', style['table_bold_align_right'])
        sheet.write(customer_row, 1, '', style['table_bold_align_right'])
        sheet.merge_range(customer_row, 2, customer_row, 8, '', style['table_bold_align_right'])

        grand_total_row = customer_row + 2
        grand_total_col = 3

        sheet.write(grand_total_row, grand_total_col, 'Grand Total', style['grand_total'])
        grand_total_col += 1

        if grand_total_receipt_amount:
            sheet.write(grand_total_row, grand_total_col, grand_total_receipt_amount, \
                        style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, grand_total_receipt_amount, \
                        style['bold_align_right'])
        grand_total_col += 3

        if grand_total_invoice_applied_amount:
            sheet.write(grand_total_row, grand_total_col, grand_total_invoice_applied_amount, \
                        style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, grand_total_invoice_applied_amount, \
                        style['bold_align_right'])
        grand_total_col += 1

        if grand_total_receipt_remaining_amount:
            sheet.write(grand_total_row, grand_total_col, grand_total_receipt_remaining_amount, \
                        style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, grand_total_receipt_remaining_amount, \
                        style['bold_align_right'])

    def get_ar_receipt_data_by_query(self, arguments):
        results = []
        where_clause = self.get_ar_receipt_where_clause(arguments)
        query = """
            SELECT
                rp.id as customer_id,
                rp.name as customer_name,
                rpb.acc_number as bank_account,
                mm.id as receipt_id,
                mm.receipt_number as receipt_number,
                mm.applied_amount as receipt_amount,
                mm.amount as receipt_amount,
                ai.applied_amount as invoice_applied_amount,
                ai.transaction_type as invoice_transaction_type,
                ai.id as invoice_id,
                am.name as invoice_number,
                am3.id as invoice_move_id,
                am3.state as invoice_move_state,
                am3.date as invoice_move_date,
                am.payment_reference as payment_reff,
                aj.name as journal_name
            FROM applied_invoices ai
            LEFT JOIN miscellaneous_miscellaneous mm ON mm.id = ai.misc_id
            LEFT JOIN account_move am ON am.id = ai.invoice_id
            LEFT JOIN account_move am3 ON am3.id = ai.move_id
            LEFT JOIN account_move am2 ON am2.id = mm.move_id
            LEFT JOIN res_partner rp ON rp.id = am.partner_id
            LEFT JOIN account_journal aj ON aj.id = mm.journal_id
            LEFT JOIN res_partner_bank rpb ON rpb.id = aj.bank_account_id
            %s
            ORDER BY 
                rp.id ASC,
                mm.id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_ar_receipt_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE mm.company_id = %s
            AND ai.transaction_type = 'apply'
        """ % wizard.company_id.id
        start_date = wizard.start_date.strftime('%Y-%m-%d')
        if wizard.date_type == 'range_of_date' and wizard.start_date and wizard.end_date:
            end_date = wizard.end_date.strftime('%Y-%m-%d')
            where_clause += """
                AND am2.date >= '%s' AND am2.date <= '%s'
            """ % (start_date, end_date)
        elif wizard.date_type == 'current_date' and wizard.start_date:
            where_clause += " AND am2.date = '%s'" % start_date
        elif wizard.date_type == 'as_of_date' and wizard.start_date:
            where_clause += " AND am2.date <= '%s'" % start_date

        return where_clause

    def get_ar_receipt_remaining_amount(self, receipt_data, inv_datas):
        total_amount_applied = 0
        remaining_amount = 0
        if receipt_data.get('receipt_amount', 0):
            remaining_amount = receipt_data['receipt_amount']

        for data in inv_datas:
            reverse = self.env['account.move'].search([('reversed_entry_id', '=', data.get('invoice_move_id', False))])
            if data.get('invoice_move_state', False) \
                    and data.get('invoice_transaction_type', False) \
                    and data['invoice_move_state'] == 'posted' \
                    and data['invoice_transaction_type'] == 'apply' and not reverse:
                total_amount_applied += data.get('invoice_applied_amount', 0)

        remaining_amount = receipt_data.get('receipt_amount', 0) - \
                           total_amount_applied

        return remaining_amount
