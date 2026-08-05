import pytz
from datetime import datetime, date
from odoo import models, _


class BudgetVSRealizaitonReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.budget_vs_realization_report_xlsx'
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
                ({'valign': 'top', 'font_size': 11, 'align': 'left', 'border': 1}),
            'table_normal_align_right': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'right', 'border': 1}),
            'table_num': workbook.add_format \
                ({'valign': 'top', 'align': 'right', 'num_format': '#,##', 'border': 1}),
            'table_num_bold': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1}),
            'table_num_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'align': 'right', 'num_format': '#,##', 'border': 1, 'bg_color': 'yellow'}),
            'table_num_bold_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'num_format': '#,##', 'border': 1,
                  'bg_color': 'yellow'}),
            'table_bold_align_left_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'left', 'border': 1, 'bg_color': 'yellow'}),
            'table_bold_align_right_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'bold': True, 'align': 'right', 'border': 1, 'bg_color': 'yellow'}),
            'table_normal_align_left_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'left', 'border': 1, 'bg_color': 'yellow'}),
            'table_normal_align_right_bg_yellow': workbook.add_format \
                ({'valign': 'top', 'font_size': 11, 'align': 'right', 'border': 1, 'bg_color': 'yellow'}),
        }

    def set_column_width(self, sheet):
        sheet.set_column('A:A', 50)
        sheet.set_column('B:B', 50)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 50)
        sheet.set_column('F:F', 40)
        sheet.set_column('G:G', 40)
        sheet.set_column('H:H', 40)
        sheet.set_column('I:I', 50)
        sheet.set_column('J:J', 50)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 50)
        sheet.set_column('M:M', 30)
        sheet.set_column('N:N', 50)
        sheet.set_column('O:O', 30)
        sheet.set_column('P:P', 30)
        sheet.set_column('Q:Q', 30)
        sheet.set_column('R:R', 30)
        sheet.set_column('S:S', 50)
        sheet.set_column('T:T', 30)
        sheet.set_column('U:U', 30)
        sheet.set_column('V:V', 30)
        sheet.set_column('W:W', 30)
        sheet.set_column('X:X', 50)
        sheet.set_column('Y:Y', 40)
        sheet.set_column('Z:Z', 50)
        sheet.set_column('AA:AA', 40)
        sheet.set_column('AB:AB', 30)
        sheet.set_column('AC:AC', 50)
        sheet.set_column('AD:AD', 20)
        sheet.set_column('AE:AE', 50)
        sheet.set_column('AF:AF', 20)
        sheet.set_column('AG:AG', 30)
        sheet.set_column('AH:AH', 30)
        sheet.set_column('AI:AI', 40)
        sheet.set_column('AJ:AJ', 30)
        sheet.set_column('AK:AK', 30)
        sheet.set_column('AL:AL', 50)
        sheet.set_column('AM:AM', 30)
        sheet.set_column('AN:AN', 30)
        sheet.set_column('AO:AO', 30)
        sheet.set_column('AP:AP', 30)
        sheet.set_column('AQ:AQ', 50)
        sheet.set_column('AR:AR', 40)
        sheet.set_column('AS:AS', 30)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        sheet.merge_range(header_row, 0, header_row, 10, \
                          'REPORT BUDGET vs PR vs PO vs REALISASI', style['title_style_align_left'])
        header_row += 1

        program_code = ''
        if wizard.program_code_type == 'specific' and wizard.program_code_ids:
            program_code = ", ".join('{0}'.format(program_code.episode_code) \
                                     for program_code in wizard.program_code_ids)
        elif wizard.program_code_type == 'all':
            program_code = "All"
        sheet.write(header_row, 0, 'KODE PROGRAM: %s' % program_code, style['header_style_align_left'])
        header_row += 1

        item_code = ''
        if wizard.item_code_type == 'specific' and wizard.item_code_ids:
            item_code = ", ".join('{0}'.format(item.item_code) \
                                  for item in wizard.item_code_ids)
        elif wizard.item_code_type == 'all':
            item_code = "All"
        sheet.write(header_row, 0, 'KODE ITEM: %s' % item_code, style['header_style_align_left'])
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
        header_row += 2

        sheet.write(header_row, 0, wizard.company_id.name, style['bold_align_left'])
        print_date = datetime.now(). \
            astimezone(pytz.timezone(self.env.user.tz)).strftime('%d-%b-%Y %H:%M')
        sheet.write(header_row, 0, print_date, style['title_style_align_left'])
        header_row += 1

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'EXPENDITURE TYPE', 'EXPENDITURE NAME', 'BUDGET (Rp)', 'KODE PROGRAM', 'JUDUL PROGRAM',
            'PROJECT CODE', 'PROJECT NAME', 'TASK NUMBER', 'EXPENDITURE CATEGORY CODE',
            'EXPENDITURE CATEGORY NAME', 'NO PR', 'DESKRIPSI PR', 'STATUS PR', 'REQUESTOR', 'TGL PENGAJUAN',
            'KATEGORI PR', 'LINE PR', 'MASTER ITEM', 'DESKRIPSI ITEM (PR)', 'QTY (PR)', 'UNIT PRICE (PR)',
            'TOTAL PR (Rp)', 'NO PO', 'DESKRIPSI PO', 'STATUS PO', 'BUYER NAME', 'TGL PEMBUATAN PO',
            'NO VENDOR', 'NAME VENDOR', 'LINE PO', 'DESKRIPSI ITEM (PO)', 'QTY (PO)', 'UNIT PRICE (PO)',
            'TOTAL PO (Rp)', 'NO INVOICE', 'NO JV', 'TGL INVOICE', 'DESKRIPSI INVOICE', 'INVOICE TYPE',
            'INVOICE STATUS', 'PAYMENT STATUS', 'LINE INVOICE', 'DESKRIPSI LINE INVOICE', 'INVOICE AMOUNT (Rp)',
            'REMAINING',
        ]

        header_row = 8
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        pmis_project_task_line_data = self.get_pmis_project_task_line_by_query(arguments)
        if not pmis_project_task_line_data:
            return

        data_index = 0
        data_row = 9
        expenditure_row = 9
        task_row = 0
        total_remaining = 0
        total_rate_distribution = 0
        looped_expenditure_ids = []
        looped_task_ids = []
        count_data_per_expenditure = 0
        for data in pmis_project_task_line_data:
            new_task = False
            last_data = False
            data_expenditure_to_write = {}
            budget_record = self.env['pmis.budget'].browse(data.get('budget_id', []))

            if not looped_expenditure_ids and data.get('expenditure_id', False):
                looped_expenditure_ids.append(data['expenditure_id'])
            elif looped_expenditure_ids and data.get('expenditure_id', False) \
                    and data['expenditure_id'] in looped_expenditure_ids \
                    and data_index and (len(pmis_project_task_line_data) - 1) == data_index:
                count_data_per_expenditure += 1
                data_expenditure_to_write = data
                last_data = True
            elif looped_expenditure_ids and data.get('expenditure_id', False) \
                    and data['expenditure_id'] not in looped_expenditure_ids \
                    and data_index and (len(pmis_project_task_line_data) - 1) == data_index:
                count_data_per_expenditure += 1
                data_expenditure_to_write = data
                last_data = True
            elif looped_expenditure_ids and data.get('expenditure_id', False) \
                    and data['expenditure_id'] not in looped_expenditure_ids \
                    and data_index:
                looped_expenditure_ids.append(data['expenditure_id'])
                data_expenditure_to_write = pmis_project_task_line_data[data_index - 1]

            if not looped_task_ids and data.get('task_id', False):
                looped_task_ids.append(data['task_id'])
            elif looped_task_ids and data.get('task_id', False) \
                    and data['task_id'] not in looped_task_ids \
                    and data_index:
                looped_task_ids.append(data['task_id'])
                new_task = True

            if new_task:
                data_row += 2

            data_col = 3
            sheet.write(data_row, data_col, data.get('episode_code', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('episode_name', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('program_code', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('program_name', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('task_code', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('expenditure_category_code', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, data.get('expenditure_category_name', ''), \
                        style['table_normal_align_left'])
            data_col += 1

            purchase_request = budget_record.budget_ids.mapped('project_pr_line_ids'). \
                mapped('line_id').mapped('request_id')
            if purchase_request:
                purchase_request = purchase_request[0]

            sheet.write(data_row, data_col, purchase_request.name or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_request.description or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_request.state.upper() if purchase_request else '',
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_request.requested_by.name or '', style['table_normal_align_left'])
            data_col += 1

            pr_date_start = ''
            if purchase_request.date_start:
                pr_date_start = purchase_request.date_start
                pr_date_start = pr_date_start.strftime('%d-%b-%y')
            sheet.write(data_row, data_col, pr_date_start, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_request.line_count or '', style['table_normal_align_right'])
            data_col += 1

            pr_line = purchase_request.line_ids
            if pr_line:
                pr_line = pr_line[0]
            sheet.write(data_row, data_col, pr_line.product_id.default_code or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, pr_line.product_id.name or '', style['table_normal_align_left'])
            data_col += 1

            if pr_line.product_qty:
                sheet.write(data_row, data_col, pr_line.product_qty, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            if pr_line.original_price:
                sheet.write(data_row, data_col, pr_line.original_price, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            if purchase_request.estimated_cost:
                sheet.write(data_row, data_col, purchase_request.estimated_cost, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            purchase_order = budget_record.budget_ids.mapped('project_pr_line_ids'). \
                mapped('po_line_id').mapped('order_id')
            if purchase_order:
                purchase_order = purchase_order[0]

            sheet.write(data_row, data_col, purchase_order.name or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_order.po_description or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_order.state.upper() if purchase_order else '',
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_order.buyer_id.name or '', style['table_normal_align_left'])
            data_col += 1

            po_creation_date = ''
            if purchase_order.create_date:
                po_creation_date = purchase_order.create_date
                po_creation_date = po_creation_date.strftime('%d-%b-%y')
            sheet.write(data_row, data_col, po_creation_date, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_order.partner_ref or '', style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, purchase_order.partner_id.name or '', style['table_normal_align_left'])
            data_col += 1

            po_line_count = ''
            if purchase_order.order_line:
                po_line_count = len(purchase_order.order_line)
            sheet.write(data_row, data_col, po_line_count, style['table_normal_align_right'])
            data_col += 1

            po_line = purchase_order.order_line
            if po_line:
                po_line = po_line[0]
            sheet.write(data_row, data_col, po_line.product_id.name or '', style['table_normal_align_left'])
            data_col += 1

            if po_line.product_qty:
                sheet.write(data_row, data_col, po_line.product_qty, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            if po_line.price_unit:
                sheet.write(data_row, data_col, po_line.price_unit, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            if purchase_order.amount_total:
                sheet.write(data_row, data_col, purchase_order.amount_total, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            bill = purchase_order.mapped('invoice_ids')
            if bill:
                bill = bill[0]
            sheet.write(data_row, data_col, bill.name or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            bill_date = ''
            if bill.invoice_date:
                bill_date = bill.invoice_date
                bill_date = bill_date.strftime('%d-%b-%y')
            sheet.write(data_row, data_col, bill_date, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, bill.ref or '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, bill.bill_type.upper() \
                if bill and bill.bill_type else '', style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, bill.state.upper() if bill and bill.state else '',
                        style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, bill.payment_state or '', style['table_normal_align_left'])
            data_col += 1

            count_bill_line = ''
            if bill.invoice_line_ids:
                count_bill_line = len(bill.invoice_line_ids)
            sheet.write(data_row, data_col, count_bill_line, style['table_normal_align_right'])
            data_col += 1

            bill_line = bill.invoice_line_ids
            if bill_line:
                bill_line = bill_line[0]
            sheet.write(data_row, data_col, bill_line.name or '', style['table_normal_align_right'])
            data_col += 1

            if bill.amount_total:
                sheet.write(data_row, data_col, bill.amount_total, style['table_num'])
            else:
                sheet.write(data_row, data_col, '', style['table_normal_align_right'])
            data_col += 1

            if data_expenditure_to_write:
                data_expenditure_budget_record = self.env['pmis.budget']. \
                    browse(data_expenditure_to_write.get('budget_id', []))
                rate_distribution = self.get_rate_distribution( \
                    data_expenditure_budget_record)
                expenditure_col = 0
                if count_data_per_expenditure and count_data_per_expenditure == 1:
                    sheet.write(expenditure_row, expenditure_col, data_expenditure_to_write.get('expenditure_code', ''),
                                style['table_normal_align_left'])
                    expenditure_col += 1

                    sheet.write(expenditure_row, expenditure_col,
                                data_expenditure_to_write.get('budget_line_item_code', ''),
                                style['table_normal_align_left'])
                    expenditure_col += 1

                    if rate_distribution:
                        sheet.write(expenditure_row, expenditure_col, rate_distribution, style['table_num'])
                    else:
                        sheet.write(expenditure_row, expenditure_col, 0, style['table_normal_align_right'])
                    expenditure_col += 42
                    total_rate_distribution += rate_distribution

                    if data_expenditure_budget_record.total_remaining:
                        sheet.write(expenditure_row, expenditure_col, data_expenditure_budget_record.total_remaining,
                                    style['table_num'])
                    else:
                        sheet.write(expenditure_row, expenditure_col, 0, style['table_normal_align_right'])
                    total_remaining += data_expenditure_budget_record.total_remaining
                elif count_data_per_expenditure and count_data_per_expenditure > 1:
                    sheet.merge_range(expenditure_row, expenditure_col,
                                      expenditure_row + (count_data_per_expenditure - 1), expenditure_col, \
                                      data_expenditure_to_write.get('expenditure_code', ''),
                                      style['table_normal_align_left'])
                    expenditure_col += 1

                    sheet.merge_range(expenditure_row, expenditure_col,
                                      expenditure_row + (count_data_per_expenditure - 1), expenditure_col, \
                                      data_expenditure_to_write.get('budget_line_item_code', ''),
                                      style['table_normal_align_left'])
                    expenditure_col += 1

                    if rate_distribution:
                        sheet.merge_range(expenditure_row, expenditure_col,
                                          expenditure_row + (count_data_per_expenditure - 1), expenditure_col, \
                                          rate_distribution, style['table_num'])
                    else:
                        sheet.merge_range(expenditure_row, expenditure_col,
                                          expenditure_row + (count_data_per_expenditure - 1), expenditure_col, \
                                          0, style['table_normal_align_right'])
                    expenditure_col += 42
                    total_rate_distribution += rate_distribution

                    if data_expenditure_budget_record.total_remaining:
                        sheet.merge_range(expenditure_row, expenditure_col,
                                          expenditure_row + (count_data_per_expenditure - 1), expenditure_col, \
                                          data_expenditure_budget_record.total_remaining, style['table_num'])
                    else:
                        sheet.merge_range(expenditure_row, expenditure_col,
                                          expenditure_row + (count_data_per_expenditure - 1), expenditure_col, \
                                          0, style['table_normal_align_right'])
                    total_remaining += data_expenditure_budget_record.total_remaining

                expenditure_row += count_data_per_expenditure
                if new_task:
                    expenditure_row += 2

                count_data_per_expenditure = 0

            if new_task or last_data:
                task_row = data_row - 2
                last_task_data = pmis_project_task_line_data[data_index - 1]
                if last_data:
                    task_row = data_row + 1
                    last_task_data = data

                task_col = 0
                sheet.write(task_row, task_col, 'TOTAL %s' % last_task_data.get('task_code', ''),
                            style['table_normal_align_left_bg_yellow'])
                task_col += 1

                sheet.write(task_row, task_col, '', style['table_normal_align_left_bg_yellow'])
                task_col += 1

                if total_rate_distribution:
                    sheet.write(task_row, task_col, total_rate_distribution, style['table_num_bg_yellow'])
                else:
                    sheet.write(task_row, task_col, 0, style['table_normal_align_right_bg_yellow'])
                task_col += 1

                empty_task_count = 40
                count = 0
                while count <= empty_task_count:
                    sheet.write(task_row, task_col, '', style['table_normal_align_right_bg_yellow'])
                    task_col += 1
                    count += 1

                if total_remaining:
                    sheet.write(task_row, task_col, total_remaining, style['table_num_bg_yellow'])
                else:
                    sheet.write(task_row, task_col, 0, style['table_normal_align_right_bg_yellow'])

                task_row += 1
                task_col = 0
                sheet.write(task_row, task_col, 'TOTAL', style['table_bold_align_left_bg_yellow'])
                task_col += 1

                empty_task_count = 42
                count = 0
                while count <= empty_task_count:
                    sheet.write(task_row, task_col, '', style['table_normal_align_right_bg_yellow'])
                    task_col += 1
                    count += 1

                if total_remaining:
                    sheet.write(task_row, task_col, total_remaining, style['table_num_bold_bg_yellow'])
                else:
                    sheet.write(task_row, task_col, 0, style['table_bold_align_right_bg_yellow'])

                total_rate_distribution = 0
                total_remaining = 0

            data_row += 1
            data_index += 1
            count_data_per_expenditure += 1

    def get_pmis_project_task_line_by_query(self, arguments):
        results = []
        where_clause = self.get_pmis_project_task_line_where_clause(arguments)
        query = """
            SELECT
                ppt.id AS task_id,
                ppt.code AS task_code,
                pet.id AS expenditure_id,
                pet.code AS expenditure_code,
                pptl.id AS project_task_line_id,
                pb.id AS budget_id,
                pbl.id AS budget_line_id,
                pbl.item_code AS budget_line_item_code,
                pec.id AS expenditure_category_id,
                pec.code AS expenditure_category_code,
                pel.id AS episode_id,
                pel.code AS episode_code,
                pel.name AS episode_name,
                pp.id AS program_id,
                pp.code AS program_code,
                pp.name AS program_name
            FROM pmis_project_task_line pptl
            LEFT JOIN pmis_episode_line pel ON pel.id = pptl.episode_line_id
            LEFT JOIN pmis_project_task ppt ON ppt.id = pptl.line_id
            LEFT JOIN pmis_budget pb ON pb.task_id = ppt.id
            LEFT JOIN pmis_program pp ON pp.id = pb.program_id
            LEFT JOIN pmis_budget_line pbl ON pbl.line_id = pb.id
            LEFT JOIN project_expenditure_type pet ON pet.id = pbl.expenditure_type_id
            LEFT JOIN project_expenditure_category pec ON pec.id = pbl.category_id
            %s
            ORDER BY
                ppt.id ASC,
                pet.id ASC,
                pptl.id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_pmis_project_task_line_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE 
                pptl.company_id = %s
                AND ppt.id IS NOT NULL
                AND pet.id IS NOT NULL
        """ % wizard.company_id.id

        if wizard.program_code_type == 'specific' and \
                wizard.program_code_ids and len(wizard.program_code_ids) > 1:
            program_code_ids = wizard.program_code_ids.ids
            where_clause += ' AND pptl.id in {program_code_ids}'. \
                format(program_code_ids=tuple(program_code_ids))
        elif wizard.program_code_type == 'specific' and \
                wizard.program_code_ids and len(wizard.program_code_ids) == 1:
            program_code_id = wizard.program_code_ids[0].id
            where_clause += ' AND pptl.id = {program_code_id}'. \
                format(program_code_id=program_code_id)

        if wizard.item_code_type == 'specific' and \
                wizard.item_code_ids and len(wizard.item_code_ids) > 1:
            item_code_ids = wizard.item_code_ids.ids
            where_clause += ' AND pet.id in {item_code_ids}'. \
                format(item_code_ids=tuple(item_code_ids))
        elif wizard.item_code_type == 'specific' and \
                wizard.item_code_ids and len(wizard.item_code_ids) == 1:
            item_code_id = wizard.item_code_ids[0].id
            where_clause += ' AND pet.id = {item_code_id}'. \
                format(item_code_id=item_code_id)

        start_date = wizard.start_date.strftime('%Y-%m-%d')
        if wizard.date_type == 'range_of_date' and wizard.start_date and wizard.end_date:
            end_date = wizard.end_date.strftime('%Y-%m-%d')
            where_clause += """
                AND pb.date_start >= '%s' AND pb.date_end <= '%s'
            """ % (start_date, end_date)
        elif wizard.date_type == 'current_date' and wizard.start_date:
            where_clause += " AND pb.date_start = '%s'" % start_date
        elif wizard.date_type == 'as_of_date' and wizard.start_date:
            where_clause += " AND pb.date_start <= '%s'" % start_date

        return where_clause

    def get_rate_distribution(self, budget):
        rate = 0
        all_rates = []
        for line in budget.budget_ids:
            all_rates += self.get_rates_per_budget_line(line)

        if all_rates:
            rate = max(all_rates)

        return rate

    def get_rates_per_budget_line(self, budget_line):
        list_of_rates = [x.amount for x in budget_line.detail_ids]
        if not list_of_rates:
            total = budget_line.budget
            # NOTE: the number for line is taken from task_id.range_start
            task = budget_line.line_id.task_id
            if task.is_batch is True:
                for x in range(task.range_end, task.range_end + 1):
                    amt = budget_line.budget
                    total -= amt
                    list_of_rates.append(amt if total >= 0 else 0)
            if task.is_batch is False:
                for x in range(task.range_start, task.range_end + 1):
                    amt = budget_line.budget / budget_line.eps
                    total -= amt
                    list_of_rates.append(amt if total >= 0 else 0)

        return list_of_rates
