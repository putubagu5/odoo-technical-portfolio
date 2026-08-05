import pytz
from datetime import datetime, date
from odoo import models, _


class StatementAccountDescriptionReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.statement_account_desc_report_xlsx'
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
            'title_style_align_center': workbook.add_format \
                ({'bold': True, 'font_size': 12, 'align': 'center'}),
            'title_style_align_left': workbook.add_format \
                ({'bold': True, 'font_size': 12, 'align': 'left'}),
            'title_style_align_right': workbook.add_format \
                ({'bold': True, 'font_size': 12, 'align': 'right'}),
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
                ({'valign': 'top', 'font_size': 11,'align': 'left', 'border': 1}),
            'table_normal_align_right': workbook.add_format \
                ({'valign': 'top', 'font_size': 11,'align': 'right', 'border': 1}),
            'table_num': workbook.add_format \
                ({'valign': 'top', 'align': 'right','num_format': '#,##', 'border': 1}),
            'table_num_bold': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1}),
            'table_num_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'align': 'right','num_format': '#,##', 'border': 1, 'bg_color': 'yellow'}),
            'table_num_bold_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1, 'bg_color': 'yellow'}),
            'table_bold_align_left_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'left', 'border': 1, 'bg_color': 'yellow'}),
            'table_bold_align_right_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'border': 1, 'bg_color': 'yellow'}),
            'table_normal_align_left_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'font_size': 11,'align': 'left', 'border': 1, 'bg_color': 'yellow'}),
            'table_normal_align_right_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'font_size': 11,'align': 'right', 'border': 1, 'bg_color': 'yellow'}),
        }

    def set_column_width(self, sheet):
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 40)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 40)
        sheet.set_column('F:F', 40)
        sheet.set_column('G:G', 40)
        sheet.set_column('H:H', 40)
        sheet.set_column('I:I', 40)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 40)
        sheet.set_column('L:L', 40)
        sheet.set_column('M:M', 40)
        sheet.set_column('N:N', 40)
        sheet.set_column('O:O', 40)
        sheet.set_column('P:P', 40)
        sheet.set_column('Q:Q', 40)
        sheet.set_column('R:R', 40)
        sheet.set_column('S:S', 40)
        sheet.set_column('T:T', 40)
        sheet.set_column('U:U', 40)
        sheet.set_column('V:V', 40)
        sheet.set_column('W:W', 40)


    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        sheet.write(header_row, 0, 
                    'STATEMENT OF ACCOUNT BY Description REPORT', style['title_style_align_left'])
        header_row += 1

        customer = ''
        if wizard.customer_type == 'specific' and wizard.customer_ids:
            customer = ", ".join('{0}'.format(customer.name) \
                for customer in wizard.customer_ids)
        elif wizard.customer_type == 'all':
            customer = "All"
        sheet.write(header_row, 0, 'Customer Name: %s' % customer, style['header_style_align_left'])
        header_row += 1
        
        period = ''
        start_date = wizard.start_date.strftime('%b-%y').capitalize()
        if wizard.date_type and wizard.date_type == 'as_of_date':
            period = 'PERIODE : S/D {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'current_date':
            period = 'DATE : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%b-%y').capitalize()
            period = 'PERIODE : {start_date} S/D {end_date}'.format(start_date=start_date, end_date=end_date)
        sheet.write(header_row, 0, period, style['title_style_align_left'])
        header_row += 1

        currency = ''
        if wizard.currency_type == 'specific' and wizard.currency_ids:
            currency = ", ".join('{0}'.format(item.currency) \
                for item in wizard.currency_ids)
        elif wizard.currency_type == 'all':
            currency = "All"
        sheet.write(header_row, 0, 'KODE ITEM: %s' % currency, style['header_style_align_left'])

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'CUSTOMER NUMBER', 'CUSTOMER NAME', 'INVOICE NUMBER', 'INVOICE DATE', 'GL DATE', 'REFF MUTASI',
            'BRAND', 'STASIUN', 'ADVERTISER', 'INVOICE AMOUNT', 'UMUR PIUTANG', 'RECEIPT/CN-DN NUMBER',
            'NOTE', 'RECEIPT/CN-DN DATE', 'APPLY DATE', 'CLEARED DATE', 'RECEIPT DUE DATE',
            'APPLIED AMOUNT', 'OUTSTANDING AMOUNT'
        ]

        header_row = 5
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

        data_index = 0
        data_row = 6
        total_invoice_amount = 0
        total_amount_residual = 0
        total_applied_amount = 0
        looped_move_ids = []
        for data in applied_invoices_data:
            write_move_data = False
            if not looped_move_ids and data.get('move_id', False):
                write_move_data = True
                looped_move_ids.append(data['move_id'])
            elif looped_move_ids and data.get('move_id', False) \
                    and data['move_id'] not in looped_move_ids \
                    and data_index:
                looped_move_ids.append(data['move_id'])
                write_move_data = True

            data_col = 0
            if write_move_data:
                sheet.write(data_row, data_col, data.get('partner_no', ''), style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            if write_move_data:
                sheet.write(data_row, data_col, data.get('partner_name', ''), style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            if write_move_data:
                sheet.write(data_row, data_col, data.get('move_name', ''), style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1
            
            move_date = data.get('move_date', '')
            if move_date:
                move_date = move_date.strftime('%d-%b-%y')
            if write_move_data:
                sheet.write(data_row, data_col, move_date, style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            if write_move_data:
                sheet.write(data_row, data_col, move_date, style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            # sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            # data_col += 1

            if write_move_data:
                sheet.write(data_row, data_col, data.get('move_ref', ''), style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            if write_move_data:
                sheet.write(data_row, data_col, data.get('move_product_gen21', ''), style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_left'])  # stasiun
            data_col += 1

            if write_move_data:
                sheet.write(data_row, data_col, data.get('move_advertiser_gen21', ''), style['table_normal_align_left'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            if data.get('applied_move_amount_total', 0):
                sheet.write(data_row, data_col, data['applied_move_amount_total'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_invoice_amount += data.get('applied_move_amount_total', 0)
            data_col += 1

            age = ''
            current_date = date.today()
            if data.get('move_date', 0) and current_date > data['move_date']:
                age = current_date - data.get('move_date', 0)
                age = age.days
            sheet.write(data_row, data_col, age, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('applied_move_name', ''), style['table_normal_align_left'])
            data_col += 1
            
            applied_move_payment_state = ''
            if data.get('applied_move_payment_state', ''):
                move_obj = self.env['account.move']
                move_payment_state_fields = dict(move_obj._fields['payment_state'].selection)
                applied_move_payment_state = move_payment_state_fields.get(data['applied_move_payment_state'])
                applied_move_payment_state = applied_move_payment_state.capitalize()
            sheet.write(data_row, data_col, applied_move_payment_state, style['table_normal_align_left'])
            data_col += 1

            applied_move_date = data.get('applied_move_date', '')
            if applied_move_date:
                applied_move_date = applied_move_date.strftime('%d-%b-%y')
            sheet.write(data_row, data_col, applied_move_date, style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, applied_move_date, style['table_normal_align_left'])
            data_col += 1

            bank_statement_line_date = ''
            bank_statement_line_record = self.env['account.bank.statement.line'].\
                browse(data.get('bank_statement_line_id', []))
            if bank_statement_line_record and bank_statement_line_record.is_matched:
                bank_statement_line_date = bank_statement_line_record.statement_id.date
                bank_statement_line_date = bank_statement_line_date.strftime('%d-%b-%y')
            sheet.write(data_row, data_col, bank_statement_line_date, style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_left'])  # receipt_due_date
            data_col += 1

            applied_amount = 0
            applied_move_record = self.env['account.move'].browse(data.get('applied_move_id', []))
            if applied_move_record:
                applied_amount = sum(applied_move_record.mapped('applied_misc_ids').\
                                     mapped('applied_amount'))
            if applied_amount:
                sheet.write(data_row, data_col, applied_amount, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_applied_amount += applied_amount
            data_col += 1
            
            if data.get('applied_move_amount_residual', 0):
                sheet.write(data_row, data_col, data['applied_move_amount_residual'], style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            total_amount_residual += data.get('applied_move_amount_residual', 0)
            data_col += 1

            data_row += 1
            data_index += 1

    def get_applied_invoices_by_query(self, arguments):
        results = []
        where_clause = self.get_applied_invoices_where_clause(arguments)
        query = """
            SELECT
                am.id AS move_id,
                am.name AS move_name,
                am.payment_reference AS move_payment_reference,
                am.invoice_date AS move_invoice_date,
                am.invoice_payment_term_id AS move_invoice_payment_term_id,
                am.ref AS move_ref,
                am.po_numbers_gen21 AS move_po_numbers_gen21,
                am.mo_numbers_gen21 AS move_mo_numbers_gen21,
                am.product_gen21 AS move_product_gen21,
                am.advertiser_gen21 AS move_advertiser_gen21,
                am.date AS move_date,
                am.amount_total AS move_amount_total,
                am.amount_residual AS move_amount_residual,
                ai.invoice_id AS applied_move_id,
                am2.name AS applied_move_name,
                am2.amount_total AS applied_move_amount_total,
                am2.amount_residual AS applied_move_amount_residual,
                am2.date AS applied_move_date,
                am2.payment_state AS applied_move_payment_state,
                apt.name AS payment_term_name,
                absl.id AS bank_statement_line_id,
                rp.name AS partner_name,
                rp.id AS partner_id,
                rp.partner_no AS partner_no
            FROM applied_invoices ai
            LEFT JOIN miscellaneous_miscellaneous mm ON mm.id = ai.misc_id
            LEFT JOIN account_move am ON am.id = mm.move_id
            LEFT JOIN account_move am2 ON am2.id = ai.invoice_id
            LEFT JOIN account_payment_term apt ON apt.id = am.invoice_payment_term_id
            LEFT JOIN account_bank_statement_line absl ON absl.move_id = am2.id
            LEFT JOIN account_payment ap ON ap.move_id = am2.id
            LEFT JOIN res_partner rp ON rp.id = am.partner_id
            %s
            ORDER BY
                am.date ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_applied_invoices_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE 
                am.company_id = %s
                AND am.state = 'posted'
        """ % wizard.company_id.id

        if wizard.customer_type == 'specific' and \
                wizard.customer_ids and len(wizard.customer_ids) > 1:
            customer_ids = wizard.customer_ids.ids
            where_clause += ' AND rp.id in {customer_ids}'.\
                format(customer_ids=tuple(customer_ids))
        elif wizard.customer_type == 'specific' and \
                wizard.customer_ids and len(wizard.customer_ids) == 1:
            customer_id = wizard.customer_ids[0].id
            where_clause += ' AND rp.id = {customer_id}'.\
                format(customer_id=customer_id)

        if wizard.currency_type == 'specific' \
                and wizard.currency_ids and len(wizard.currency_ids) == 1:
            where_clause += " AND am.currency_id = %s" % wizard.currency_ids.id
        elif wizard.currency_type == 'specific' \
                and wizard.currency_ids and len(wizard.currency_ids) > 1:
            where_clause += " AND am.currency_id in {0}".format(tuple(wizard.currency_ids.ids))

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