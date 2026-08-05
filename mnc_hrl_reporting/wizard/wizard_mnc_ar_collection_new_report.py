from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncArCollectionNewReport(models.TransientModel):
    _name = 'wizard.mnc.ar.collection.new.report'

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
    month = fields.Selection([
        ('01', 'Jan'), ('02', 'Feb'),
        ('03', 'Mar'), ('04', 'Apr'),
        ('05', 'May'), ('06', 'Jun'),
        ('07', 'Jul'), ('08', 'Aug'),
        ('09', 'Sep'), ('10', 'Oct'),
        ('11', 'Nov'), ('12', 'Dec')], string="Month")
    year = fields.Selection(selection="get_year_selection", default=get_this_year, string="Year")
    is_date_range = fields.Boolean(string="Custom Date Range", default=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    all_partner = fields.Boolean(string="All Customer", default=True)
    partner_ids = fields.Many2many("res.partner", string="Customer")
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
        center_title = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'center'})
        center_title.set_font_size('15')
        right_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'right'})
        right_title_sub.set_font_size('12')
        center_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_title_sub.set_font_size('14')
        #################################################################################
        left_title_sub = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title_sub.set_font_size('12')
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
        right_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer.set_font_size('12')
        right_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('12')
        numb_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 20)
        worksheet1.set_column('B:B', 25)
        worksheet1.set_column('C:C', 25)
        worksheet1.set_column('D:D', 25)
        worksheet1.set_column('E:E', 25)
        worksheet1.set_column('F:F', 25)
        worksheet1.set_column('G:G', 20)
        worksheet1.set_column('H:H', 20)
        worksheet1.set_column('I:I', 20)
        worksheet1.set_column('J:J', 20)
        worksheet1.set_column('K:K', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AR - Collection Detail Report (new)"

        worksheet1.merge_range('A1:K1', 'Print Date : ' + datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime(
            "%d-%b-%Y %H:%M:%S"), right_title_sub)
        worksheet1.merge_range('A2:K2', 'COLLECTION DETAIL REPORT', center_title)
        worksheet1.merge_range('A3:K3', self.company_id.name, center_title)
        if self.is_date_range:
            worksheet1.merge_range('A4:K4', 'Period : ' + datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime(
                "%d-%b-%Y") + ' s/d ' + \
                                   datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                   center_title_sub)
        else:
            worksheet1.merge_range('A4:K4', 'As of Period : ' + dict(self._fields['month'].selection).get(
                self.month) + '-' + self.year, center_title_sub)

        i = 5
        move_vals = []

        query = """ 
                    SELECT mv.id
                        FROM account_move AS mv
                            INNER JOIN res_partner rp ON rp.id=mv.partner_id
                    WHERE mv.partner_id IS NOT NULL AND mv.company_id=%s AND mv.move_type='out_invoice' AND mv.state='posted'
                """
        params = (self.company_id.id,)

        if not self.all_partner:
            query += ' AND mv.partner_id IN %s'
            params += (tuple(self.partner_ids.ids),)
        if self.is_date_range:
            query += ' AND mv.invoice_date >= %s AND mv.invoice_date <= %s'
            params += (self.start_date, self.end_date,)
        else:
            end_day = calendar.monthrange(int(self.year), int(self.month))[1]
            end_period = datetime.strptime(str(self.year) + '-' + str(self.month) + '-' + str(end_day), "%Y-%m-%d")

            query += " AND mv.invoice_date <= %s"
            params += (end_period,)
        query += ' ORDER BY rp.name asc'

        self._cr.execute(query, params)
        move_ids = self.env['account.move'].sudo().browse([r[0] for r in self._cr.fetchall()])
        for move in move_ids:
            self._cr.execute(
                """ SELECT SUM(mv.amount_total)
                        FROM account_move mv
                    WHERE mv.partner_id=%s AND mv.company_id=%s AND mv.move_type='out_refund' AND mv.state='posted' AND mv.ref LIKE %s
                """, (move.partner_id.id, move.company_id.id, '%' + move.name + '%',))
            amount_credit_memo = self.env.cr.fetchone()[0] or 0.0

            move_vals.append({
                'partner_id': move.partner_id.id,
                'number': move.name,
                'invoice_number': move.payment_reference,
                'receipt_number': move.applied_misc_ids[0].misc_id.receipt_number if move.applied_misc_ids else '',
                'advertiser_gen21': move.advertiser_gen21,
                'product_gen21': move.product_gen21,
                'po_numbers_gen21': move.po_numbers_gen21,
                'sales_person_gen21': move.sales_person_gen21,
                'amount_total': move.amount_total,
                'amount_adjustment': move.adjustment_amount,
                'amount_credit_memo': amount_credit_memo,
                'amount_payment': move.amount_total - move.amount_residual,
                'amount_outstanding': move.amount_residual,
            })

        grouped = collections.defaultdict(list)
        for item in move_vals:
            grouped[item['partner_id']].append(item)

        for partner, items in grouped.items():
            partner_id = self.env['res.partner'].sudo().browse(partner)

            worksheet1.merge_range(i, 0, i, 10, 'Customer Name : ' + partner_id.name, left_title_sub)
            i += 1
            worksheet1.write(i, 0, 'Invoice Number', header_table)
            worksheet1.write(i, 1, 'Receipt No', header_table)
            worksheet1.write(i, 2, 'Advertiser', header_table)
            worksheet1.write(i, 3, 'Brand', header_table)
            worksheet1.write(i, 4, 'PO#', header_table)
            worksheet1.write(i, 5, 'Sales', header_table)
            worksheet1.write(i, 6, 'Invoice Amount', header_table)
            worksheet1.write(i, 7, 'Adjustment Amount', header_table)
            worksheet1.write(i, 8, 'Credit Memo Amount', header_table)
            worksheet1.write(i, 9, 'Receipt Amount', header_table)
            worksheet1.write(i, 10, 'Outstanding Amount', header_table)
            i += 1

            for item in items:
                worksheet1.write(i, 0, item['invoice_number'], left_table)
                worksheet1.write(i, 1, item['receipt_number'] if item['receipt_number'] else '', left_table)
                worksheet1.write(i, 2, item['advertiser_gen21'] if item['advertiser_gen21'] else '', left_table)
                worksheet1.write(i, 3, item['product_gen21'] if item['product_gen21'] else '', left_table)
                worksheet1.write(i, 4, item['po_numbers_gen21'] if item['po_numbers_gen21'] else '', left_table)
                worksheet1.write(i, 5, item['sales_person_gen21'] if item['sales_person_gen21'] else '', left_table)
                worksheet1.write(i, 6, item['amount_total'], numb_table)
                worksheet1.write(i, 7, item['amount_adjustment'], numb_table)
                worksheet1.write(i, 8, item['amount_credit_memo'], numb_table)
                worksheet1.write(i, 9, item['amount_payment'], numb_table)
                worksheet1.write(i, 10, item['amount_outstanding'], numb_table)
                i += 1

            worksheet1.write(i, 0, '', left_footer)
            worksheet1.write(i, 1, '', left_footer)
            worksheet1.write(i, 2, '', left_footer)
            worksheet1.write(i, 3, '', left_footer)
            worksheet1.write(i, 4, '', left_footer)
            worksheet1.write(i, 5, 'Sub Total', left_footer)
            worksheet1.write(i, 6, sum(item['amount_total'] for item in items), numb_footer)
            worksheet1.write(i, 7, sum(item['amount_adjustment'] for item in items), numb_footer)
            worksheet1.write(i, 8, sum(item['amount_credit_memo'] for item in items), numb_footer)
            worksheet1.write(i, 9, sum(item['amount_payment'] for item in items), numb_footer)
            worksheet1.write(i, 10, sum(item['amount_outstanding'] for item in items), numb_footer)
            i += 2

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ar.collection.new.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
