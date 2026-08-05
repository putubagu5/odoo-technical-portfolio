from calendar import monthrange
from datetime import datetime, date
from io import BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name as xlcol
from odoo import api, fields, models


LAST_2_YEARS = datetime.now().year - 2
NEXT_2_YEARS = datetime.now().year + 2
CURRENT_YEAR = datetime.now().year
YEARS = [(str(year), str(year)) for year in range(LAST_2_YEARS, NEXT_2_YEARS)]


class AssetDetailReport(models.TransientModel):
    _name = 'wizard.asset.detail.report'
    _description = 'Asset Detail Report'

    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], 'Month', default=str(datetime.now().month))
    year = fields.Selection(YEARS, 'Year', default=str(CURRENT_YEAR))
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)

    def _get_month_dict(self):
        """ helper function to get month dictionary """
        month_dict = {str(k): 0 for k in range(1, 13)}
        return month_dict

    def _group_data(self, data: list) -> dict:
        """ helper function to group data """
        group_data = {}
        # loop and generate dict. Keys: Segment -> Category -> list of data
        for dt in data:
            group_data.setdefault(dt['segment'], {})
            group_data[dt['segment']].setdefault(dt['category'], [])
            group_data[dt['segment']][dt['category']].append(dt.values())
        return group_data

    def _prepare_report_data(self):
        """ function to prepare report data containing a dict """
        result = {}
        ast_dict = {}
        ast_data = []
        # find acquisition_date with the same year
        month = int(self.month)
        year = int(self.year)
        _, day = monthrange(year, month)
        # ('acquisition_date', '>=', date(year, month, 1)),
        domain = [
            ('acquisition_date', '<=', date(year, month, day)),
            ('company_id', '=', self.company_id.id),
            ('state', 'not in', ('model', 'draft')),
        ]
        assets = self.env['account.asset'].search(domain)
        for ast in assets:
            if not ast.model_id.segment_id or not ast.model_id:
                continue  # skip if no segment or category

            origin = ast.origin_ids[0] if ast.origin_ids else False
            invoice = origin.move_id if origin else False
            life_year = ast.method_number // (12 if ast.method_period == '1' else 1)
            life_month = (ast.method_number % 12) if ast.method_period == '1' else 0
            data = {
                'segment': ast.model_id.segment_id,
                'category': ast.model_id,
                'number': ast.asset_no,
                'tag': ast.tag_number or '',
                'serial': ast.serial_number or '',
                'supplier': origin.partner_id.name if origin else '',
                'pr': '',
                'po': '',
                'rr': '',
                'invoice': invoice.name if invoice else '',
                'name': ast.name,
                'company': ast.company_id.name,
                'location': ast.last_location_id.name or '',
                'expense_account': ast.account_depreciation_expense_id.display_name,
                'qty': ast.qty,
                'uom': '',
                'date_in_service': invoice.invoice_date.strftime('%d/%m/%Y') if invoice else '',
                'life_year': life_year,
                'life_month': life_month,
                'remaining_year': '',
                'remaining_month': '',
                'cost_begin': ast.original_value,
                'cost_add': ast.gross_increase_value,
                'cost_adjustment': 0,
                'cost_end': ast.original_value + ast.gross_increase_value + 0,
            }

            # month_data = self._get_month_dict()
            lines = ast.depreciation_line_ids[0] if ast.depreciation_line_ids else False
            depre_month_1 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 1 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_2 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 2 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_3 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 3 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_4 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 4 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_5 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 5 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_6 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 6 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_7 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 7 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_8 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 8 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_9 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 9 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_10 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 10 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_11 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 11 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_12 = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 12 and r.depreciation_date.year == year and r.move_posted_check is True)
            depre_month_last = ast.depreciation_line_ids.filtered(lambda r: r.depreciation_date.month == 12 and r.depreciation_date.year == year - 1)

            depre_data_1 = sum(x.amount for x in depre_month_1) if depre_month_1 else 0
            depre_data_2 = sum(x.amount for x in depre_month_2) if depre_month_2 else 0
            depre_data_3 = sum(x.amount for x in depre_month_3) if depre_month_3 else 0
            depre_data_4 = sum(x.amount for x in depre_month_4) if depre_month_4 else 0
            depre_data_5 = sum(x.amount for x in depre_month_5) if depre_month_5 else 0
            depre_data_6 = sum(x.amount for x in depre_month_6) if depre_month_6 else 0
            depre_data_7 = sum(x.amount for x in depre_month_7) if depre_month_7 else 0
            depre_data_8 = sum(x.amount for x in depre_month_8) if depre_month_8 else 0
            depre_data_9 = sum(x.amount for x in depre_month_9) if depre_month_9 else 0
            depre_data_10 = sum(x.amount for x in depre_month_10) if depre_month_10 else 0
            depre_data_11 = sum(x.amount for x in depre_month_11) if depre_month_11 else 0
            depre_data_12 = sum(x.amount for x in depre_month_12) if depre_month_12 else 0
            depre_data_last = sum(x.amount for x in depre_month_last) if depre_month_last else 0

            total_depre = depre_data_1 + depre_data_2 + depre_data_3 + depre_data_4 + depre_data_5 + depre_data_6 + depre_data_7 + depre_data_8 + depre_data_9 + depre_data_10 + depre_data_11 + depre_data_12

            # lines_all = ast.depreciation_move_ids
            residual = lines.remaining_value if lines else 0
            book_begin = lines.remaining_value + lines.amount if lines else 0
            acc_end = depre_data_last + total_depre + 0
            # amount = sum(x.asset_remaining_value for x in lines)
            # month_data[self.month] = amount
            # month_dict = {str(k): residual for k in range(1, 13)}
            month_amount_data = {
                '1': depre_data_1,
                '2': depre_data_2,
                '3': depre_data_3,
                '4': depre_data_4,
                '5': depre_data_5,
                '6': depre_data_6,
                '7': depre_data_7,
                '8': depre_data_8,
                '9': depre_data_9,
                '10': depre_data_10,
                '11': depre_data_11,
                '12': depre_data_12,
            }
            data.update(month_amount_data)

            # lazy things
            next_data = {
                'acc_begin': depre_data_last,
                'acc_add': total_depre,
                'acc_adjustment': 0,
                'acc_end': acc_end,
                'book_begin': book_begin,
                'book_end': book_begin - acc_end,
            }
            data.update(next_data)
            ast_data.append(data)

        # group by Segment -> Category
        result = self._group_data(ast_data)

        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'Asset Detail %s' % (self.year)
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_xlsx(self, response, data={}):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('Asset Detail')

        # styles
        white_bg = wb.add_format({'bg_color': 'white'})

        # title: bold 14 center
        s_title = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 14, 'font_name': 'Arial',
            'valign': 'vcenter',
        })

        # header: 8 bold border center
        s_header = wb.add_format({
            'bold': 1, 'align': 'center', 'font_name': 'Arial', 'font_size': 8,
            'valign': 'vcenter', 'num_format': '#,###', 'border': 1,
        })

        # normal: 8 border
        s_normal = wb.add_format({
            'font_name': 'Arial', 'font_size': 8, 'num_format': '#,###',
            'border': 1,
        })

        # normal_bold: 8 border bold
        s_normal_bold = wb.add_format({
            'font_name': 'Arial', 'font_size': 8, 'num_format': '#,###',
            'border': 1, 'bold': 1,
        })

        # set column width
        widths = [25, 36.5, 12.5, 10.5, 12.2, 36.5, 5.5, 5.5, 5.5, 33, 36.5,
                  14.5, 35.5, 26.5, 14, 5.3, 12.5, 4.5, 6, 4.5, 6, 23, 7.5,
                  11, 23, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 23,
                  7.5, 14, 23, 23, 23]
        for idx, width in enumerate(widths):
            ws.set_column(idx, idx, width, white_bg)

        row = col = 0

        period = date(int(self.year), int(self.month), 1)
        str_year = period.strftime('%y')
        period = period.strftime('%b %Y')
        ws.merge_range('A1:AQ1', self.company_id.name, s_title)
        ws.merge_range('A2:AQ2', 'MNC ASSET BOOK COMMERCIAL', s_title)
        ws.merge_range('A3:AQ3', 'Report Details', s_title)
        ws.merge_range('A4:AQ4', 'Laporan Daftar Aktiva Tetap', s_title)
        ws.merge_range('A5:AQ5', 'Periode : %s' % (period), s_title)

        # headers are directly generated due to the fixed nature
        ws.merge_range('A7:B7', 'Asset Category', s_header)
        ws.write('A8', 'Major', s_header)
        ws.write('B8', 'Minor', s_header)
        ws.merge_range('C7:C8', 'Asset Number', s_header)
        ws.merge_range('D7:D8', 'Tag Number', s_header)
        ws.merge_range('E7:E8', 'Serial Number', s_header)
        ws.merge_range('F7:F8', 'Supplier Name', s_header)
        ws.merge_range('G7:G8', 'PR', s_header)
        ws.merge_range('H7:H8', 'PO', s_header)
        ws.merge_range('I7:I8', 'RR', s_header)
        ws.merge_range('J7:J8', 'INV', s_header)
        ws.merge_range('K7:K8', 'Asset Description', s_header)
        ws.merge_range('L7:N7', 'Location', s_header)
        ws.write('L8', 'Company', s_header)
        ws.write('M8', 'Location', s_header)
        ws.write('N8', 'Expense', s_header)
        ws.merge_range('O7:O8', 'Quantity', s_header)
        ws.merge_range('P7:P8', 'UOM', s_header)
        ws.merge_range('Q7:Q8', 'Date in Service', s_header)
        ws.merge_range('R7:S7', 'Life', s_header)
        ws.write('R8', 'Year', s_header)
        ws.write('S8', 'Month', s_header)
        ws.merge_range('T7:U7', 'Remaining', s_header)
        ws.write('T8', 'Year', s_header)
        ws.write('U8', 'Month', s_header)
        ws.merge_range('V7:Y7', 'At Cost', s_header)
        ws.write('V8', 'Acquisition Value', s_header)
        ws.write('W8', 'Addition', s_header)
        ws.write('X8', 'Adjustment', s_header)
        ws.write('Y8', 'Ending Balance', s_header)
        ws.merge_range('Z7:Z8', 'Jan-%s' % (str_year), s_header)
        ws.merge_range('AA7:AA8', 'Feb-%s' % (str_year), s_header)
        ws.merge_range('AB7:AB8', 'Mar-%s' % (str_year), s_header)
        ws.merge_range('AC7:AC8', 'Apr-%s' % (str_year), s_header)
        ws.merge_range('AD7:AD8', 'May-%s' % (str_year), s_header)
        ws.merge_range('AE7:AE8', 'Jun-%s' % (str_year), s_header)
        ws.merge_range('AF7:AF8', 'Jul-%s' % (str_year), s_header)
        ws.merge_range('AG7:AG8', 'Aug-%s' % (str_year), s_header)
        ws.merge_range('AH7:AH8', 'Sep-%s' % (str_year), s_header)
        ws.merge_range('AI7:AI8', 'Oct-%s' % (str_year), s_header)
        ws.merge_range('AJ7:AJ8', 'Nov-%s' % (str_year), s_header)
        ws.merge_range('AK7:AK8', 'Dec-%s' % (str_year), s_header)
        ws.merge_range('AL7:AO7', 'Accumulated Depreciation', s_header)
        ws.write('AL8', 'Beginning Balance', s_header)
        ws.write('AM8', 'Addition', s_header)
        ws.write('AN8', 'Adjustment', s_header)
        ws.write('AO8', 'Ending Balance', s_header)
        ws.merge_range('AP7:AQ7', 'Book Value', s_header)
        ws.write('AP8', 'Beginning Balance', s_header)
        ws.write('AQ8', 'Ending Balance', s_header)

        row += 8

        # loop by each group, each group will have list of data
        grand_list = []
        for sg, info in data.items():
            for categ, cinfo in info.items():
                tmp_list = []
                start = row + 1  # real row
                end = row + 1  # real row
                for linfo in cinfo:
                    # print by segment and category (1 segment, n categories)
                    ws.write(row, col, sg.name, s_normal)
                    ws.write(row, col + 1, categ.name, s_normal)
                    for idx, item in enumerate(linfo):
                        if idx not in (0, 1):
                            ws.write(row, col + idx, item, s_normal)
                    row += 1
                    end = row
                ws.write(row, col, 'Subtotal', s_normal_bold)
                ws.merge_range(row, col + 1, row, col + 20,
                               '%s %s' % (sg.name, categ.name), s_normal_bold)
                # from V to AQ sum
                start_col = 21  # V
                end_col = 42  # AQ
                for i in range(start_col, end_col + 1):
                    cell = xlcol(i)
                    scell = '%s%s' % (cell, start)
                    ecell = '%s%s' % (cell, end)
                    formula = '=SUM(%s:%s)' % (scell, ecell)
                    vcell = '%s%s' % (cell, row + 1)  # the cell with amount
                    ws.write(vcell, formula, s_normal_bold)
                    tmp_list.append(vcell)
                row += 1
                grand_list.append(tmp_list)

        if data:
            # grand total
            grand_list = list(map(lambda x: ','.join(x), zip(*grand_list)))
            ws.merge_range(row, col, row, col + 20, 'Grand Total', s_normal_bold)
            # from V to AQ sum
            start_col = 21  # V
            end_col = 42  # AQ
            for idx, i in enumerate(range(start_col, end_col + 1)):
                ws.write(row, i, '=SUM(%s)' % grand_list[idx], s_normal_bold)

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
