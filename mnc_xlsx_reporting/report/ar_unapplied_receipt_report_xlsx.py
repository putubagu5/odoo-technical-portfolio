import pytz
from datetime import datetime
from odoo import models, _


class ARUnappliedReceiptReportXLSX(models.AbstractModel):
    _name = 'report.mnc_xlsx_reporting.ar_unapplied_receipt_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet("MNC3TV_AR___Unapplied_Receipts_")
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
        sheet.set_column('O:O', 10)

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
                       'Receipt Number', 'Receipt Date', 'Unid', 'Status', 'On Account Amt', \
                       'Unapplied Amt', 'Claim Amt']

        header_row = 4
        header_col = 0
        for header in header_list:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])
        body_row = 5
        receipts = self.get_ar_unapplied_receipt_data(wizard)
        total_on_account_amount, total_claim_amount, total_receipt_amount = 0, 0, 0
        for receipt in receipts:
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

            sheet.write(body_row, body_col, "", style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, "", style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.journal_id.name or '', style['table_normal_align_left'])
            body_col += 1

            sheet.write(body_row, body_col, \
                        receipt.receipt_number or '', style['table_normal_align_left'])
            body_col += 1

            sheet.write(body_row, body_col, gl_date, style['table_normal_align_right'])
            body_col += 1

            sheet.write(body_row, body_col, '', style['table_normal_align_right'])
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

            if receipt.amount:
                sheet.write(body_row, body_col, receipt.amount, style['table_normal_num'])
            else:
                sheet.write(body_row, body_col, receipt.amount, style['table_normal_align_right'])
            total_receipt_amount += receipt.amount
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

        if total_receipt_amount:
            sheet.write(body_row, total_col, total_receipt_amount, style['table_num_bold'])
        else:
            sheet.write(body_row, total_col, total_receipt_amount, style['table_bold_align_right'])
        total_col += 1

        if total_claim_amount:
            sheet.write(body_row, total_col, total_claim_amount, style['table_num_bold'])
        else:
            sheet.write(body_row, total_col, total_claim_amount, style['table_bold_align_right'])

    def get_ar_unapplied_receipt_data_by_query(self, date):
        query = """
            SELECT
                rc.company_code as company,
                coa.code as account,
                rp.alias_name as customer_name,
                rp.partner_no as customer,
                am.date as gl_date,
                aj.name as receipt_method,
                mm.receipt_number as receipt_number,
                am.date as date,
                CASE
                    WHEN mm.is_matched = True THEN 'CLEARED'
                    ELSE 'NOT CLEARED'
                END,
                mm.amount as amount
            FROM miscellaneous_miscellaneous mm
            LEFT JOIN res_company rc on rc.id = mm.company_id
            LEFT JOIN account_account coa on coa.id = mm.applied_partner_account
            LEFT JOIN res_partner rp on rp.id = mm.misc_partner_id
            LEFT JOIN account_journal aj on aj.id = mm.journal_id
            LEFT JOIN account_move am on am.id = mm.move_id
            WHERE
                mm.company_id = %s
                and mm.journal_group = 'merge'
                and am.date = '%s'
        """ % (self.env.user.company_id.id, date.strftime('%Y-%m-%d'))
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_ar_unapplied_receipt_data(self, wizard):
        if wizard.date_type and wizard.date_type == 'range_of_date':
            receipts = self.sudo().env['miscellaneous.miscellaneous'].search([
                ('date', '>=', wizard.start_date),
                ('date', '<=', wizard.end_date),
                ('journal_group', '=', 'merge'),
                ('company_id', 'in', wizard.company_ids.ids),
            ], order="id desc")
        elif wizard.date_type and wizard.date_type == 'as_of_date':
            receipts = self.sudo().env['miscellaneous.miscellaneous'].search([
                ('date', '<=', wizard.start_date),
                ('journal_group', '=', 'merge'),
                ('company_id', 'in', wizard.company_ids.ids),
            ], order="id desc")
        elif wizard.date_type and wizard.date_type == 'current_date':
            receipts = self.sudo().env['miscellaneous.miscellaneous'].search([
                ('date', '=', wizard.start_date),
                ('journal_group', '=', 'merge'),
                ('company_id', 'in', wizard.company_ids.ids),
            ], order="id desc")

        return receipts
