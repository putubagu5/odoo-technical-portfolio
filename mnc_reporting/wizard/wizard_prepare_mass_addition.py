from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar


class WizardPrepareMassAdditionReport(models.TransientModel):
    _name = 'wizard.prepare.mass.addition.report'

    @api.model
    def _get_default_company_id(self):
        return self.env.user.company_id.id

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

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=_get_default_company_id)
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
        numb_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_table.set_font_size('11')
        numb_table.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 35)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:E', 15)
        worksheet1.set_column('F:F', 2)
        worksheet1.set_column('G:G', 30)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 30)
        worksheet1.set_column('J:K', 30)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 35)
        worksheet1.set_column('N:P', 20)
        worksheet1.set_column('Q:Q', 30)
        worksheet1.set_column('R:R', 25)
        worksheet1.set_column('S:S', 50)
        worksheet1.set_column('T:T', 20)
        worksheet1.set_column('U:V', 25)
        worksheet1.set_column('W:W', 20)
        worksheet1.set_column('X:Y', 25)
        worksheet1.set_column('Z:AA', 15)
        worksheet1.set_column('AB:AB', 35)
        worksheet1.set_column('AC:AC', 30)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " MNC FA - Prepare Mass Addition Report"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'MNC FA - Prepare mass addition', left_title_sub)
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
        worksheet1.write(i, 0, 'Print Date', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                         left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'User', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, self.env.user.name, left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'Invoice Number', header_table)
        worksheet1.write(i, 2, 'Invoice Line', header_table)
        worksheet1.write(i, 3, 'Dist Line', header_table)
        worksheet1.merge_range(i, 4, i, 5, 'Queue', header_table)
        worksheet1.write(i, 6, 'Description', header_table)
        worksheet1.write(i, 7, 'Units', header_table)
        worksheet1.write(i, 8, 'Cost', header_table)
        worksheet1.write(i, 9, 'Major', header_table)
        worksheet1.write(i, 10, 'Minor', header_table)
        worksheet1.write(i, 11, 'Vendor Number', header_table)
        worksheet1.write(i, 12, 'Vendor Name', header_table)
        worksheet1.write(i, 13, 'PO Number', header_table)
        worksheet1.write(i, 14, 'Create Batch', header_table)
        worksheet1.write(i, 15, 'Create Date', header_table)
        worksheet1.write(i, 16, 'Source System', header_table)
        worksheet1.write(i, 17, 'Invoice Date', header_table)
        worksheet1.write(i, 18, 'Clearing Account', header_table)
        worksheet1.write(i, 19, 'Asset Type', header_table)
        worksheet1.write(i, 20, 'In Physical Inventory', header_table)
        worksheet1.write(i, 21, 'Book', header_table)
        worksheet1.write(i, 22, 'Depreciate', header_table)
        worksheet1.write(i, 23, 'Date In Service', header_table)
        worksheet1.write(i, 24, 'Depreciate Method', header_table)
        worksheet1.write(i, 25, 'Life Year', header_table)
        worksheet1.write(i, 26, 'Life Month', header_table)
        worksheet1.write(i, 27, 'Delivery Address PO', header_table)
        worksheet1.write(i, 28, 'Requestor PR', header_table)
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
            print("ASETTTTTTTTT", asset)
            self._cr.execute(
                """ SELECT ast.id
                        FROM x_asset ast
                    WHERE ast.asset_number=%s 
                    limit 1
                """, (asset.asset_no,))

            x_asset_id = self.env['x.asset'].browse([r[0] for r in self._cr.fetchall()])

            # for line in asset.source_line_ids:
            worksheet1.merge_range(i, 0, i, 1, asset.name or '', left_table)
            worksheet1.write(i, 2, '', left_table)
            worksheet1.write(i, 3, '', left_table)
            worksheet1.merge_range(i, 4, i, 5, '', left_table)
            worksheet1.write(i, 6, '', left_table)
            worksheet1.write(i, 7, '', left_table)
            worksheet1.write(i, 8, '', left_table)
            worksheet1.write(i, 9, '', left_table)
            worksheet1.write(i, 10, '', left_table)
            worksheet1.write(i, 11, '', left_table)
            worksheet1.write(i, 12, '', left_table)
            worksheet1.write(i, 13, '', left_table)
            worksheet1.write(i, 14, '', left_table)
            worksheet1.write(i, 15, '', numb_table)
            worksheet1.write(i, 16, '', numb_table)
            worksheet1.write(i, 17, '', numb_table)
            worksheet1.write(i, 18, '', left_table)
            worksheet1.write(i, 19, '', left_table)
            worksheet1.write(i, 20, '', left_table)
            worksheet1.write(i, 21, '', left_table)
            worksheet1.write(i, 22, '', left_table)
            worksheet1.write(i, 23, '', left_table)
            worksheet1.write(i, 24, '', left_table)
            worksheet1.write(i, 25, '', left_table)
            worksheet1.write(i, 26, '', left_table)
            worksheet1.write(i, 27, '', left_table)
            worksheet1.write(i, 28, '', left_table)
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.prepare.mass.addition.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
