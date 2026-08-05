import pytz
from datetime import datetime
from odoo import models, _


class ARUnappliedReceiptReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.ar_unapplied_receipt_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet(wizard.company_id.name)
        arguments = {
            'sheet': sheet,
            'workbook': workbook,
            'wizard': wizard,
        }
        sheet.hide_gridlines(2)
        self.set_column_width(sheet)
        self.set_header_data(arguments)
        self.set_table_header_data(arguments)
        self.set_table_body_data(arguments)

    def set_column_width(self, sheet):
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 35)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 35)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 5)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 15)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])
        sheet.write('A1: A1', 'AR Unapplied Receipt Report', style['normal_bold'])

        start_date = wizard.start_date.strftime('%d %b %Y')
        if wizard.date_type and wizard.date_type == 'range_of_date':
            start_date = wizard.start_date.strftime('%b-%y')
            end_date = wizard.end_date.strftime('%b-%y')
            sheet.merge_range('A2:I2', 'Periode: %s s/d %s' % (start_date, end_date), style['normal_bold'])
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            sheet.merge_range('A2:I2', 'Periode: s/d %s' % (start_date), style['normal_bold'])
        elif wizard.date_type and wizard.date_type == 'current_date':
            sheet.merge_range('A2:I2', 'Periode: %s' % (start_date), style['normal_bold'])

    def get_workbook_style(self, workbook):
        return {
            'normal_bold': workbook.add_format({'bold': True}),
            'table_header': workbook.add_format \
                ({'bold': True, 'align': 'center', 'border': 1}),
            'table_normal_align_right': workbook.add_format({'align': 'right', 'border': 1}),
            'table_normal_align_left': workbook.add_format({'align': 'left', 'border': 1}),
            'table_normal_num': workbook.add_format \
                ({'align': 'right', 'num_format': '#,##', 'border': 1}),
            'table_bold_align_left': workbook.add_format({'align': 'left', 'border': 1, 'bold': 1}),
            'table_bold_align_right': workbook.add_format({'align': 'right', 'border': 1, 'bold': 1}),
            'table_num_bold': workbook.add_format \
                ({'align': 'right', 'num_format': '#,##', 'border': 1, 'bold': 1}),
        }

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])
        header_list = ['Company', 'Account', 'Customer Name', \
                       'Customer', 'Gl Date', 'Batch Source', 'Batch', 'Receipt Method', \
                       'Receipt Number', 'Receipt Date', 'Unid', 'Status', 'On Account Amount', \
                       'Unapplied Amount', 'Claim Amount']

        header_row = 4
        header_col = 0
        for header in header_list:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])
        body_row = 5
        receipts = self.get_ar_unapplied_receipt_data_by_query(arguments)
        total_on_account_amount, total_claim_amount, total_remaining_amount = 0, 0, 0
        for receipt in receipts:
            remaining_amount = self.get_receipt_remaining_amount(receipt)
            if not remaining_amount or remaining_amount <= 0:
                continue

            body_col = 0
            sheet.write(body_row, body_col, \
                        receipt.company_id.company_code or '', style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.applied_partner_account.code or '', style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.misc_partner_id.alias_name or '', style['table_normal_align_left'])
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.misc_partner_id.partner_no or '', style['table_normal_align_right'])
            body_col += 1

            gl_date = ''
            if receipt.date:
                gl_date = receipt.date.strftime('%d-%b-%y')
            sheet.write(body_row, body_col, gl_date, style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, "", style['table_normal_align_right'])  # batch_source
            body_col += 1

            sheet.write(body_row, body_col, "", style['table_normal_align_right'])  # batch
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.journal_id.name or '', style['table_normal_align_left'])
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.receipt_number or '', style['table_normal_align_left'])
            body_col += 1

            sheet.write(body_row, body_col, gl_date, style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, '', style['table_normal_align_right'])  # unid
            body_col += 1

            if receipt.is_matched:
                sheet.write(body_row, body_col, "CLEARED", style['table_normal_align_left'])
            else:
                sheet.write(body_row, body_col, "NOT CLEARED", style['table_normal_align_left'])
            body_col += 1

            on_account_amount = 0
            sheet.write(body_row, body_col, on_account_amount, style['table_normal_align_right'])
            total_on_account_amount += on_account_amount
            body_col += 1

            if remaining_amount:
                sheet.write(body_row, body_col, remaining_amount, style['table_normal_num'])
            else:
                sheet.write(body_row, body_col, 0, style['table_normal_align_right'])
            total_remaining_amount += remaining_amount
            body_col += 1

            claim_amount = 0
            sheet.write(body_row, body_col, claim_amount, style['table_normal_align_right'])
            total_claim_amount += claim_amount

            body_row += 1

        total_col = 0
        sheet.merge_range(body_row, total_col, body_row, total_col + 11, 'Grand Total:', style['table_bold_align_left'])
        total_col += 12

        if total_on_account_amount:
            sheet.write(body_row, total_col, total_on_account_amount, style['table_num_bold'])
        else:
            sheet.write(body_row, total_col, total_on_account_amount, style['table_bold_align_right'])
        total_col += 1

        if total_remaining_amount:
            sheet.write(body_row, total_col, total_remaining_amount, style['table_num_bold'])
        else:
            sheet.write(body_row, total_col, total_remaining_amount, style['table_bold_align_right'])
        total_col += 1

        if total_claim_amount:
            sheet.write(body_row, total_col, total_claim_amount, style['table_num_bold'])
        else:
            sheet.write(body_row, total_col, total_claim_amount, style['table_bold_align_right'])

    def get_ar_unapplied_receipt_data_by_query(self, arguments):
        unapplied_receipt_datas = self.env['miscellaneous.miscellaneous']
        where_clause = self.get_ar_unapplied_receipt_data_where_clause(arguments)
        query = """
            SELECT
                mm.id
            FROM miscellaneous_miscellaneous mm
            LEFT JOIN receipt_type rt on rt.id = mm.receipt_type_id
            LEFT JOIN account_move am on am.id = mm.move_id
            %s
            ORDER BY 
                am.date ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.fetchall()
        if results and isinstance(results, list):
            unapplied_receipt_datas = unapplied_receipt_datas.sudo().browse([data[0] for data in results])

        return unapplied_receipt_datas

    def get_ar_unapplied_receipt_data_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE mm.company_id = %s
            AND rt.name = 'Receipt Standart'
        """ % wizard.company_id.id
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

    def get_ar_unapplied_receipt_data(self, arguments):
        wizard = arguments['wizard']
        if wizard.date_type and wizard.date_type == 'range_of_date':
            receipts = self.sudo().env['miscellaneous.miscellaneous'].search([
                ('date', '>=', wizard.start_date),
                ('date', '<=', wizard.end_date),
                ('receipt_type_id.name', '=', 'Receipt Standart'),
                ('company_id', '=', wizard.company_id.id),
            ], order="id desc")
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            receipts = self.sudo().env['miscellaneous.miscellaneous'].search([
                ('date', '<=', wizard.start_date),
                ('receipt_type_id.name', '=', 'Receipt Standart'),
                ('company_id', '=', wizard.company_id.id),
            ], order="id desc")
        elif wizard.date_type and wizard.date_type == 'current_date':
            receipts = self.sudo().env['miscellaneous.miscellaneous'].search([
                ('date', '=', wizard.start_date),
                ('receipt_type_id.name', '=', 'Receipt Standart'),
                ('company_id', '=', wizard.company_id.id),
            ], order="id desc")

        return receipts

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
