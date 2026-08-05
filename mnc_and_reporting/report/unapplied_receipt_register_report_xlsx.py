import pytz
from datetime import datetime, date
from odoo import models, _


class UnappliedReceiptRegisterReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.unapplied_receipt_register_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet( \
            '%s Unapplied Receipts Register_Details' % wizard.company_id.name)
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
        sheet.set_column('A:A', 3)
        sheet.set_column('B:B', 50)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 40)
        sheet.set_column('G:G', 30)
        sheet.set_column('H:H', 30)
        sheet.set_column('I:I', 30)
        sheet.set_column('I:I', 30)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:K', 30)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])
        header_row = 0
        sheet.write(header_row, 0, \
                    '%s Unapplied Receipts Register' % wizard.company_id.name, style['header_style_align_left'])
        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')
        sheet.write(header_row, 10, 'Print date: %s' % print_date, style['print_date_format'])
        header_row += 1

        sheet.write(header_row, 0, 'Format Option: %s' % wizard.format_option.capitalize(), \
                    style['header_style_align_left'])
        sheet.write(header_row, 10, 'User: %s' % self.env.user.name, style['print_date_format'])
        header_row += 1

        start_date = wizard.start_date.strftime('%d%b%Y').upper()
        if wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%d%b%Y').upper()
            sheet.write(header_row, 0, \
                        'GL Date From: %s to %s' % (start_date, end_date), style['header_style_align_left'])
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            sheet.write(header_row, 0, \
                        'GL Date Before:  %s' % (start_date), style['header_style_align_left'])
        elif wizard.date_type and wizard.date_type == 'current_date':
            sheet.write(header_row, 0, \
                        'GL Date From: %s' % (start_date), style['header_style_align_left'])
        header_row += 1

        currency = ""
        if wizard.currency_type == 'specific' and wizard.currency_ids:
            currency = ", ".join(currency.name for currency in wizard.currency_ids)
        elif wizard.currency_type == 'all':
            currency = "All"
        sheet.write(header_row, 0, 'Currency: %s' % currency, style['header_style_align_left'])
        header_row += 1

        unapplied_account = self.get_unapplied_account(arguments)
        sheet.write(header_row, 0, 'Account: %s' % unapplied_account.display_name or '', \
                    style['header_style_align_left'])

    def get_unapplied_account(self, arguments):
        wizard = arguments['wizard']
        domain = [
            ('code', '=', '1151501'),
            ('company_id', '=', wizard.company_id.id),
        ]
        unapplied_account = self.env['account.account']. \
            sudo().search(domain, limit=1, order='id desc')

        if not unapplied_account:
            unapplied_account = self.env['account.account']. \
                sudo().search([('code', '=', '1151501')], limit=1, order='id desc')

        return unapplied_account

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'No', 'Customer Name / Customer Number', 'GL Date',
            'Batch Source', 'Batch Number', 'Receipt Method',
            'Receipt Number', 'Receipt Date', 'On Account Amount',
            'Unapplied Amount', 'Claim Amount',
        ]

        header_row = 7
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        ar_receipt_datas = self.get_receipt_data(arguments)
        if not ar_receipt_datas:
            return

        cust_row, data_row = 8, 8
        index = 0
        used_customer_ids = []
        grand_total_remaining_amount = 0;
        grand_total_claim_amount = 0
        for customer_id, data_per_customer in ar_receipt_datas.items():
            customer_id = self.env['res.partner'].browse(customer_id)
            customer_name_and_number = '%s, %s' % (customer_id.name, customer_id.partner_no)
            total_claim_amount = 0;
            total_remaining_amount = 0

            count_receipt_data_per_customer = len(data_per_customer)

            if not used_customer_ids or (customer_id and used_customer_ids \
                                         and customer_id not in used_customer_ids):
                used_customer_ids.append(customer_id)
                index += 1

            for receipt in data_per_customer:
                remaining_amount = self.sudo().get_receipt_remaining_amount(receipt)
                receipt_col = 2
                gl_date = receipt.date.strftime('%d-%b-%y').upper()
                sheet.write(data_row, receipt_col, gl_date or '', style['table_normal_align_left'])
                receipt_col += 1

                sheet.write(data_row, receipt_col, '', style['table_normal_align_left'])
                receipt_col += 1

                sheet.write(data_row, receipt_col, receipt.name or '', style['table_normal_align_left'])
                receipt_col += 1

                sheet.write(data_row, receipt_col, receipt.journal_id.name or '', style['table_normal_align_left'])
                receipt_col += 1

                sheet.write(data_row, receipt_col, receipt.receipt_number or '', style['table_normal_align_left'])
                receipt_col += 1

                sheet.write(data_row, receipt_col, gl_date or '', style['table_normal_align_left'])
                receipt_col += 1

                # sheet.write(data_row, receipt_col, receipt.partner_bank_id.display_name or '', style['table_normal_align_left'])
                sheet.write(data_row, receipt_col, '', style['table_normal_align_left'])
                receipt_col += 1

                if remaining_amount:
                    sheet.write(data_row, receipt_col, remaining_amount, style['table_num'])
                else:
                    sheet.write(data_row, receipt_col, 0, style['table_normal_align_right'])
                total_remaining_amount += remaining_amount
                receipt_col += 1

                claim_amount = 0
                if claim_amount:
                    sheet.write(data_row, receipt_col, claim_amount, style['table_num'])
                else:
                    sheet.write(data_row, receipt_col, \
                                claim_amount, style['table_normal_align_right'])
                total_claim_amount += claim_amount

                data_row += 1

            cust_col = 0
            sheet.merge_range(cust_row, cust_col, cust_row + count_receipt_data_per_customer,
                              cust_col, index, style['table_normal_align_right'])
            cust_col += 1

            sheet.merge_range(cust_row, cust_col, cust_row + count_receipt_data_per_customer,
                              cust_col, customer_name_and_number, style['table_bold_align_left'])
            cust_col += 1

            sheet.merge_range(cust_row + count_receipt_data_per_customer, \
                              cust_col, cust_row + count_receipt_data_per_customer, \
                              cust_col + 5, 'Sub total Per %s' % customer_name_and_number, \
                              style['table_bold_align_right'])
            cust_col += 6

            sheet.write(cust_row + count_receipt_data_per_customer, \
                        cust_col, "", style['table_bold_align_right'])
            cust_col += 1

            if total_remaining_amount:
                sheet.write(cust_row + count_receipt_data_per_customer, \
                            cust_col, total_remaining_amount, style['table_num_bold'])
            else:
                sheet.write(cust_row + count_receipt_data_per_customer, \
                            cust_col, total_remaining_amount, style['table_bold_align_right'])
            cust_col += 1

            if total_claim_amount:
                sheet.write(cust_row + count_receipt_data_per_customer, \
                            cust_col, total_claim_amount, style['table_num_bold'])
            else:
                sheet.write(cust_row + count_receipt_data_per_customer, \
                            cust_col, total_claim_amount, style['table_bold_align_right'])

            data_row += 1
            cust_row += count_receipt_data_per_customer + 1

            grand_total_remaining_amount += total_remaining_amount
            grand_total_claim_amount += total_claim_amount

        grand_total_row = data_row + 2
        grand_total_col = 0
        unapplied_account = self.get_unapplied_account(arguments)
        sheet.merge_range(grand_total_row, grand_total_col, \
                          grand_total_row, grand_total_col + 7, \
                          'Sub Total Per {0}'.format(unapplied_account[0].code), style['grand_total'])
        grand_total_col += 8

        sheet.write(grand_total_row, grand_total_col, \
                    "", style['bold_align_right'])
        grand_total_col += 1

        if grand_total_remaining_amount:
            sheet.write(grand_total_row, grand_total_col, \
                        grand_total_remaining_amount, style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, \
                        grand_total_remaining_amount, style['bold_align_right'])
        grand_total_col += 1

        if grand_total_claim_amount:
            sheet.write(grand_total_row, grand_total_col, \
                        grand_total_claim_amount, style['num_bold'])
        else:
            sheet.write(grand_total_row, grand_total_col, \
                        grand_total_claim_amount, style['bold_align_right'])

    def get_receipt_data(self, arguments):
        receipts = self.get_receipt_data_with_orm(arguments)
        list_of_customer_ids = receipts.mapped('misc_partner_id').ids
        all_data = {customer_id: {} for customer_id in list_of_customer_ids}
        for customer_id in list_of_customer_ids:
            data_receipt_per_customer = receipts.filtered(
                lambda receipt: receipt.misc_partner_id.id == customer_id
            )
            all_data[customer_id] = data_receipt_per_customer

        return all_data

    def get_receipt_data_with_orm(self, arguments):
        wizard = arguments['wizard']
        receipts = self.env['miscellaneous.miscellaneous']
        unapplied_account = self.get_unapplied_account(arguments)
        domain = [
            ('receipt_type_id.name', '=', 'Receipt Standart'),
            ('applied_partner_account', '=', unapplied_account.id),
            ('company_id', '=', wizard.company_id.id),
        ]
        if wizard.date_type and wizard.date_type == 'range_of_date':
            domain += [('date', '>=', wizard.start_date), ('date', '<=', wizard.end_date)]
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            domain += [('date', '<=', wizard.start_date)]
        elif wizard.date_type and wizard.date_type == 'current_date':
            domain += [('date', '=', wizard.start_date)]

        if wizard.currency_type == 'specific':
            domain += [('currency_id', 'in', wizard.currency_ids.ids)]

        receipts = self.env['miscellaneous.miscellaneous']. \
            sudo().search(domain, order='date ASC')

        unapplied_receipts = self.sudo().env['miscellaneous.miscellaneous']
        for receipt in receipts:
            remaining_amount = self.sudo().get_receipt_remaining_amount(receipt)
            if remaining_amount and remaining_amount > 0:
                unapplied_receipts |= receipt

        return unapplied_receipts

    def get_receipt_data_by_query(self, arguments):
        results = []
        where_clause = self.get_receipt_where_clause(arguments)
        query = """
            SELECT
                rp.id as customer_id,
                rp.name as customer_name,
                rp.partner_no as customer_number,
                mm.id as receipt_id
            FROM miscellaneous_miscellaneous mm
            LEFT JOIN res_partner rp on rp.id = mm.misc_partner_id
            %s
            ORDER BY rp.name ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_receipt_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE mm.company_id = %s
            AND mm.journal_group = 'merge'
        """ % wizard.company_id.id

        unapplied_account = self.get_unapplied_account(arguments)
        where_clause += " AND mm.applied_partner_account = %s" % unapplied_account.id

        if wizard.currency_type == 'specific' \
                and wizard.currency_ids and len(wizard.currency_ids) == 1:
            where_clause += " AND mm.currency_id = %s" % wizard.currency_ids.id
        elif wizard.currency_type == 'specific' \
                and wizard.currency_ids and len(wizard.currency_ids) > 1:
            where_clause += " AND mm.currency_id in {0}".format(tuple(wizard.currency_ids.ids))

        return where_clause

    def filter_receipt_by_date(self, data, arguments):
        wizard = arguments['wizard']
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

        return data

    def get_receipt_remaining_amount(self, receipt):
        total_amount_applied = 0
        remaining_amount = 0
        if receipt.amount:
            remaining_amount = receipt.amount

        for invoice in receipt.invoice_ids:
            reverse = self.env['account.move'].search([('reversed_entry_id', '=', invoice.move_id.id)])
            if invoice.move_id.state and invoice.transaction_type \
                    and invoice.move_id.state == 'posted' \
                    and invoice.transaction_type == 'apply' and not reverse:
                total_amount_applied += invoice.applied_amount

        remaining_amount = receipt.amount - \
                           total_amount_applied

        return remaining_amount
