import pytz
from datetime import datetime, date
from odoo import models, _


class SubledgerDetailsReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.subledger_details_report_xlsx'
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
        sheet.set_column('A:A', 45)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 30)
        sheet.set_column('G:G', 30)
        sheet.set_column('H:H', 30)
        sheet.set_column('I:I', 30)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 30)
        sheet.set_column('M:M', 30)
        sheet.set_column('N:N', 30)
        sheet.set_column('O:O', 30)
        sheet.set_column('P:P', 30)
        sheet.set_column('Q:Q', 30)
        sheet.set_column('R:R', 30)
        sheet.set_column('S:S', 30)
        sheet.set_column('T:T', 30)
        sheet.set_column('U:U', 30)
        sheet.set_column('V:V', 30)
        sheet.set_column('W:W', 30)
        sheet.set_column('X:X', 30)
        sheet.set_column('Y:Y', 30)
        sheet.set_column('Z:Z', 30)
        sheet.set_column('AA:AA', 30)
        sheet.set_column('AB:AB', 45)
        sheet.set_column('AC:AC', 30)
        sheet.set_column('AD:AD', 30)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        sheet.merge_range(header_row, 0, header_row, 30, wizard.company_id.name, style['title_style'])
        header_row += 1

        sheet.merge_range(header_row, 0, header_row, 30, 'SUB LEDGER DETAIL', style['title_style'])
        header_row += 1

        sheet.write(header_row, 0, 'Period :', style['normal_align_right'])

        start_date = wizard.start_date.strftime('%d-%b').capitalize()
        sheet.write(header_row, 1, start_date, style['normal_align_right'])

        if wizard.date_type and wizard.date_type == 'range_of_date' and wizard.end_date:
            end_date = wizard.end_date.strftime('%d-%b').capitalize()
            sheet.write(header_row, 2, end_date, style['normal_align_right'])
        header_row += 1

        sheet.write(header_row, 0, 'Company :', style['normal_align_right'])
        sheet.write(header_row, 1, wizard.company_id.company_code or '', style['normal_align_right'])

        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M:%S').capitalize()
        sheet.write(header_row, 18, 'Print date :', style['normal_align_right'])
        sheet.write(header_row, 19, print_date, style['normal_align_right'])
        header_row += 1

        sheet.write(header_row, 0, 'Cost Center :', style['normal_align_right'])
        cost_center = 'ALL COST CENTER'
        if wizard.analytic_account_type == 'specific':
            cost_center = ', '.join(account.code for account in wizard.analytic_account_ids)
        sheet.write(header_row, 1, cost_center, style['normal_align_right'])

        sheet.write(header_row, 18, 'User :', style['normal_align_right'])
        sheet.write(header_row, 19, self.env.user.name, style['normal_align_right'])
        header_row += 1

        # sheet.write(header_row, 0, 'Area :', style['normal_align_right'])
        # sheet.write(header_row, 1, 'ALL AREA', style['normal_align_right'])
        # header_row += 1

        # sheet.write(header_row, 0, 'Future1 :', style['normal_align_right'])
        # sheet.write(header_row, 1, 'ALL FUTURE1', style['normal_align_right'])
        # header_row += 1
        #
        # sheet.write(header_row, 0, 'Future2 :', style['normal_align_right'])
        # sheet.write(header_row, 1, 'ALL FUTURE2', style['normal_align_right'])
        # header_row += 1

        sheet.write(header_row, 0, 'Account :', style['normal_align_right'])
        account = 'ALL ACCOUNT'
        if wizard.account_type == 'specific':
            account = ', '.join(account.code for account in wizard.account_ids)
        sheet.write(header_row, 1, account, style['normal_align_right'])

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'COA', 'Account', 'Cost Center', 'Area', 'Journal Name', 'Source',
            'Category', 'Gl Date', 'Descriptions', 'Beginning Balance', 'Debit',
            'Credit', 'Ending Balance', 'Customer/Supplier', 'Project Number', 'PO Number',
            'Invoice Number', 'Gl Date Invoice', 'Type', 'MO Number', 'Voucher Number',
            'Gl Date Voucher', 'Curr Code', 'Curr Type', 'Curr Rate', 'Valas', 'Batch',
            'Description Line Journal', 'Faktur Pajak', 'Date Faktur',
        ]

        header_row = 9
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        account_move_line_data = self.get_account_move_line_data(arguments)
        if not account_move_line_data:
            return

        account_row = 10
        data_row = 11
        space_row = 14
        data_index = 0
        looped_account_ids = []
        count_data_per_account = 0
        total_debit_per_account = 0
        total_credit_per_account = 0
        total_ending_balance_per_account = 0
        total_sum_of_ending_balance_per_account = 0
        total_sum_of_debit_per_account = 0
        total_sum_of_credit_per_account = 0
        total_sum_of_ending_balance_per_account_to_write = 0
        beginning_balance = 0
        for data in account_move_line_data:
            last_data = False
            data_account_to_write = {}
            if not looped_account_ids and data.get('account_id', False):
                looped_account_ids.append(data['account_id'])
                beginning_balance = self. \
                    get_account_beginning_balance(arguments, data.get('account_id', False))
            elif looped_account_ids and data.get('account_id', False) \
                    and data['account_id'] not in looped_account_ids and data_index:
                looped_account_ids.append(data['account_id'])
                data_account_to_write = account_move_line_data[data_index - 1]
                total_sum_of_ending_balance_per_account_to_write = total_sum_of_ending_balance_per_account
                total_sum_of_ending_balance_per_account = 0
                beginning_balance = self. \
                    get_account_beginning_balance(arguments, data.get('account_id', False))
                data_row += 2

            # Handle last account data to write
            if looped_account_ids and data.get('account_id', False) \
                    and data['account_id'] in looped_account_ids \
                    and data_index and (len(account_move_line_data) - 1) == data_index:
                count_data_per_account += 1
                data_account_to_write = data
                last_data = True

            data_col = 0
            coa_code = ''
            if wizard.company_id.company_code:
                coa_code += wizard.company_id.company_code
            if data.get('account_code', ''):
                coa_code += '.' + data['account_code']
            if data.get('analytic_account_code', ''):
                coa_code += '.' + data['analytic_account_code']
            if data.get('operating_unit_code', ''):
                coa_code += '.' + data['operating_unit_code']
            if data.get(''):
                coa_code += '.' + data['000']
            if data.get(''):
                coa_code += '.' + data['000']
            if data.get(''):
                coa_code += '.' + data['000']

            sheet.write(data_row, data_col, coa_code, style['table_normal_align_right'])
            data_col += 1  # coa

            sheet.write(data_row, data_col, data.get('account_code', ''), style['table_normal_align_right'])
            data_col += 1  # account

            sheet.write(data_row, data_col, data.get('analytic_account_code', ''), style['table_normal_align_right'])
            data_col += 1  # cost_center

            sheet.write(data_row, data_col, data.get('operating_unit_code', ''), style['table_normal_align_right'])
            data_col += 1  # area

            sheet.write(data_row, data_col, data.get('journal_number', ''), style['table_normal_align_right'])
            data_col += 1  # journal_name

            sheet.write(data_row, data_col, data.get('journal_type', ''), style['table_normal_align_right'])
            data_col += 1  # source

            sheet.write(data_row, data_col, data.get('journal_name', ''), style['table_normal_align_right'])
            data_col += 1  # category

            move_line_date = data.get('move_line_date', '')
            if move_line_date:
                move_line_date = move_line_date.strftime('%d-%b-%y').capitalize()
            sheet.write(data_row, data_col, move_line_date, style['table_normal_align_right'])
            data_col += 1  # gl_date

            sheet.write(data_row, data_col, data.get('move_line_name', ''), style['table_normal_align_right'])
            data_col += 1  # description

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # beginning_balance

            if data.get('move_line_debit', 0):
                sheet.write(data_row, data_col, data['move_line_debit'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_debit_per_account += data.get('move_line_debit', 0)
            total_sum_of_debit_per_account += data.get('move_line_debit', 0)
            data_col += 1  # debit

            if data.get('move_line_credit', 0):
                sheet.write(data_row, data_col, data['move_line_credit'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_credit_per_account += data.get('move_line_credit', 0)
            total_sum_of_credit_per_account += data.get('move_line_credit', 0)
            data_col += 1  # credit

            if data_account_to_write and not last_data:
                total_ending_balance_per_account = 0

            if data.get('move_line_debit', 0) and not total_ending_balance_per_account:
                total_ending_balance_per_account += (beginning_balance + data.get('move_line_debit', 0))
            elif data.get('move_line_debit', 0) and total_ending_balance_per_account:
                total_ending_balance_per_account += data.get('move_line_debit', 0)
            elif data.get('move_line_credit', 0) and not total_ending_balance_per_account:
                total_ending_balance_per_account += (beginning_balance - data.get('move_line_credit', 0))
            elif data.get('move_line_credit', 0) and total_ending_balance_per_account:
                total_ending_balance_per_account -= data.get('move_line_credit', 0)

            if total_ending_balance_per_account:
                sheet.write(data_row, data_col, total_ending_balance_per_account, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_sum_of_ending_balance_per_account += total_ending_balance_per_account
            data_col += 1  # ending_balance

            sheet.write(data_row, data_col, data.get('partner_name', ''), style['table_normal_align_right'])
            data_col += 1  # customer_supplier

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # project_number

            sheet.write(data_row, data_col, data.get('purchase_order_name', ''), style['table_normal_align_right'])
            data_col += 1  # po_number

            sheet.write(data_row, data_col, data.get('move_payment_reference', ''), style['table_normal_align_right'])
            data_col += 1  # invoice_number

            move_date = data.get('move_date', '')
            if move_date:
                move_date = move_date.strftime('%d-%b-%y').capitalize()
            sheet.write(data_row, data_col, move_date, style['table_normal_align_right'])
            data_col += 1  # gl_date_invoice

            bill_type = data.get('move_bill_type', '')
            if bill_type:
                bill_type = bill_type.upper()
            sheet.write(data_row, data_col, bill_type, style['table_normal_align_right'])
            data_col += 1  # type

            sheet.write(data_row, data_col, data.get('move_mo_numbers_gen21', ''), style['table_normal_align_right'])
            data_col += 1  # mo_number

            sheet.write(data_row, data_col, data.get('move_voucher_number', ''), style['table_normal_align_right'])
            data_col += 1  # voucher_number

            sheet.write(data_row, data_col, move_date, style['table_normal_align_right'])
            data_col += 1  # gl_date_voucher

            sheet.write(data_row, data_col, data.get('currency_name', ''), style['table_normal_align_right'])
            data_col += 1  # currency_code

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # currency_type

            currency = self.env['res.currency'].browse(data.get('currency_id', []))
            sheet.write(data_row, data_col, currency.actual_rate if currency else '', style['table_normal_align_right'])
            data_col += 1  # currency_rate

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # valas

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # batch

            invoice_number = 'Invoice Number %s |' % data['move_payment_reference'] if data.get(
                'move_payment_reference', '') else ''
            supplier_number = 'Supplier Number %s |' % data['partner_no'] if data.get('partner_no', '') else ''
            supplier_name = 'Supplier Name %s |' % data['partner_name'] if data.get('partner_name', '') else ''
            voucher_number = 'Voucher Number %s |' % data['move_voucher_number'] if data.get('move_voucher_number', \
                                                                                             data.get(
                                                                                                 'move_payment_reference',
                                                                                                 '')) else ''
            description = 'Description %s |' % data['move_line_name'] if data.get('move_line_name', '') else ''
            description_line_journal = invoice_number + supplier_number \
                                       + supplier_name + voucher_number + description
            sheet.write(data_row, data_col, description_line_journal or '', style['table_normal_align_left'])
            data_col += 1  # description_line_journal

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # faktur_pajak

            sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1  # date_faktur

            if data_account_to_write:
                account_col = 0
                account_full_name = ''
                account_name = ''
                account_code = ''
                if data_account_to_write.get('account_name', ''):
                    account_name = data_account_to_write['account_name']
                if data_account_to_write.get('account_code', ''):
                    account_code = data_account_to_write['account_code']
                if account_name and account_code:
                    account_full_name = account_code + ' - ' + account_name
                elif account_name and not account_code:
                    account_full_name = account_name
                elif not account_name and account_code:
                    account_full_name = account_code
                sheet.write(account_row, account_col, account_full_name, style['table_bold_align_left'])
                account_col += 1

                empty_account_section_1 = 6
                empty_account_section_index = 0
                while empty_account_section_index <= empty_account_section_1:
                    sheet.write(account_row, account_col, '', style['table_normal_align_left'])  # Test
                    account_col += 1
                    empty_account_section_index += 1

                sheet.write(account_row, account_col, account_name, style['table_bold_align_left'])
                account_col += 1

                account_to_write_beginning_balance = self.get_account_beginning_balance(arguments, \
                                                                                        data_account_to_write.get(
                                                                                            'account_id', False))
                if account_to_write_beginning_balance:
                    sheet.write(account_row, account_col, \
                                account_to_write_beginning_balance, style['table_num_bold'])
                else:
                    sheet.write(account_row, account_col, 0, style['table_bold_align_right'])
                account_col += 1

                empty_account_section_1 = 19
                empty_account_section_index = 0
                while empty_account_section_index <= empty_account_section_1:
                    sheet.write(account_row, account_col, '', style['table_normal_align_left'])  # test2
                    account_col += 1
                    empty_account_section_index += 1

                account_row += count_data_per_account + 1
                subtotal_section_1 = 5
                subtotal_section_index = 0
                account_col = 0
                while subtotal_section_index <= subtotal_section_1:
                    sheet.write(account_row, account_col, '', style['table_normal_align_left'])
                    account_col += 1
                    subtotal_section_index += 1

                sheet.write(account_row, account_col, 'Subtotal :', style['table_bold_align_left_italic'])
                account_col += 1

                sheet.write(account_row, account_col, '', style['table_bold_align_left'])
                account_col += 1

                sheet.write(account_row, account_col, '', style['table_bold_align_left'])
                account_col += 1

                if account_to_write_beginning_balance:
                    sheet.write(account_row, account_col, account_to_write_beginning_balance, style['table_num_bold'])
                else:
                    sheet.write(account_row, account_col, 0, style['table_bold_align_right'])
                account_col += 1

                if total_sum_of_debit_per_account and not last_data:
                    total_sum_of_debit_per_account -= data.get('move_line_debit', 0)
                if total_sum_of_debit_per_account:
                    sheet.write(account_row, account_col, total_sum_of_debit_per_account, style['table_num_bold'])
                else:
                    sheet.write(account_row, account_col, 0, style['table_bold_align_right'])
                account_col += 1

                if total_sum_of_credit_per_account and not last_data:
                    total_sum_of_credit_per_account -= data.get('move_line_credit', 0)
                if total_sum_of_credit_per_account:
                    sheet.write(account_row, account_col, total_sum_of_credit_per_account, style['table_num_bold'])
                else:
                    sheet.write(account_row, account_col, 0, style['table_bold_align_right'])
                account_col += 1

                if last_data:
                    total_sum_of_ending_balance_per_account_to_write = \
                        total_sum_of_ending_balance_per_account

                if total_sum_of_ending_balance_per_account_to_write:
                    sheet.write(account_row, account_col, total_sum_of_ending_balance_per_account_to_write,
                                style['table_num_bold'])
                else:
                    sheet.write(account_row, account_col, 0, style['table_bold_align_right'])
                account_col += 1

                subtotal_section_2 = 16
                subtotal_section_index = 0
                while subtotal_section_index <= subtotal_section_2:
                    sheet.write(account_row, account_col, '', style['table_normal_align_left'])
                    account_col += 1
                    subtotal_section_index += 1

                account_row += 1
                count_data_per_account = 0

                if data.get('move_line_debit', 0):
                    total_sum_of_ending_balance_per_account = beginning_balance + data['move_line_debit']
                elif data.get('move_line_credit', 0):
                    total_sum_of_ending_balance_per_account = beginning_balance - data['move_line_credit']

                total_sum_of_debit_per_account = data.get('move_line_debit', 0)
                total_sum_of_credit_per_account = data.get('move_line_credit', 0)

                empty_row_section_1 = 1
                empty_row_section_index = 0
                while empty_row_section_index <= empty_row_section_1:
                    account_row += 1
                    empty_row_section_index += 1

            count_data_per_account += 1
            data_row += 1
            data_index += 1

    def get_account_move_line_data(self, arguments):
        results = []
        where_clause = self.get_account_move_line_where_clause(arguments)
        query = """
            SELECT 
                aml.id AS move_line_id,
                aml.date AS move_line_date,
                aml.name AS move_line_name,
                aml.debit AS move_line_debit,
                aml.credit AS move_line_credit,
                aa.id AS account_id,
                aa.name AS account_name,
                aa.code AS account_code,
                aaa.id AS analytic_account_id,
                aaa.name AS analytic_account_name,
                aaa.code AS analytic_account_code,
                ou.name AS operating_unit_name,
                ou.code AS operating_unit_code,
                aj.id AS journal_id,
                aj.name AS journal_name,
                aj.name AS journal_number,
                aj.code AS journal_code,
                aj.type AS journal_type,
                rp.id AS partner_id,
                rp.name AS partner_name,
                rp.partner_no AS partner_no,
                am.id AS move_id,
                am.payment_reference AS move_payment_reference,
                am.date AS move_date,
                am.bill_type AS move_bill_type,
                am.mo_numbers_gen21 AS move_mo_numbers_gen21,
                am.voucher_no AS move_voucher_number,
                po.id AS purchase_order_id,
                po.name AS purchase_order_name,
                pol.id AS purchase_order_line_id,
                pol.name AS purchase_order_line_name,
                rc.id AS currency_id,
                rc.name AS currency_name,
                rc.symbol AS currency_symbol
            FROM account_move_line aml 
            LEFT JOIN account_account aa ON aa.id = aml.account_id 
            LEFT JOIN account_analytic_account aaa ON aaa.id =  aml.analytic_account_id 
            LEFT JOIN operating_unit ou ON ou.id = aml.operating_unit_id
            LEFT JOIN account_journal aj ON aj.id = aml.journal_id
            LEFT JOIN res_partner rp ON rp.id = aml.partner_id
            LEFT JOIN account_move am ON am.id = aml.move_id
            LEFT JOIN purchase_order_line pol ON pol.id = aml.purchase_line_id
            LEFT JOIN purchase_order po ON po.id = pol.order_id
            LEFT JOIN res_currency rc ON rc.id = aml.currency_id
            %s
            ORDER BY
                aa.id ASC,
                aml.id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_account_move_line_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE aml.company_id = %s AND aml.parent_state = 'posted'
        """ % wizard.company_id.id

        if wizard.account_type == 'specific' and \
                wizard.account_ids and len(wizard.account_ids) > 1:
            account_ids = wizard.account_ids.ids
            where_clause += ' AND aa.id in {account_ids}'. \
                format(account_ids=tuple(account_ids))
        elif wizard.account_type == 'specific' and \
                wizard.account_ids and len(wizard.account_ids) == 1:
            account_id = wizard.account_ids[0].id
            where_clause += ' AND aa.id = {account_id}'. \
                format(account_id=account_id)

        if wizard.analytic_account_type == 'specific' and \
                wizard.analytic_account_ids and len(wizard.analytic_account_ids) > 1:
            analytic_account_ids = wizard.analytic_account_ids.ids
            where_clause += ' AND aaa.id in {analytic_account_ids}'. \
                format(analytic_account_ids=tuple(analytic_account_ids))
        elif wizard.analytic_account_type == 'specific' and \
                wizard.analytic_account_ids and len(wizard.analytic_account_ids) == 1:
            analytic_account_id = wizard.analytic_account_ids[0].id
            where_clause += ' AND aaa.id = {analytic_account_id}'. \
                format(analytic_account_id=analytic_account_id)

        start_date = wizard.start_date.strftime('%Y-%m-%d')
        if wizard.date_type == 'range_of_date' and wizard.start_date and wizard.end_date:
            end_date = wizard.end_date.strftime('%Y-%m-%d')
            where_clause += """
                AND aml.date >= '%s' AND aml.date <= '%s'
            """ % (start_date, end_date)
        elif wizard.date_type == 'current_date' and wizard.start_date:
            where_clause += " AND aml.date = '%s'" % start_date
        elif wizard.date_type == 'as_of_date' and wizard.start_date:
            where_clause += " AND aml.date <= '%s'" % start_date

        return where_clause

    def get_account_beginning_balance(self, arguments, account_id):
        where_clause = self.get_account_beginning_balance_where_clause(arguments, account_id)
        beginning_balance = 0
        if account_id:
            query = """
                SELECT 
                    sum(aml.balance) AS beginning_balance
                FROM account_account aa 
                LEFT JOIN account_move_line aml ON aml.account_id = aa.id
                LEFT JOIN account_analytic_account aaa ON aaa.id = aml.analytic_account_id
                %s
                GROUP BY aa.id

            """ % where_clause
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()
            if results:
                beginning_balance = results[0].get('beginning_balance', 0)

        return beginning_balance

    def get_account_beginning_balance_where_clause(self, arguments, account_id):
        wizard = arguments['wizard']
        where_clause = """
            WHERE aml.company_id = %s AND aml.parent_state = 'posted'
        """ % wizard.company_id.id

        if account_id:
            where_clause += ' AND aa.id = {account_id}'.format(account_id=account_id)

        if wizard.analytic_account_type == 'specific' and \
                wizard.analytic_account_ids and len(wizard.analytic_account_ids) > 1:
            analytic_account_ids = wizard.analytic_account_ids.ids
            where_clause += ' AND aaa.id in {analytic_account_ids}'. \
                format(analytic_account_ids=tuple(analytic_account_ids))
        elif wizard.analytic_account_type == 'specific' and \
                wizard.analytic_account_ids and len(wizard.analytic_account_ids) == 1:
            analytic_account_id = wizard.analytic_account_ids[0].id
            where_clause += ' AND aaa.id = {analytic_account_id}'. \
                format(analytic_account_id=analytic_account_id)

        if wizard.start_date:
            start_date = wizard.start_date.strftime('%Y-%m-%d')
            where_clause += " AND aml.date < '%s'" % start_date

        return where_clause
