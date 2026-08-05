from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncFixAssetReport(models.TransientModel):
    _name = 'wizard.mnc.fix.asset.report'

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
        center_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_title_sub.set_font_size('13')
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
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('B:B', 15)
        worksheet1.set_column('C:C', 30)
        worksheet1.set_column('D:D', 10)
        worksheet1.set_column('E:E', 40)
        worksheet1.set_column('F:F', 15)
        worksheet1.set_column('G:G', 15)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 10)
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
        worksheet1.set_column('W:W', 15)
        worksheet1.set_column('X:X', 15)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " FA - Outstanding Asset Clearing"

        worksheet1.merge_range('A1:E1', 'RINCIAN FIXED ASSET CLEARING', left_title)
        worksheet1.merge_range('A2:E2', self.company_id.name, left_title)
        i = 2
        worksheet1.write(i, 0, 'Detailed List of', left_title_sub)
        worksheet1.write(i, 1,
                         ': ' + datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d-%b-%Y") + ' s/d ' + \
                         datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"), left_title_sub)
        i += 2
        worksheet1.write(i, 0, 'PO NUMBER', header_table)
        worksheet1.write(i, 1, 'COMPANY', header_table)
        worksheet1.write(i, 2, 'SUPPLIER NAME', header_table)
        worksheet1.write(i, 3, 'LINE PO', header_table)
        worksheet1.write(i, 4, 'DESCRIPTION', header_table)
        worksheet1.write(i, 5, 'AMOUNT PO', header_table)
        worksheet1.write(i, 6, 'AMOUNT PO IDR', header_table)
        worksheet1.write(i, 7, 'NO RR', header_table)
        worksheet1.write(i, 8, 'LINE RCV', header_table)
        worksheet1.write(i, 9, 'TGL RR', header_table)
        worksheet1.write(i, 10, 'CREATE ACCOUNTING RR', header_table)
        worksheet1.write(i, 11, 'AP MATCHING DATE', header_table)
        worksheet1.write(i, 12, 'INVOICE NUMBER', header_table)
        worksheet1.write(i, 13, 'CREATE ACCOUNTING AP', header_table)
        worksheet1.write(i, 14, 'ASSET NUMBER', header_table)
        worksheet1.write(i, 15, 'CREATE MA', header_table)
        worksheet1.write(i, 16, 'AMOUNT MASS ADDITION', header_table)
        worksheet1.write(i, 17, 'POST MA CREATE', header_table)
        worksheet1.write(i, 18, 'CREATE ACCOUNTING FA', header_table)
        worksheet1.write(i, 19, 'AMOUNT \nPOST MA', header_table)
        worksheet1.write(i, 20, 'SUM PO (IDR)', header_table)
        worksheet1.write(i, 21, 'ADJUSTMENT', header_table)
        worksheet1.write(i, 22, 'SUM POST MA', header_table)
        worksheet1.write(i, 22, 'OUTSTANDING', header_table)
        i += 1

        query = """ 
                    SELECT mvl.id
                        FROM account_move_line AS mvl
                            INNER JOIN account_move mv ON mv.id=mvl.move_id
                            INNER JOIN account_account acc ON acc.id=mvl.account_id
                    WHERE mvl.company_id=%s AND mvl.date>=%s AND mvl.date<=%s AND acc.code=%s AND mv.state='posted'
                    ORDER BY mvl.date asc
                """
        params = (self.company_id.id, self.start_date, self.end_date, '1239001',)

        self._cr.execute(query, params)
        move_ids = self.env['account.move.line'].sudo().browse([r[0] for r in self._cr.fetchall()])
        for move in move_ids:
            worksheet1.write(i, 0, move.move_id.po_numbers, left_table)
            worksheet1.write(i, 1, move.company_id.company_code, left_table)
            worksheet1.write(i, 2, move.partner_id.name, left_table)
            worksheet1.write(i, 3, move.line_number, center_table)
            worksheet1.write(i, 4, move.name, left_table)
            worksheet1.write(i, 5, move.amount_currency * -1 if move.amount_currency < 0 else move.amount_currency,
                             numb_table)
            worksheet1.write(i, 6, move.amount_currency * -1 if move.amount_currency < 0 else move.amount_currency,
                             numb_table)
            worksheet1.write(i, 7, move.move_id.rr_numbers, left_table)
            worksheet1.write(i, 8, move.line_number, center_table)
            worksheet1.write(i, 9, '', center_table)  # tgl_rr
            worksheet1.write(i, 10, '', center_table)  # create_acounting_rr
            worksheet1.write(i, 11, datetime.strptime(str(move.move_id.invoice_date), "%Y-%m-%d").strftime(
                "%d-%b-%Y") if move.move_id.invoice_date else '', center_table)
            worksheet1.write(i, 12, move.move_id.payment_reference if move.move_id.payment_reference else '',
                             left_table)
            worksheet1.write(i, 13,
                             datetime.strptime(str(move.date), "%Y-%m-%d").strftime("%d-%b-%Y") if move.date else '',
                             center_table)
            worksheet1.write(i, 14, move.move_id.asset_id.asset_no if move.move_id.asset_id.asset_no else '',
                             left_table)
            worksheet1.write(i, 15, datetime.strptime(str(move.move_id.asset_id.acquisition_date), "%Y-%m-%d").strftime(
                "%d-%b-%Y") if move.move_id.asset_id.acquisition_date else '', center_table)
            worksheet1.write(i, 16, move.move_id.asset_id.original_value if move.move_id.asset_id.original_value else 0,
                             numb_table)
            worksheet1.write(i, 17, datetime.strptime(str(move.move_id.asset_id.acquisition_date), "%Y-%m-%d").strftime(
                "%d-%b-%Y") if move.move_id.asset_id.acquisition_date else '', center_table)
            worksheet1.write(i, 18, datetime.strptime(str(move.move_id.asset_id.acquisition_date), "%Y-%m-%d").strftime(
                "%d-%b-%Y") if move.move_id.asset_id.acquisition_date else '', center_table)
            worksheet1.write(i, 19, move.move_id.asset_id.original_value if move.move_id.asset_id.original_value else 0,
                             numb_table)
            worksheet1.write(i, 20, move.move_id.asset_id.original_value if move.move_id.asset_id.original_value else 0,
                             numb_table)
            worksheet1.write(i, 21, 0, numb_table)  # sum_po_idr
            worksheet1.write(i, 22, move.move_id.asset_id.original_value if move.move_id.asset_id.original_value else 0,
                             numb_table)
            worksheet1.write(i, 22, 0, numb_table)  # outstanding
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.fix.asset.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
            self.id, filename),
            'target': 'new',
        }
