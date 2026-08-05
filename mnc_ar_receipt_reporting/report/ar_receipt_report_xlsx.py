import pytz
from datetime import datetime
from odoo import models, _


class ARReceiptReportXLSX(models.AbstractModel):
    _name = 'report.mnc_ar_receipt_reporting.ar_receipt_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        for company in wizard.company_ids:
            sheet = workbook.add_worksheet(company.name)
            arguments = {
                'workbook': workbook,
                'sheet': sheet,
                'wizard': wizard,
                'company_id': company,
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
                ({'valign': 'top', 'font_size': 11,'align': 'left', 'border': 1}),
            'table_normal_align_right': workbook.add_format \
                ({'valign': 'top', 'font_size': 11,'align': 'right', 'border': 1}),
            'table_num': workbook.add_format \
                ({'valign': 'top', 'align': 'right','num_format': '#,##', 'border': 1}),
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
        sheet, wizard, company_id= arguments['sheet'], arguments['wizard'], arguments['company_id']
        style = self.get_workbook_style(arguments['workbook'])
        start_date = wizard.start_date.strftime('%b-%y')
        end_date = wizard.end_date.strftime('%b-%y')
        print_date = datetime.now().astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')

        sheet.merge_range('A1:I1', 'Print date: %s' % print_date, style['print_date_format'])
        sheet.merge_range('A2:I2', 'AR RECEIPT REPORT', style['title_style'])
        sheet.merge_range('A3:I3', 'Periode: %s s/d %s' % (start_date, end_date), style['period_format'])
        sheet.merge_range('A4:I4', company_id.name, style['header_style_align_left'])

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'No', 'Customer Name', 'Receipt Num',
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

        ar_receipt_datas = self.get_ar_receipt_data(arguments)
        if not ar_receipt_datas:
            return

        cust_row, data_row = 6, 6
        index = 0
        used_customer_name = []
        grand_total_receipt_amount = 0
        grand_total_inv_amount_applied = 0
        grand_total_remaining_amount = 0
        for customer_id, data_per_customer in ar_receipt_datas.items():
            new_customer_data = False
            customer_name = self.env['res.partner'].browse(customer_id).name
            total_remaining_amount = 0; total_inv_amount_applied = 0; total_receipt_amount = 0

            count_invoice_data_per_customer = 0
            if data_per_customer:
                list_invoices_data_per_customer = list(data_per_customer.values())
                for list_of_inv in list_invoices_data_per_customer:
                    count_invoice_data_per_customer += len(list_of_inv)

            if not used_customer_name or (customer_name and used_customer_name \
                    and customer_name not in used_customer_name):
                index += 1
                if index > 1:
                    new_customer_data = True
                if new_customer_data:
                    data_row += 1

            for receipt_id, list_of_invoice in data_per_customer.items():
                receipt = self.env['miscellaneous.miscellaneous'].browse(receipt_id)
                receipt_col = 2

                sheet.merge_range(data_row, receipt_col, 
                    data_row + (len(list_of_invoice) - 1), 
                    receipt_col, receipt.receipt_number, style['table_normal_align_left'])
                receipt_col += 1

                sheet.merge_range(data_row, receipt_col,
                    data_row + (len(list_of_invoice) - 1), receipt_col,
                    receipt.partner_bank_id.acc_number, style['table_normal_align_left'])
                receipt_col += 1

                if receipt.applied_amount:
                    sheet.merge_range(data_row, receipt_col,
                        data_row + (len(list_of_invoice) - 1),
                        receipt_col, receipt.applied_amount, style['table_num'])
                else:
                    sheet.merge_range(data_row, receipt_col,
                        data_row + (len(list_of_invoice) - 1),
                        receipt_col, receipt.applied_amount, style['table_normal_align_right'])
                total_receipt_amount += receipt.applied_amount
                receipt_col += 4

                if receipt.remaining_amount:
                    sheet.merge_range(data_row, receipt_col,
                        data_row + (len(list_of_invoice) - 1),
                        receipt_col, receipt.remaining_amount, style['table_num'])
                else:
                    sheet.merge_range(data_row, receipt_col,
                        data_row + (len(list_of_invoice) - 1),
                        receipt_col, receipt.remaining_amount, style['table_normal_align_right'])
                total_remaining_amount += receipt.remaining_amount

                for invoice in list_of_invoice:
                    inv_col = 5
                    gl_date = self.env['applied.invoices'].\
                        browse(invoice.get('applied_invoice_id', [])).date
                    if gl_date:
                        gl_date = gl_date.strftime('%d-%b-%y')

                    sheet.write(data_row, inv_col, gl_date, style['table_normal_align_right'])
                    inv_col += 1

                    sheet.write(data_row, inv_col, invoice.get('invoice_number', ''), \
                        style['table_normal_align_right'])
                    inv_col += 1

                    if invoice.get('amount_applied', 0):
                        sheet.write(data_row, inv_col, invoice['amount_applied'], \
                            style['table_num'])
                    else:
                        sheet.write(data_row, inv_col, invoice['amount_applied'], \
                            style['table_normal_align_right'])
                    total_inv_amount_applied += invoice.get('amount_applied', 0)
                    data_row += 1

            cust_col = 0
            sheet.merge_range(cust_row, cust_col, cust_row + count_invoice_data_per_customer, 
                cust_col, index, style['table_normal_align_right'])
            cust_col += 1

            sheet.merge_range(cust_row, cust_col, cust_row + count_invoice_data_per_customer,
                cust_col, customer_name, style['table_bold_align_left'])
            used_customer_name.append(customer_name)
            cust_col += 1
            
            sheet.write(cust_row + count_invoice_data_per_customer, cust_col, '', \
                style['table_normal_align_left'])
            cust_col += 1

            sheet.write(cust_row + count_invoice_data_per_customer, cust_col, \
                'Sub total', style['table_bold_align_left'])
            cust_col += 1

            if total_receipt_amount:
                sheet.write(cust_row + count_invoice_data_per_customer, \
                    cust_col, total_receipt_amount, style['table_num_bold'])
            else:
                sheet.write(cust_row + count_invoice_data_per_customer, \
                    cust_col, total_receipt_amount, style['table_bold_align_right'])
            cust_col += 1

            sheet.write(cust_row + count_invoice_data_per_customer, \
                cust_col, '', style['table_normal_align_left'])
            cust_col += 1

            sheet.write(cust_row + count_invoice_data_per_customer, \
                cust_col, '', style['table_normal_align_left'])
            cust_col += 1

            if total_inv_amount_applied:
                sheet.write(cust_row + count_invoice_data_per_customer, \
                    cust_col, total_inv_amount_applied, style['table_num_bold'])
            else:
                sheet.write(cust_row + count_invoice_data_per_customer, \
                    cust_col, total_inv_amount_applied, style['table_bold_align_right'])
            cust_col += 1

            if total_remaining_amount:
                sheet.write(cust_row + count_invoice_data_per_customer, \
                    cust_col, total_remaining_amount, style['table_num_bold'])
            else:
                sheet.write(cust_row + count_invoice_data_per_customer, \
                    cust_col, total_remaining_amount, style['table_bold_align_right'])

            cust_row = data_row + 1
            
            add_space_row = cust_row
            add_space_col = 0
            sheet.write(add_space_row, add_space_col, '', style['table_normal_align_right'])
            add_space_col += 1
            sheet.write(add_space_row, add_space_col, '', style['table_normal_align_right'])
            add_space_col += 1
            sheet.merge_range(add_space_row, add_space_col, add_space_row, \
                add_space_col + 6, '', style['table_normal_align_right'])
            data_row += 1
            cust_row += 1
            
            grand_total_receipt_amount += total_receipt_amount
            grand_total_inv_amount_applied += total_inv_amount_applied
            grand_total_remaining_amount += total_remaining_amount

        grand_total_row = data_row + 2
        grand_total_col = 3
        sheet.write(grand_total_row, grand_total_col, 'Grand Total', style['grand_total'])
        grand_total_col += 1

        if grand_total_receipt_amount:
            sheet.write(grand_total_row, grand_total_col, \
                grand_total_receipt_amount, style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, \
                grand_total_receipt_amount, style['bold_align_right'])
        grand_total_col += 3

        if grand_total_inv_amount_applied:
            sheet.write(grand_total_row, grand_total_col, \
                grand_total_inv_amount_applied, style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, \
                grand_total_inv_amount_applied, style['bold_align_right'])
        grand_total_col += 1

        if grand_total_remaining_amount:
            sheet.write(grand_total_row, grand_total_col, \
                grand_total_remaining_amount, style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, \
                grand_total_remaining_amount, style['bold_align_right'])

    def get_ar_receipt_data(self, arguments):
        results = self.get_ar_receipt_data_by_query(arguments)
        list_of_customer_ids = list(map(lambda data: data.get('customer_id'), results))
        all_data = {customer_id: {} for customer_id in list_of_customer_ids}
        for customer_id in list_of_customer_ids:
            data_per_customer = list(\
                filter(lambda data: data.get('customer_id', False) \
                and data['customer_id'] == customer_id, results))
            data_receipt_per_customer = list(\
                dict.fromkeys(map(lambda data: data.get('misc_id', False), data_per_customer))) 
            for receipt in data_receipt_per_customer:
                data_invoice_per_receipt = list(\
                    filter(lambda data: data.get('misc_id', False) \
                    and data['misc_id'] == receipt, data_per_customer))
                all_data[customer_id][receipt] = data_invoice_per_receipt

        return all_data

    def get_ar_receipt_data_by_query(self, arguments):
        results = []
        company_id = arguments['company_id']
        wizard = arguments['wizard']
        start_date = wizard.start_date.strftime('%Y-%m-%d')
        end_date = wizard.end_date.strftime('%Y-%m-%d')
        if company_id and start_date and end_date:
            company_id = company_id.id
            query = """
                SELECT
                    rp.id as customer_id,
                    rp.name as customer_name,
                    mm.receipt_number as receipt_num,
                    rpb.acc_number as bank_account,
                    mm.applied_amount as receipt_amount,
                    am.name as invoice_number,
                    ai.applied_amount as amount_applied,
                    ai.id as applied_invoice_id,
                    ai.misc_id as misc_id
                FROM applied_invoices ai
                LEFT JOIN miscellaneous_miscellaneous mm on mm.id = ai.misc_id
                LEFT JOIN account_move am on am.id = ai.invoice_id
                LEFT JOIN account_move am2 on am2.id = ai.move_id
                LEFT JOIN res_partner rp on rp.id = am.partner_id
                LEFT JOIN res_partner_bank rpb on rpb.id = mm.partner_bank_id
                WHERE
                    mm.company_id = %s
                    AND am2.date >= '%s'
                    AND am2.date <= '%s'
                ORDER BY rp.name ASC
            """ % (company_id, start_date, end_date)
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()

        return results