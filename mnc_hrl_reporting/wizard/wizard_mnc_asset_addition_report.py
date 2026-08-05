from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncAssetAdditionReport(models.TransientModel):
    _name = 'wizard.mnc.asset.addition.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
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
        left_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_title_sub.set_font_size('13')
        #################################################################################
        header_table = workbook.add_format({'valign': 'vcenter', 'align': 'center', 'font_color': '#FFFFFF'})
        header_table.set_font_size('12')
        header_table.set_bg_color('#02569C')
        header_table.set_border()
        header_table.set_text_wrap()
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
        worksheet1.set_column('A:A', 15)
        worksheet1.set_column('B:B', 15)
        worksheet1.set_column('C:C', 15)
        worksheet1.set_column('D:D', 15)
        worksheet1.set_column('E:E', 15)
        worksheet1.set_column('F:F', 15)
        worksheet1.set_column('G:G', 15)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 15)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 15)
        worksheet1.set_column('N:N', 15)
        worksheet1.set_column('O:O', 15)
        worksheet1.set_column('P:P', 15)
        worksheet1.set_column('Q:Q', 15)
        worksheet1.set_column('R:R', 45)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " FA - Asset Addition Report"

        worksheet1.merge_range('A1:E1', 'ASSET ADDITION REPORT', left_title)
        worksheet1.merge_range('A2:E2', self.company_id.name, left_title)

        i = 2
        worksheet1.write(i, 0, 'Period', left_title_sub)
        worksheet1.write(i, 1, ': ' + datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%b-%Y") + ' s/d ' + \
                         datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%b-%Y"), left_title_sub)

        i += 2
        worksheet1.write(i, 0, 'Asset Type', header_table)
        worksheet1.write(i, 1, 'Asset Account', header_table)
        worksheet1.write(i, 2, 'Reserve Account', header_table)
        worksheet1.write(i, 3, 'Asset Number', header_table)
        worksheet1.write(i, 4, 'Date Placed In Service', header_table)
        worksheet1.write(i, 5, 'Deprn Method', header_table)
        worksheet1.write(i, 6, 'Life Asset', header_table)
        worksheet1.write(i, 7, 'Month/Year', header_table)
        worksheet1.write(i, 8, 'Initial Cost', header_table)
        worksheet1.write(i, 9, 'Year-To-Date Depreciation', header_table)
        worksheet1.write(i, 10, 'Initial Deprn Reserve', header_table)
        worksheet1.write(i, 11, 'Transaction Number', header_table)
        worksheet1.write(i, 12, 'Invoice Number', header_table)
        worksheet1.write(i, 13, 'PO Number', header_table)
        worksheet1.write(i, 14, 'Quantity PO', header_table)
        worksheet1.write(i, 15, 'PR Number', header_table)
        worksheet1.write(i, 16, 'Supplier Name', header_table)
        worksheet1.write(i, 17, 'Description', header_table)
        i += 1

        query = """ 
                    SELECT ast.id
                        FROM account_asset AS ast
                    WHERE ast.company_id=%s AND ast.first_depreciation_date>=%s AND ast.first_depreciation_date<=%s AND ast.state IN ('open','close')
                    ORDER BY ast.first_depreciation_date asc
                """
        params = (self.company_id.id, self.start_date, self.end_date,)

        self._cr.execute(query, params)
        asset_ids = self.env['account.asset'].sudo().browse([r[0] for r in self._cr.fetchall()])
        for asset in asset_ids:
            worksheet1.write(i, 0, dict(asset._fields['state'].selection).get(asset.state), left_table)
            worksheet1.write(i, 1, asset.account_asset_id.code, left_table)
            worksheet1.write(i, 2, asset.account_depreciation_id.code, left_table)
            worksheet1.write(i, 3, asset.asset_no if asset.asset_no else '', left_table)
            worksheet1.write(i, 4, datetime.strptime(str(asset.first_depreciation_date), "%Y-%m-%d").strftime(
                "%d-%b-%Y") if asset.first_depreciation_date else '', left_table)
            worksheet1.write(i, 5, dict(asset._fields['method'].selection).get(asset.method) if asset.method else '',
                             left_table)
            worksheet1.write(i, 6, asset.method_number, left_table)
            worksheet1.write(i, 7, dict(asset._fields['method_period'].selection).get(
                asset.method_period) if asset.method_period else '', left_table)
            worksheet1.write(i, 8, asset.original_value, numb_table)
            worksheet1.write(i, 9, asset.amount_depreciated, numb_table)
            worksheet1.write(i, 10, 0, numb_table)
            worksheet1.write(i, 11, '', left_table)
            worksheet1.write(i, 12, asset.source_line_ids[0].invoice_name if asset.source_line_ids else '',
                             left_table)
            worksheet1.write(i, 13, asset.source_line_ids[0].purchase_name if asset.source_line_ids else '',
                             left_table)
            worksheet1.write(i, 14, sum(sum(line.product_qty for line in po.order_line) for po in
                                        asset.source_line_ids.mapped('product_id')) if asset.source_line_ids else 0,
                             numb_table)
            worksheet1.write(i, 15, '', left_table)  # pr_number
            worksheet1.write(i, 16, '', left_table)  # supplier_name
            worksheet1.write(i, 17, asset.source_line_ids[0].description if asset.source_line_ids else '', left_table)
            # worksheet1.write(i, 15, asset.source_line_ids[0].purchase_id.order_line[
            #     0].request_id.name if asset.source_line_ids and asset.source_line_ids[0].purchase_id else '',
            #                  left_table)
            # worksheet1.write(i, 16,
            #                  asset.source_line_ids[0].purchase_id.partner_id.name if asset.source_line_ids else '',
            #                  left_table)

            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.asset.addition.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
