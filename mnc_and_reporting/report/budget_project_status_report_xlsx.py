from pytz import timezone
from datetime import datetime, date
from odoo import models, _


class BudgetProjectStatusReportXLSX(models.AbstractModel):
    _name = 'report.mnc_and_reporting.budget_project_status_report_xlsx'
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
        workbook.close()

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
        }

    def set_column_width(self, sheet):
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 40)
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
        sheet.set_column('P:P', 50)
        sheet.set_column('Q:Q', 40)
        sheet.set_column('R:R', 40)
        sheet.set_column('S:S', 40)
        sheet.set_column('T:T', 40)

    def set_header_data(self, arguments):
        sheet, wizard = arguments['sheet'], arguments['wizard']
        style = self.get_workbook_style(arguments['workbook'])

        header_row = 0
        sheet.write(header_row, 0, 'Budget Project Status Report', style['title_style_align_left'])
        header_row += 1

        period = ''
        start_date = wizard.start_date.strftime('%d-%b-%y').upper()
        if wizard.date_type and wizard.date_type == 'as_of_date':
            period = 'As of Date : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'current_date':
            period = 'Date : {start_date}'.format(start_date=start_date)
        elif wizard.date_type and wizard.date_type == 'range_of_date':
            end_date = wizard.end_date.strftime('%d-%b-%y').upper()
            period = 'Date : {start_date} - {end_date}'.format(start_date=start_date, end_date=end_date)
        sheet.merge_range(header_row, 0, header_row, 10, period, style['title_style_align_left'])
        header_row += 1

    def set_table_header_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        headers = [
            'Main Project', 'Project Number', 'Project Name', 'Task Number',
            'Task Name', 'Baselined Date', 'Version Number', 'Budget Status', 'Cur Base Raw Cost',
            'Project Type', 'Project Status Code', 'Creation Date', 'Start Date', 'Closed Date',
            'Baselined By Person Name', 'Pr Amount Idr', 'Po Amount Idr', 'Inv Amount Idr', 'Settlement Amount',
        ]

        header_row = 5
        header_col = 0
        for header in headers:
            sheet.write(header_row, header_col, header, style['table_header'])
            header_col += 1

    def set_table_body_data(self, arguments):
        sheet = arguments['sheet']
        style = self.get_workbook_style(arguments['workbook'])

        budget_project_data = self.get_budget_project_by_query(arguments)
        if not budget_project_data:
            return

        data_row = 6
        total_rate_distribution = 0
        total_pr_amount_idr = 0
        total_po_amount_idr = 0
        total_inv_amount_idr = 0
        total_settlement_inv_amount = 0
        for data in budget_project_data:
            budget_record = self.env['pmis.budget'].browse(data.get('pmis_budget_id', []))
            data_col = 0

            sheet.write(data_row, data_col, \
                        data.get('main_project_name', ''), style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, \
                        data.get('program_code', ''), style['table_normal_align_left'])
            data_col += 1

            sheet.write(data_row, data_col, \
                        data.get('program_name', ''), style['table_normal_align_left'])
            data_col += 1

            task_id = self.env['pmis.project.task']
            if data.get('task_id', False) and isinstance(data['task_id'], int):
                task_id = task_id.browse([data['task_id']])

            episode_code = ''
            episode_with_episode_code = task_id.episode_ids. \
                filtered(lambda episode: episode.episode_code)
            if episode_with_episode_code:
                episode_code = episode_with_episode_code[0].episode_code

            sheet.write(data_row, data_col, episode_code, style['table_normal_align_left'])
            data_col += 1

            episode_line_id_code = ''
            episode_with_episode_line_id_code = task_id.episode_ids. \
                filtered(lambda episode: episode.episode_line_id.code)
            if episode_with_episode_line_id_code:
                episode_line_id_code = episode_with_episode_line_id_code[0].episode_line_id.code

            sheet.write(data_row, data_col, episode_line_id_code, style['table_normal_align_left'])
            data_col += 1

            approval_data = self.get_budget_approval_data(budget_record)
            sheet.write(data_row, data_col, approval_data.get('date', '') or '', style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            task_status = ''
            if data.get('pmis_budget_task_status', ''):
                task_status = data['pmis_budget_task_status']
                task_status = task_status.capitalize()
            sheet.write(data_row, data_col, task_status, style['table_normal_align_left'])
            data_col += 1

            rate_distribution = self.get_rate_distribution(budget_record)
            if rate_distribution:
                sheet.write(data_row, data_col, rate_distribution, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            data_col += 1
            total_rate_distribution += rate_distribution

            # PROJECT TYPE NOT CLEAR
            sheet.write(data_row, data_col, '', style['table_normal_align_left'])
            data_col += 1

            project_status_code = 'Active'
            printed_date = date.today()
            if printed_date and budget_record.date_end and printed_date > budget_record.date_end:
                project_status_code = 'Inactive'
            sheet.write(data_row, data_col, project_status_code, style['table_normal_align_left'])
            data_col += 1

            budget_create_date = ''
            if data.get('pmis_budget_create_date', ''):
                budget_create_date = data['pmis_budget_create_date'].strftime('%d-%b-%y')
            sheet.write(data_row, data_col, budget_create_date, style['table_normal_align_right'])
            data_col += 1

            budget_date_start = ''
            if data.get('pmis_budget_date_start', ''):
                budget_date_start = data['pmis_budget_date_start'].strftime('%d-%b-%y')
            sheet.write(data_row, data_col, budget_date_start, style['table_normal_align_right'])
            data_col += 1

            budget_date_end = ''
            if data.get('pmis_budget_date_end', ''):
                budget_date_end = data['pmis_budget_date_end'].strftime('%d-%b-%y')
            sheet.write(data_row, data_col, budget_date_end, style['table_normal_align_right'])
            data_col += 1

            sheet.write(data_row, data_col, approval_data.get('author', ''), style['table_normal_align_left'])
            data_col += 1

            pr_amount_idr = 0
            purchase_requests = budget_record.budget_ids.mapped('project_pr_line_ids'). \
                mapped('line_id').mapped('request_id')
            if purchase_requests:
                pr_amount_idr = sum(purchase_requests.mapped('estimated_cost'))
            if pr_amount_idr:
                sheet.write(data_row, data_col, pr_amount_idr, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            data_col += 1
            total_pr_amount_idr += pr_amount_idr

            po_amount_idr = 0
            purchase_orders = budget_record.budget_ids.mapped('project_pr_line_ids'). \
                mapped('po_line_id').mapped('order_id')
            if purchase_orders:
                po_amount_idr = sum(purchase_orders.mapped('amount_total'))
            if po_amount_idr:
                sheet.write(data_row, data_col, po_amount_idr, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            data_col += 1
            total_po_amount_idr += po_amount_idr

            inv_amount_idr = 0
            bills = purchase_orders.mapped('invoice_ids')
            if bills:
                inv_amount_idr = sum(bills.mapped('amount_total'))
            if inv_amount_idr:
                sheet.write(data_row, data_col, inv_amount_idr, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            data_col += 1
            total_inv_amount_idr += inv_amount_idr

            settlement_inv_amount = 0
            settlement_bills = bills.filtered(lambda bill: bill.bill_type == 'settlement')
            if settlement_bills:
                settlement_inv_amount = sum(settlement_bills.mapped('amount_total'))
            if settlement_inv_amount:
                sheet.write(data_row, data_col, settlement_inv_amount, style['table_num'])
            else:
                sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
            data_col += 1
            total_settlement_inv_amount += settlement_inv_amount

            data_row += 1

        data_col = 0
        sheet.write(data_row, data_col, '', style['table_normal_align_right'])
        data_col += 1

        sheet.merge_range(data_row, data_col, data_row, data_col + 6, 'Grand Total :', style['table_bold_align_left'])
        data_col += 7

        if total_rate_distribution:
            sheet.write(data_row, data_col, total_rate_distribution, style['table_num_bold'])
        else:
            sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
        data_col += 1

        sheet.merge_range(data_row, data_col, data_row, data_col + 5, '', style['table_bold_align_left'])
        data_col += 6

        if total_pr_amount_idr:
            sheet.write(data_row, data_col, total_pr_amount_idr, style['table_num_bold'])
        else:
            sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
        data_col += 1

        if total_po_amount_idr:
            sheet.write(data_row, data_col, total_po_amount_idr, style['table_num_bold'])
        else:
            sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
        data_col += 1

        if total_inv_amount_idr:
            sheet.write(data_row, data_col, total_inv_amount_idr, style['table_num_bold'])
        else:
            sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
        data_col += 1

        if total_settlement_inv_amount:
            sheet.write(data_row, data_col, total_settlement_inv_amount, style['table_num_bold'])
        else:
            sheet.write(data_row, data_col, 0, style['table_normal_align_right'])
        data_col += 1

    def get_budget_project_by_query(self, arguments):
        results = []
        where_clause = self.get_budget_project_where_clause(arguments)
        query = """
            SELECT 
                pmp.id AS main_project_id,
                pmp.name AS main_project_code,
                pmp.main_project_name AS main_project_name,
                pp.id AS program_id,
                pp.name AS program_name,
                pp.code AS program_code,
                ppt.id AS task_id,
                pb.id as pmis_budget_id,
                pb.task_status AS pmis_budget_task_status,
                pb.create_date AS pmis_budget_create_date,
                pb.date_start AS pmis_budget_date_start,
                pb.date_end AS pmis_budget_date_end
            FROM pmis_budget pb
            LEFT JOIN pmis_main_project pmp ON pmp.id = pb.main_project_id
            LEFT JOIN pmis_program pp ON pp.id = pb.program_id
            LEFT JOIN pmis_project_task ppt ON ppt.id = pb.task_id
            %s
            ORDER BY pb.id ASC
        """ % (where_clause)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        return results

    def get_budget_project_where_clause(self, arguments):
        wizard = arguments['wizard']
        where_clause = """
            WHERE pb.company_id = %s
        """ % wizard.company_id.id

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

    def get_budget_approval_data(self, budget):
        approval_data = {}
        if budget.task_status and budget.task_status == 'approve':
            budget_model_id = self.get_budget_model_id()
            budget_task_status_field_id = self. \
                get_budget_model_field_id(budget_model_id, 'task_status')
            approval_tracking_value = self. \
                get_budget_approval_data_tracking_value(budget_task_status_field_id)
            if approval_tracking_value:
                approval_date = approval_tracking_value.get('create_date', False)
                if approval_date:
                    approval_date = approval_date.astimezone(timezone(self.env.user.tz))
                    approval_date = approval_date.strftime("%d-%b-%y")
                    approval_data['date'] = approval_date

                approval_user_name = approval_tracking_value.get('author_name', '')
                if approval_user_name:
                    approval_data['author'] = approval_user_name

        return approval_data

    def get_budget_model_id(self):
        budget_model_id = False
        query = """
            SELECT im.id
            FROM ir_model im
            WHERE im.model = 'pmis.budget'
            ORDER BY im.id DESC
            LIMIT 1
        """
        self.env.cr.execute(query)
        result = self.env.cr.fetchone()
        if result:
            budget_model_id = result[0]

        return budget_model_id

    def get_budget_model_field_id(self, budget_model_id, field):
        budget_model_field_id = False
        query = """
            SELECT imf.id
            FROM ir_model_fields imf
            WHERE 
                imf.model_id = %s
                and imf.name = '%s'
            ORDER BY imf.id DESC
            LIMIT 1
        """ % (budget_model_id, field)
        self.env.cr.execute(query)
        result = self.env.cr.fetchone()
        if result:
            budget_model_field_id = result[0]

        return budget_model_field_id

    def get_budget_approval_data_tracking_value(self, field_id):
        approval_data = ''
        query = """
            SELECT
                rp.name as author_name,
                mtv.create_date as create_date
            FROM mail_tracking_value mtv
            LEFT JOIN mail_message mm ON mm.id = mtv.mail_message_id
            LEFT JOIN res_partner rp ON rp.id = mm.author_id
            WHERE 
                mtv.field = %s
                and new_value_char = 'Approved'
                and mm.model = 'pmis.budget'
            ORDER BY mtv.id desc
            LIMIT 1
        """ % field_id
        self.env.cr.execute(query)
        approval_data = self.env.cr.dictfetchone()

        return approval_data

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
