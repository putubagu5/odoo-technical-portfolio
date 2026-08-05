from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncProjectCostingDetailReport(models.TransientModel):
    _name = 'wizard.mnc.project.costing.detail.report'

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
        int_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0'})
        int_table.set_font_size('11')
        int_table.set_border()
        #################################################################################
        right_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer.set_font_size('12')
        right_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('12')
        numb_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 15)
        worksheet1.set_column('B:B', 15)
        worksheet1.set_column('C:C', 15)
        worksheet1.set_column('D:D', 15)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 30)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 30)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 15)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 15)
        worksheet1.set_column('N:N', 15)
        worksheet1.set_column('O:O', 15)
        worksheet1.set_column('P:P', 15)
        worksheet1.set_column('Q:Q', 15)
        worksheet1.set_column('R:R', 15)
        worksheet1.set_column('S:S', 15)
        worksheet1.set_column('T:T', 15)
        worksheet1.set_column('U:U', 15)
        worksheet1.set_column('V:V', 15)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " PC - Project Costing Detail Report"

        worksheet1.merge_range('A1:H1', 'PROJECT COSTING DETAIL REPORT', left_title)
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

        budget_vals = []
        for budget in budget_ids:
            budget_vals.append({
                'budget_id': budget.line_id.id,
                'budget_name': budget.line_id.display_name,
                'budget_line_id': budget.id
            })

        grouped = collections.defaultdict(list)
        for item in budget_vals:
            grouped[item['budget_id']].append(item)

        for bdt, items in grouped.items():
            budget_id = self.env['pmis.budget'].sudo().browse(bdt)

            worksheet1.merge_range(i, 0, i, 3, budget_id.program_id.name, left_title_sub)
            i += 1
            worksheet1.write(i, 0, 'PERIODE', header_table)
            worksheet1.write(i, 1, 'PROJECT CODE', header_table)
            worksheet1.write(i, 2, 'TASK NAME', header_table)
            worksheet1.write(i, 3, 'TASK NUMBER', header_table)
            worksheet1.write(i, 4, 'PROGRAM CODE', header_table)
            worksheet1.write(i, 5, 'PROGRAM TITLE', header_table)
            worksheet1.write(i, 6, 'EXPENDITURE TYPE', header_table)
            worksheet1.write(i, 7, 'EXPENDITURE DESCRIPTION', header_table)
            worksheet1.write(i, 8, 'BUDGET COST', header_table)
            worksheet1.write(i, 9, 'PR NO', header_table)
            worksheet1.write(i, 10, 'PR LINE NUM', header_table)
            worksheet1.write(i, 11, 'PR AMOUNT IDR', header_table)
            worksheet1.write(i, 12, 'PO NO', header_table)
            worksheet1.write(i, 13, 'PO DATE', header_table)
            worksheet1.write(i, 14, 'PO STATUS', header_table)
            worksheet1.write(i, 15, 'PO LINE NUM', header_table)
            worksheet1.write(i, 16, 'PO AMOUNT IDR', header_table)
            worksheet1.write(i, 17, 'INV NO', header_table)
            worksheet1.write(i, 18, 'INV AMOUNT IDR', header_table)
            worksheet1.write(i, 19, 'REF AMOUNT IDR', header_table)
            worksheet1.write(i, 20, 'INV SET NO', header_table)
            worksheet1.write(i, 21, 'SET AMOUNT IDR', header_table)
            i += 1

            amount_budget = 0
            amount_pr_idr = 0
            amount_po_idr = 0
            amount_inv_idr = 0
            amount_ref_idr = 0
            amount_set_idr = 0
            for item in items:
                budget_line_id = self.env['pmis.budget.line'].sudo().browse(item['budget_line_id'])

                project_pr_ids = budget_line_id.project_pr_line_ids.filtered(lambda l: l.line_id)
                i_prl = len(project_pr_ids) if project_pr_ids else 0

                worksheet1.merge_range(i, 0, i + i_prl, 0,
                                       datetime.strptime(str(budget_id.program_id.date_start), "%Y-%m-%d").strftime(
                                           "%b-%Y") if budget_id.program_id.date_start else '', left_table)
                worksheet1.merge_range(i, 1, i + i_prl, 1, budget_id.program_id.code, left_table)
                worksheet1.merge_range(i, 2, i + i_prl, 2, budget_id.task_id.episode_ids[
                    0].episode_code if budget_id.task_id and budget_id.task_id.episode_ids else '', left_table)
                worksheet1.merge_range(i, 3, i + i_prl, 3, budget_id.task_id.episode_ids[
                    0].episode_code if budget_id.task_id and budget_id.task_id.episode_ids else '', left_table)
                worksheet1.merge_range(i, 4, i + i_prl, 4, budget_id.task_id.episode_ids[
                    0].episode_code if budget_id.task_id and budget_id.task_id.episode_ids else '', left_table)
                worksheet1.merge_range(i, 5, i + i_prl, 5, budget_id.task_id.episode_ids[
                    0].episode_name if budget_id.task_id and budget_id.task_id.episode_ids else '', left_table)
                worksheet1.merge_range(i, 6, i + i_prl, 6, budget_line_id.expenditure_type_id.name, left_table)
                worksheet1.merge_range(i, 7, i + i_prl, 7, budget_line_id.expenditure_type_id.note, left_table)
                worksheet1.merge_range(i, 8, i + i_prl, 8, budget_line_id.rate, numb_table)

                if project_pr_ids:
                    for prl in project_pr_ids:
                        worksheet1.write(i, 9, prl.line_id.request_id.name if prl.line_id else '', left_table)
                        worksheet1.write(i, 10, prl.line_id.line_number if prl.line_id else '', int_table)
                        worksheet1.write(i, 11, prl.line_id.estimated_cost if prl.line_id else 0, left_table)
                        worksheet1.write(i, 12, prl.po_line_id.order_id.name if prl.po_line_id else '', left_table)
                        worksheet1.write(i, 13, datetime.strptime(str(prl.po_line_id.order_id.date_order),
                                                                  "%Y-%m-%d %H:%M:%S").strftime(
                            "%d-%b-%Y") if prl.po_line_id else '', left_table)
                        worksheet1.write(i, 14, dict(prl.po_line_id.order_id._fields['state'].selection).get(
                            prl.po_line_id.order_id.state) if prl.po_line_id else '', left_table)
                        worksheet1.write(i, 15, prl.po_line_id.line_number if prl.po_line_id else '', int_table)
                        worksheet1.write(i, 16, prl.po_line_id.price_subtotal if prl.po_line_id else 0, numb_table)
                        worksheet1.write(i, 17, prl.account_line_id.move_id.name if prl.account_line_id else '',
                                         left_table)
                        worksheet1.write(i, 18, prl.account_line_id.price_subtotal if prl.account_line_id else 0,
                                         numb_table)
                        worksheet1.write(i, 19, 0, numb_table)
                        worksheet1.write(i, 20, '', numb_table)
                        worksheet1.write(i, 21, 0, numb_table)

                        amount_budget += budget_line_id.rate
                        amount_pr_idr += prl.line_id.estimated_cost if prl.line_id else 0
                        amount_po_idr += prl.po_line_id.price_subtotal if prl.po_line_id else 0
                        amount_inv_idr += prl.account_line_id.price_subtotal if prl.account_line_id else 0
                        amount_ref_idr += 0
                        amount_set_idr += 0
                        i += 1

                else:
                    worksheet1.write(i, 9, '', left_table)
                    worksheet1.write(i, 10, '', int_table)
                    worksheet1.write(i, 11, 0, left_table)
                    worksheet1.write(i, 12, '', left_table)
                    worksheet1.write(i, 13, '', left_table)
                    worksheet1.write(i, 14, '', left_table)
                    worksheet1.write(i, 15, '', int_table)
                    worksheet1.write(i, 16, 0, numb_table)
                    worksheet1.write(i, 17, '', numb_table)
                    worksheet1.write(i, 18, 0, numb_table)
                    worksheet1.write(i, 19, 0, numb_table)
                    worksheet1.write(i, 20, '', numb_table)
                    worksheet1.write(i, 21, 0, numb_table)

                    amount_budget += 0
                    amount_pr_idr += 0
                    amount_po_idr += 0
                    amount_inv_idr += 0
                    amount_ref_idr += 0
                    amount_set_idr += 0
                    i += 1

            worksheet1.merge_range(i, 0, i, 7, 'TOTAL ' + str(budget_id.program_id.name), right_footer)
            worksheet1.write(i, 8, amount_budget, numb_footer)
            worksheet1.write(i, 9, '', right_footer)
            worksheet1.write(i, 10, '', right_footer)
            worksheet1.write(i, 11, amount_pr_idr, numb_footer)
            worksheet1.write(i, 12, '', right_footer)
            worksheet1.write(i, 13, '', right_footer)
            worksheet1.write(i, 14, '', right_footer)
            worksheet1.write(i, 15, '', right_footer)
            worksheet1.write(i, 16, amount_po_idr, numb_footer)
            worksheet1.write(i, 17, '', right_footer)
            worksheet1.write(i, 18, amount_inv_idr, numb_footer)
            worksheet1.write(i, 19, amount_ref_idr, numb_footer)
            worksheet1.write(i, 20, '', right_footer)
            worksheet1.write(i, 21, amount_set_idr, numb_footer)
            i += 2

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.project.costing.detail.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
