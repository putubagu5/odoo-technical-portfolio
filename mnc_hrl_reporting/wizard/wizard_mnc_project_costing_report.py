from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncProjectCostingReport(models.TransientModel):
    _name = 'wizard.mnc.project.costing.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    project_id = fields.Many2one(comodel_name="pmis.main.project", string="Project Code")
    task_id = fields.Many2one(comodel_name="pmis.project.task", string="Task Name")
    program_id = fields.Many2one(comodel_name="pmis.program", string="Program Code")
    expenditure_type_id = fields.Many2one(comodel_name="project.expenditure.type", string="Expenditure Type")
    file = fields.Binary("File")

    @api.onchange('company_id')
    def onchange_company_id(self):
        return {'domain': {
            'company_id': [
                ('id', 'in', self.env.user.company_ids.ids),
            ]
        }
        }

    def button_print_excel(self):
        self.ensure_one()

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        left_title = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title.set_font_size('15')
        left_title2 = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_title2.set_font_size('14')

        left_title_sub = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title_sub.set_font_size('14')
        #################################################################################
        header_table = workbook.add_format({'valign': 'vcenter', 'align': 'center', 'font_color': '#FFFFFF'})
        header_table.set_font_size('12')
        header_table.set_bg_color('#02569C')
        header_table.set_border()
        #################################################################################
        center_table = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_table.set_font_size('11')
        center_table.set_border()
        #################################################################################
        left_table = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_table.set_font_size('11')
        left_table.set_border()
        #################################################################################
        numb_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_table.set_font_size('11')
        numb_table.set_border()
        #################################################################################
        left_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_footer.set_font_size('12')
        left_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('12')
        numb_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 25)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 15)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 35)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 30)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 15)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 15)
        worksheet1.set_column('N:N', 15)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " PC - Project Costing Summary Report"

        worksheet1.merge_range('A1:H1', 'PROJECT COSTING SUMMARY REPORT', left_title)
        worksheet1.write('A2', 'Project Code', left_title2)
        worksheet1.merge_range('B2:D2', ': ' + (self.project_id.name if self.project_id else 'All'), left_title2)
        worksheet1.write('A3', 'Task Name', left_title2)
        worksheet1.merge_range('B3:D3', ': ' + (self.task_id.display_name if self.task_id else 'All'), left_title2)
        worksheet1.write('A4', 'Program Code', left_title2)
        worksheet1.merge_range('B4:D4', ': ' + (self.program_id.code if self.program_id else 'All'), left_title2)
        worksheet1.write('A5', 'Expenditure Type', left_title2)
        worksheet1.merge_range('B5:D5', ': ' + (self.expenditure_type_id.name if self.expenditure_type_id else 'All'),
                               left_title2)

        i = 6

        query = """ 
                    SELECT bgl.id
                        FROM pmis_budget_line AS bgl
                            INNER JOIN pmis_budget bg ON bg.id=bgl.line_id
                    WHERE bg.company_id=%s AND bg.task_status='approve'
                """
        params = (self.company_id.id,)
        if self.project_id:
            query += ' AND bg.main_project_id=%s'
            params += (self.project_id.id,)
        if self.task_id:
            query += ' AND bg.task_id=%s'
            params += (self.task_id.id,)
        if self.program_id:
            query += ' AND bg.program_id=%s'
            params += (self.program_id.id,)
        if self.expenditure_type_id:
            query += ' AND bgl.expenditure_type_id=%s'
            params += (self.expenditure_type_id.id,)

        self._cr.execute(query, params)
        budget_ids = self.env['pmis.budget.line'].sudo().browse([r[0] for r in self._cr.fetchall()])

        item_vals = []
        for budget in budget_ids:
            item_vals.append({
                'budget_id': budget.line_id.id,
                'budget_name': budget.line_id.display_name,
                'budget_line_id': budget.id
            })

        grouped = collections.defaultdict(list)
        for item in item_vals:
            grouped[item['budget_id']].append(item)

        for bdt, items in grouped.items():
            budget_id = self.env['pmis.budget'].sudo().browse(bdt)

            worksheet1.merge_range(i, 0, i, 3, budget_id.program_id.name, left_title_sub)
            i += 1
            worksheet1.write(i, 0, 'Project Main', header_table)
            worksheet1.write(i, 1, 'Project Code', header_table)
            worksheet1.write(i, 2, 'Periode', header_table)
            worksheet1.write(i, 3, 'Task Name', header_table)
            worksheet1.write(i, 4, 'Program Code', header_table)
            worksheet1.write(i, 5, 'Program Title', header_table)
            worksheet1.write(i, 6, 'Expenditure Type', header_table)
            worksheet1.write(i, 7, 'Expenditure Description', header_table)
            worksheet1.write(i, 8, 'Budget Cost', header_table)
            worksheet1.write(i, 9, 'Pr Amount Idr', header_table)
            worksheet1.write(i, 10, 'Po Amount Idr', header_table)
            worksheet1.write(i, 11, 'Inv Amount Idr', header_table)
            worksheet1.write(i, 12, 'Set Amount Idr', header_table)
            worksheet1.write(i, 13, 'Bgt Inv Set', header_table)
            i += 1

            amount_budget = 0
            amount_pr = 0
            amount_po = 0
            amount_inv = 0
            amount_set_inv = 0
            amount_budget_inv = 0
            for item in items:
                budget_line_id = self.env['pmis.budget.line'].sudo().browse(item['budget_line_id'])

                purchase_request = budget_line_id.project_pr_line_ids.mapped('line_id').filtered(
                    lambda l: l.request_state in ['to_approve', 'approved', 'done'])
                purchase_order = budget_line_id.project_pr_line_ids.mapped('po_line_id').filtered(
                    lambda l: l.state in ['to approve', 'purchase', 'done'])

                worksheet1.write(i, 0, budget_id.main_project_id.main_project_name, left_table)
                worksheet1.write(i, 1, budget_id.program_id.code, left_table)
                worksheet1.write(i, 2, datetime.strptime(str(budget_id.program_id.date_start), "%Y-%m-%d").strftime(
                    "%b-%Y") if budget_id.program_id.date_start else '', left_table)
                worksheet1.write(i, 3, budget_id.task_id.code, left_table)
                worksheet1.write(i, 4, budget_id.task_id.episode_ids[
                    0].episode_code if budget_id.task_id and budget_id.task_id.episode_ids else '', left_table)
                worksheet1.write(i, 5, budget_id.task_id.episode_ids[
                    0].episode_name if budget_id.task_id and budget_id.task_id.episode_ids else '', left_table)
                worksheet1.write(i, 6, budget_line_id.expenditure_type_id.name, left_table)
                worksheet1.write(i, 7,
                                 budget_line_id.expenditure_type_id.note if budget_line_id.expenditure_type_id.note else budget_line_id.expenditure_type_id.name,
                                 left_table)
                worksheet1.write(i, 8, budget_line_id.rate, numb_table)
                worksheet1.write(i, 9, sum(purchase_request.mapped('estimated_cost')), numb_table)
                worksheet1.write(i, 10, sum(purchase_order.mapped('price_subtotal')), numb_table)
                worksheet1.write(i, 11, sum(inv.price_subtotal for inv in purchase_order.invoice_lines.filtered(
                    lambda i: i.move_id.state != 'cancel')), numb_table)
                worksheet1.write(i, 12, 0, numb_table)
                worksheet1.write(i, 13, budget_line_id.rate - sum(inv.price_subtotal for inv in
                                                                  purchase_order.invoice_lines.filtered(
                                                                      lambda i: i.move_id.state != 'cancel')),
                                 numb_table)

                amount_budget += budget_line_id.rate
                amount_pr += sum(purchase_request.mapped('estimated_cost'))
                amount_po += sum(purchase_order.mapped('price_subtotal'))
                amount_inv += sum(inv.price_subtotal for inv in
                                  purchase_order.invoice_lines.filtered(lambda i: i.move_id.state != 'cancel'))
                amount_set_inv += 0
                amount_budget_inv += budget_line_id.rate - sum(inv.price_subtotal for inv in
                                                               purchase_order.invoice_lines.filtered(
                                                                   lambda i: i.move_id.state != 'cancel'))
                i += 1

            worksheet1.merge_range(i, 0, i, 7, '', left_footer)
            worksheet1.write(i, 8, amount_budget, numb_footer)
            worksheet1.write(i, 9, amount_pr, numb_footer)
            worksheet1.write(i, 10, amount_po, numb_footer)
            worksheet1.write(i, 11, amount_inv, numb_footer)
            worksheet1.write(i, 12, amount_set_inv, numb_footer)
            worksheet1.write(i, 13, amount_budget_inv, numb_footer)
            i += 2

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.project.costing.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
            self.id, filename),
            'target': 'new',
        }
