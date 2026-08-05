import pytz
from datetime import datetime, date
from odoo import models, _


class InvoicePrepaymentPaidSupplierXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.inv_prepayment_paid_supplier_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet( \
            '%s AP - Invoice Prepayment Paid For Supplier v3' % wizard.company_id.name)
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
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 50)
        sheet.set_column('F:F', 30)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 30)
        sheet.set_column('I:I', 30)
        sheet.set_column('I:I', 30)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 30)
        sheet.set_column('M:M', 30)
        sheet.set_column('N:N', 30)
        sheet.set_column('O:O', 30)
        sheet.set_column('P:P', 30)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 10)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])
        header_row = 0
        sheet.write(header_row, 0, \
                    'Invoice (Prepayment) Detail of Account Payable', style['header_style_align_left'])
        header_row += 1

        sheet.write(header_row, 0, wizard.company_id.name, style['header_style_align_left'])
        header_row += 1

        start_date = wizard.start_date.strftime('%b-%Y').capitalize()
        if wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%b-%Y').capitalize()
            sheet.write(header_row, 0, \
                        'Period: %s s/d %s' % (start_date, end_date), style['header_style_align_left'])
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            sheet.write(header_row, 0, \
                        'Period: s/d %s' % (start_date), style['header_style_align_left'])
        elif wizard.date_type and wizard.date_type == 'current_date':
            sheet.write(header_row, 0, \
                        'Period: %s' % (start_date), style['header_style_align_left'])

        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y')
        sheet.write(header_row, 16, 'Date of Print: %s' % print_date, style['print_date_format'])
        header_row += 1

        account = ""
        if wizard.account_type == 'specific' and wizard.account_ids:
            account = ", ".join('{0} - {1}'.format(account.code, account.name) \
                                for account in wizard.account_ids)
        elif wizard.account_type == 'all':
            account = "All"
        sheet.write(header_row, 0, 'Account: %s' % account, style['header_style_align_left'])
        header_row += 1

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'No', 'Vendor Id', 'Vendor Name', 'No Invoice', 'Description', 'Tgl Invoice',
            'Curr', 'Exchange Rate', 'Amount', 'Functional Amount (Rp)',
            'Amount Remaining (Rp)', 'Account', 'Invoice Voucher', 'Payment Voucher', 'JV Number',
            'Employee Name', 'Payment Status', 'Approve'
        ]

        header_row = 6
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        bill_datas = self.get_bill_data(arguments)
        if not bill_datas:
            return

        data_row = 7
        index = 1
        total_amount = 0
        total_amount_total_signed = 0
        total_amount_residual = 0
        for vendor_id, bill_per_vendor in bill_datas.items():
            total_amount_per_vendor = 0
            total_amount_total_signed_per_vendor = 0
            total_amount_residual_per_vendor = 0
            data_col = 0
            vendor_id = self.env['res.partner'].browse(vendor_id)
            count_bill_bill_per_vendor = len(bill_per_vendor)

            if count_bill_bill_per_vendor and count_bill_bill_per_vendor > 1:
                sheet.merge_range(data_row, data_col, \
                                  data_row + (count_bill_bill_per_vendor - 1), \
                                  data_col, index, style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, index, style['table_normal_align_left'])
            data_col += 1

            vendor_code = ""
            if vendor_id.partner_no:
                vendor_code = vendor_id.partner_no

            if count_bill_bill_per_vendor and count_bill_bill_per_vendor > 1:
                sheet.merge_range(data_row, data_col, \
                                  data_row + (count_bill_bill_per_vendor - 1), \
                                  data_col, vendor_code, style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, vendor_code, style['table_normal_align_left'])
            data_col += 1

            if count_bill_bill_per_vendor and count_bill_bill_per_vendor > 1:
                sheet.merge_range(data_row, data_col, \
                                  data_row + (count_bill_bill_per_vendor - 1), \
                                  data_col, vendor_id.alias_name, style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, vendor_id.alias_name, style['table_normal_align_left'])
            data_col += 1
            for bill in bill_per_vendor:
                data_col = 3
                sheet.write(data_row, data_col, bill.get('payment_reference', ''), style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, bill.get('description', ''), style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, bill.get('date', ''), style['table_normal_align_left'])
                data_col += 1

                currency_id = self.env['res.currency'].browse(bill.get('currency_id', []))
                sheet.write(data_row, data_col, currency_id.name or '', style['table_normal_align_left'])
                data_col += 1

                if currency_id.rate:
                    sheet.write(data_row, data_col, currency_id.rate or '', style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                data_col += 1

                if bill.get('amount_total', 0):
                    sheet.write(data_row, data_col, bill['amount_total'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_amount_per_vendor += bill.get('amount_total', 0)
                data_col += 1

                if bill.get('amount_total_signed', 0):
                    sheet.write(data_row, data_col, bill['amount_total_signed'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_amount_total_signed_per_vendor += bill.get('amount_total_signed', 0)
                data_col += 1

                if bill.get('amount_residual', 0):
                    sheet.write(data_row, data_col, bill['amount_residual'], style['table_num'])
                else:
                    sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
                total_amount_residual_per_vendor += bill.get('amount_residual', 0)
                data_col += 1

                inv_line_account = self.env['account.move'].browse(bill.get('bill_id', [])).invoice_line_ids.filtered(
                    lambda line: not line.exclude_from_invoice_tab
                                 and line.account_id.id in wizard.account_ids.ids
                ).mapped('account_id')
                sheet.write(data_row, data_col, \
                            inv_line_account[0].code if inv_line_account else '', \
                            style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, bill.get('voucher_no', ''), style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, bill.get('voucher_no', ''), style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, bill.get('name', ''), style['table_normal_align_left'])
                data_col += 1

                sheet.write(data_row, data_col, bill.get('employee_text', ''), style['table_normal_align_left'])
                data_col += 1

                payment_state = dict(wizard._fields['prepayment_state'].selection).get(bill.get('payment_state', ''),
                                                                                       '')
                if not payment_state:
                    payment_state = bill.get('payment_state', '')
                sheet.write(data_row, data_col, payment_state, style['table_normal_align_left'])
                data_col += 1

                state = dict(wizard.env['account.move']._fields['state'].selection).get(bill.get('state', ''), '')
                if not state:
                    state = bill.get('state', '')
                sheet.write(data_row, data_col, state, style['table_normal_align_left'])
                data_col += 1

                data_row += 1

            total_amount += total_amount_per_vendor
            total_amount_total_signed += total_amount_total_signed_per_vendor
            total_amount_residual += total_amount_residual_per_vendor
            index += 1

        total_col = 0
        sheet.merge_range(data_row, total_col, data_row, total_col + 7, 'Total: ', style['table_normal_align_right'])
        total_col += 8

        if total_amount:
            sheet.write(data_row, total_col, total_amount, style['table_num'])
        else:
            sheet.write(data_row, total_col, 0, style['table_normal_align_right'])
        total_col += 1

        if total_amount_total_signed:
            sheet.write(data_row, total_col, total_amount_total_signed, style['table_num'])
        else:
            sheet.write(data_row, total_col, 0, style['table_normal_align_right'])
        total_col += 1

        if total_amount_residual:
            sheet.write(data_row, total_col, total_amount_residual, style['table_num'])
        else:
            sheet.write(data_row, total_col, 0, style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

        sheet.write(data_row, total_col, '', style['table_normal_align_right'])
        total_col += 1

    def get_bill_data(self, arguments):
        bills = self.get_bill_data_by_query(arguments)
        list_of_vendor_ids = list(map(lambda data: data.get('vendor_id', False), bills))
        all_data = {vendor_id: {} for vendor_id in list_of_vendor_ids}
        for vendor_id in list_of_vendor_ids:
            bill_per_vendor = list(filter( \
                lambda data: data.get('vendor_id', False) \
                             and data['vendor_id'] == vendor_id, bills))
            all_data[vendor_id] = bill_per_vendor

        return all_data

    def get_bill_data_by_query(self, arguments):
        results = []
        where_clause = self.get_bill_where_clause(arguments)
        query = """
            SELECT
                am.id as bill_id,
                am.date as date,
                am.partner_id as vendor_id,
                am.name as no_invoice,
                am.ref as description,
                am.invoice_date as invoice_date,
                am.currency_id as currency_id,
                am.amount_total as amount_total,
                am.amount_residual as amount_residual,
                am.payment_reference as payment_reference,
                am.amount_total_signed as amount_total_signed,
                am.amount_residual_signed as amount_residual_signed,
                am.voucher_no as voucher_no,
                am.employee_text as employee_text,
                am.payment_state as payment_state,
                am.state as state
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            LEFT JOIN res_partner rp ON rp.id = am.partner_id
            %s
            GROUP BY am.id
            ORDER BY am.partner_id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_bill_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE am.company_id = %s
            AND am.move_type = 'in_invoice'
            AND am.bill_type = 'prepayment'
            AND am.state = 'posted'
        """ % wizard.company_id.id

        if wizard.account_type == 'specific' \
                and wizard.account_ids and len(wizard.account_ids) == 1:
            where_clause += " AND aml.account_id = {0}".format(wizard.account_ids.id)
        elif wizard.account_type == 'specific' \
                and wizard.account_ids and len(wizard.account_ids) > 1:
            where_clause += " AND aml.account_id in {0}".format(tuple(wizard.account_ids.ids))

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

        if wizard.prepayment_state:
            where_clause += " AND am.payment_state = '{0}'".format(wizard.prepayment_state)

        return where_clause
