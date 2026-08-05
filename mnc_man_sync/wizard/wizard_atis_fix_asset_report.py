from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError, MissingError, Warning
import base64
from io import BytesIO
import xlsxwriter
import calendar
import math


class WizardAtisFixAssetReport(models.TransientModel):
    _name = 'wizard.atis.fix.asset.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    @api.model
    def get_year_selection(self):
        years = []
        show_year = 0
        next_year = datetime.today().year + 2
        while show_year < 10:
            years.append(next_year)
            next_year -= 1
            show_year += 1
        return [(str(year), str(year)) for year in years]

    @api.model
    def get_this_year(self):
        return str(datetime.today().year)

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    is_date_range = fields.Boolean(string="Custom Date Range", default=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    month = fields.Selection([
        ('01', 'Jan'), ('02', 'Feb'),
        ('03', 'Mar'), ('04', 'Apr'),
        ('05', 'May'), ('06', 'Jun'),
        ('07', 'Jul'), ('08', 'Aug'),
        ('09', 'Sep'), ('10', 'Oct'),
        ('11', 'Nov'), ('12', 'Dec')], string="Month")
    year = fields.Selection(selection="get_year_selection", default=get_this_year, string="Year")
    book_type = fields.Char(string="Book Type")
    file = fields.Binary('File')

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
        left_title_sub.set_font_size('14')
        center_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_title_sub.set_font_size('14')
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
        right_table = workbook.add_format({'valign': 'vcenter', 'align': 'right'})
        right_table.set_font_size('11')
        right_table.set_border()
        #################################################################################
        numb_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_table.set_font_size('11')
        numb_table.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 28)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 10)
        worksheet1.set_column('E:E', 70)
        worksheet1.set_column('F:G', 30)
        worksheet1.set_column('H:O', 20)
        worksheet1.set_column('P:Q', 33)
        worksheet1.set_column('R:W', 25)
        worksheet1.set_column('X:Z', 30)
        worksheet1.set_column('AA:AA', 50)
        worksheet1.set_column('AB:AD', 30)
        worksheet1.set_column('AE:AE', 20)
        worksheet1.set_column('AF:AF', 30)
        worksheet1.set_column('AG:AG', 35)
        worksheet1.set_column('AH:AH', 20)
        worksheet1.set_column('AI:AI', 30)
        worksheet1.set_column('AJ:AJ', 20)
        worksheet1.set_column('AK:AL', 15)
        worksheet1.set_column('AM:AM', 20)
        worksheet1.set_column('AN:AN', 20)
        worksheet1.set_column('AO:AO', 20)
        worksheet1.set_column('AP:AQ', 15)
        worksheet1.set_column('AR:AS', 20)
        worksheet1.set_column('AT:AT', 20)
        worksheet1.set_column('AU:AU', 30)
        worksheet1.set_column('AV:AW', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " ATIS - Fixed Asset Reconciled"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'Fixed Asset - ATIS Reconciled List', left_title_sub)
        i = 3
        if self.is_date_range:
            worksheet1.write(i, 0, 'Period', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d-%b-%Y") + ' to ' + \
                             datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"), left_title_sub)
        else:
            worksheet1.write(i, 0, 'As of Period', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, dict(self._fields['month'].selection).get(self.month) + '-' + self.year,
                             left_title_sub)
        # worksheet1.write(i, 4, 'Print Date', left_title_sub)
        # worksheet1.write(i, 5, ':', center_title_sub)
        # worksheet1.write(i, 6, datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
        #                  left_title_sub)
        i += 1
        # worksheet1.write(i, 0, 'Book Type', left_title_sub)
        # worksheet1.write(i, 1, ':', center_title_sub)
        # worksheet1.write(i, 2, '', left_title_sub)
        # i += 1
        worksheet1.write(i, 0, 'Print Date', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                         left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'User', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, self.env.user.name, left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'Book Type', header_table)
        worksheet1.write(i, 2, 'Asset Number', header_table)
        worksheet1.write(i, 3, 'Unit Qty', header_table)
        worksheet1.write(i, 4, 'Asset Description', header_table)
        worksheet1.write(i, 5, 'Major Category', header_table)
        worksheet1.write(i, 6, 'Minor Category', header_table)
        worksheet1.write(i, 7, 'Date In Service', header_table)
        worksheet1.write(i, 8, 'Prorate Convention', header_table)
        worksheet1.write(i, 9, 'Prorate Date', header_table)
        worksheet1.write(i, 10, 'Life In Months', header_table)
        worksheet1.write(i, 11, 'Life Years', header_table)
        worksheet1.write(i, 12, 'Remaining Life Years', header_table)
        worksheet1.write(i, 13, 'Remaining Life Months', header_table)
        worksheet1.write(i, 14, 'Fixed Asset Cost', header_table)
        worksheet1.write(i, 15, 'Accumulated Depreciation Cost', header_table)
        worksheet1.write(i, 16, 'Net Book Value', header_table)
        worksheet1.write(i, 17, 'Child Barcode', header_table)
        worksheet1.write(i, 18, 'Component Barcode', header_table)
        worksheet1.write(i, 19, 'Component Barcode Label', header_table)
        worksheet1.write(i, 20, 'Serial Number', header_table)
        worksheet1.write(i, 21, 'Tag Number', header_table)
        worksheet1.write(i, 22, 'Goods Brand', header_table)
        worksheet1.write(i, 23, 'Brand Model/Type', header_table)
        worksheet1.write(i, 24, 'Specification', header_table)
        worksheet1.write(i, 25, 'Condition', header_table)
        worksheet1.write(i, 26, 'Remarks', header_table)
        # worksheet1.write(i, 27, 'Payment Voucher', header_table)
        worksheet1.write(i, 27, 'Invoice Number', header_table)
        worksheet1.write(i, 28, 'Invoice Line Number', header_table)
        worksheet1.write(i, 29, 'Item Code', header_table)
        worksheet1.write(i, 30, 'Item Name', header_table)
        worksheet1.write(i, 31, 'Item Description', header_table)
        worksheet1.write(i, 32, 'PO Number', header_table)
        worksheet1.write(i, 33, 'PO Date', header_table)
        worksheet1.write(i, 34, 'PO Vendor Name', header_table)
        worksheet1.write(i, 35, 'PO Line Number', header_table)
        worksheet1.write(i, 36, 'PO Qty', header_table)
        worksheet1.write(i, 37, 'PO UoM', header_table)
        worksheet1.write(i, 38, 'PO UoM Description', header_table)
        worksheet1.write(i, 39, 'PR Number', header_table)
        worksheet1.write(i, 40, 'PR Date', header_table)
        worksheet1.write(i, 41, 'PR Line Number', header_table)
        worksheet1.write(i, 42, 'PR Qty', header_table)
        worksheet1.write(i, 43, 'PR Uom', header_table)
        worksheet1.write(i, 44, 'PR Uom Description', header_table)
        worksheet1.write(i, 45, 'ATIS Doc. Number', header_table)
        worksheet1.write(i, 46, 'ATIS Doc. Date', header_table)
        worksheet1.write(i, 47, 'ATIS Line Number', header_table)
        worksheet1.write(i, 48, 'Department Owner', header_table)
        i += 1

        query = """
                    SELECT ast.id
                        FROM account_asset AS ast
                            
                    WHERE ast.company_id=%s AND ast.state in ('open','close')
                """
        params = (self.company_id.id,)
        if self.is_date_range:
            query += ' AND ast.first_depreciation_date >= %s AND ast.first_depreciation_date <= %s'
            params += (self.start_date, self.end_date,)
        else:
            end_day = calendar.monthrange(int(self.year), int(self.month))[1]
            end_period = datetime.strptime(str(self.year) + '-' + str(self.month) + '-' + str(end_day), "%Y-%m-%d")

            query += " AND ast.first_depreciation_date <= %s"
            params += (end_period,)

        self._cr.execute(query, params)

        asset_ids = self.env['account.asset'].browse([r[0] for r in self._cr.fetchall()])
        for asset in asset_ids:
            if asset.asset_no:
                print("ASETTTTTTTTT", asset)
                self._cr.execute(
                    """ SELECT ast.id
                        FROM x_asset ast
                        WHERE ast.asset_number=%s
                        limit 1
                    """, (asset.asset_no,))
            else:
                raise Warning('Data tidak tersedia, silahkan cek kembali !!')

            x_asset_id = self.env['x.asset'].browse([r[0] for r in self._cr.fetchall()])

            worksheet1.merge_range(i, 0, i, 1, asset.company_id.name, left_table)  # book_type
            worksheet1.write(i, 2, asset.asset_no, left_table)  # asset_number
            worksheet1.write(i, 3, x_asset_id.unit_qty if x_asset_id else '', left_table)  # unit_qty
            worksheet1.write(i, 4, asset.name, left_table)  # asset_description
            worksheet1.write(i, 5, asset.model_id.segment_id.name or '', left_table)  # major_catageory
            worksheet1.write(i, 6, asset.model_id.name or '', left_table)  # minor_category
            worksheet1.write(i, 7, datetime.strptime(str(asset.first_depreciation_date), "%Y-%m-%d").strftime(
                "%d-%b-%y") if asset.first_depreciation_date else '', right_table)  # date_in_service
            worksheet1.write(i, 8, (x_asset_id.prorate_convention or '') if x_asset_id else '',
                             left_table)  # prorate_convention
            worksheet1.write(i, 9, datetime.strptime(str(asset.first_depreciation_date), "%Y-%m-%d").strftime(
                "%d-%b-%y") if asset.first_depreciation_date else '', right_table)  # prorate_date
            worksheet1.write(i, 10,
                             "{} Bulan".format(x_asset_id.life_in_months) if x_asset_id.life_in_months else '0 Bulan',
                             left_table)  # life_in_months
            worksheet1.write(i, 11, "{} Tahun".format(x_asset_id.life_year) if x_asset_id.life_year else '0 Tahun',
                             left_table)  # life_years

            life_years = x_asset_id.life_in_months - asset.total_depreciation
            result_months = life_years % 12
            result_years = math.floor(life_years / 12)
            # print(result_months)
            # print(result_years)
            # worksheet1.write(i, 12, math.floor(x_asset_id.life_year - asset.total_depreciation / 12) or 0,
            #                  left_table)  # remaining_life_years
            worksheet1.write(i, 12, "{} Tahun".format(result_years) if result_years else "0 Tahun",
                             left_table)  # remaining_life_years
            worksheet1.write(i, 13, "{} Bulan".format(result_months) if result_months else "0 Bulan",
                             left_table)  # remaining_life_months
            worksheet1.write(i, 14, asset.original_value or '', numb_table)  # fixed_asset_cost
            worksheet1.write(i, 15, asset.amount_depreciated or '', numb_table)  # accumulated_depreciation_cost
            worksheet1.write(i, 16, asset.book_value or '', numb_table)  # net_book_value
            worksheet1.write(i, 17, x_asset_id.child_barcode if x_asset_id else '', left_table)  # child_barcode
            worksheet1.write(i, 18, x_asset_id.component_barcode if x_asset_id else '', left_table)  # component_barcode
            worksheet1.write(i, 19, x_asset_id.component_barcode_label if x_asset_id else '',
                             left_table)  # component_barcode_label
            worksheet1.write(i, 20, (x_asset_id.serial_number or '') if x_asset_id else '', left_table)  # serial_number
            worksheet1.write(i, 21, (x_asset_id.tag_number or '') if x_asset_id else '', left_table)  # tag_number
            worksheet1.write(i, 22, x_asset_id.goods_brand if x_asset_id else '', left_table)  # goods_brand
            worksheet1.write(i, 23, x_asset_id.brand_model if x_asset_id else '', left_table)  # brand_model
            worksheet1.write(i, 24, x_asset_id.specification if x_asset_id else '', left_table)  # spesification
            worksheet1.write(i, 25, x_asset_id.condition if x_asset_id else '', left_table)  # condition
            worksheet1.write(i, 26, (x_asset_id.remarks or '') if x_asset_id else '', left_table)  # remarks
            # worksheet1.write(i, 27, x_asset_id.payment_voucher if x_asset_id else '', left_table)  # payment_voucher
            worksheet1.write(i, 27, (x_asset_id.invoice_number or '') if x_asset_id else '',
                             left_table)  # invoice_number
            worksheet1.write(i, 28, (x_asset_id.invoice_line_number or '') if x_asset_id else '',
                             left_table)  # invoice_line_number
            worksheet1.write(i, 29, (x_asset_id.item_code or '') if x_asset_id else '', left_table)  # item_code
            worksheet1.write(i, 30, (x_asset_id.item_name or '') if x_asset_id else '', left_table)  # item_name
            worksheet1.write(i, 31, x_asset_id.item_description if x_asset_id else '', left_table)  # item_description
            worksheet1.write(i, 32, x_asset_id.po_number if x_asset_id else '', left_table)  # po_number
            worksheet1.write(i, 33, x_asset_id.po_date if x_asset_id else '', left_table)  # po_date
            worksheet1.write(i, 34, x_asset_id.po_vendor_name if x_asset_id else '', left_table)  # po_vendor_name
            worksheet1.write(i, 35, x_asset_id.po_line_number if x_asset_id else '', left_table)  # po_line_number
            worksheet1.write(i, 36, x_asset_id.po_qty if x_asset_id else '', left_table)  # po_qty
            worksheet1.write(i, 37, (x_asset_id.po_uom or '') if x_asset_id else '', left_table)  # po_uom
            worksheet1.write(i, 38, (x_asset_id.po_uom_description or '') if x_asset_id else '',
                             left_table)  # po_uom_description
            worksheet1.write(i, 39, x_asset_id.pr_number if x_asset_id else '', left_table)  # pr_number
            worksheet1.write(i, 40, x_asset_id.pr_date if x_asset_id else '', left_table)  # pr_date
            worksheet1.write(i, 41, x_asset_id.pr_line_number if x_asset_id else '', left_table)  # pr_line_number
            worksheet1.write(i, 42, x_asset_id.pr_qty if x_asset_id else '', left_table)  # pr_qty
            worksheet1.write(i, 43, (x_asset_id.pr_uom or '') if x_asset_id else '', left_table)  # pr_uom
            worksheet1.write(i, 44, (x_asset_id.pr_uom_description or '') if x_asset_id else '',
                             left_table)  # pr_uom_description
            worksheet1.write(i, 45, x_asset_id.atis_doc_number if x_asset_id else '', left_table)  # atis_doc_number
            worksheet1.write(i, 46, x_asset_id.atis_doc_date if x_asset_id else '', left_table)  # atis_doc_date
            worksheet1.write(i, 47, x_asset_id.atis_line_number or '', left_table)  # atis_line_number
            worksheet1.write(i, 48, x_asset_id.department_owner if x_asset_id else '', left_table)  # department_owner
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.atis.fix.asset.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
