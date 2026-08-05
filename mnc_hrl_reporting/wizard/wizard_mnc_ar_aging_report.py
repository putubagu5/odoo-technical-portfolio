from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncArAgingReport(models.TransientModel):
    _name = 'wizard.mnc.ar.aging.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    as_of_date = fields.Date(string="As of Date")
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

    def get_partner_name(self):
        self.ensure_one()

        partner_name = ''
        for partner in self.partner_ids:
            if partner_name == '':
                partner_name = partner.name
            else:
                partner_name += ', ' + partner.name

        return partner_name

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
        int_table = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0'})
        int_table.set_font_size('11')
        int_table.set_border()
        #################################################################################
        left_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_footer.set_font_size('11')
        left_footer.set_border()
        #################################################################################
        right_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        right_footer.set_font_size('11')
        right_footer.set_border()
        #################################################################################
        numb_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_footer.set_font_size('11')
        numb_footer.set_border()
        #################################################################################
        percent_footer = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '0.00%'})
        percent_footer.set_font_size('11')
        percent_footer.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 20)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 15)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 20)
        worksheet1.set_column('G:G', 15)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 10)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 15)
        worksheet1.set_column('N:N', 15)
        worksheet1.set_column('O:O', 15)
        worksheet1.set_column('P:P', 15)
        worksheet1.set_column('Q:Q', 15)
        worksheet1.set_column('R:R', 15)
        worksheet1.set_column('S:S', 15)
        worksheet1.set_column('T:T', 15)
        worksheet1.set_column('U:U', 10)
        worksheet1.set_column('V:V', 15)
        worksheet1.set_column('W:W', 15)
        worksheet1.set_column('X:X', 15)
        worksheet1.set_column('Y:Y', 15)
        worksheet1.set_column('Z:Z', 15)
        worksheet1.set_column('AA:AA', 15)
        worksheet1.set_column('AB:AB', 15)
        worksheet1.set_column('AC:AC', 15)
        worksheet1.set_column('AD:AD', 15)
        worksheet1.set_column('AE:AE', 15)
        worksheet1.set_column('AF:AF', 15)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " AR - Aging Report Details"

        worksheet1.merge_range('A1:D1', self.company_id.name, left_title)
        worksheet1.merge_range('A2:D2', 'AR Aging Report Details', left_title)
        i = 2
        worksheet1.write(i, 0, 'As of Date', left_title_sub)
        worksheet1.merge_range(i, 1, i, 2,
                               ': ' + datetime.strptime(str(self.as_of_date), "%Y-%m-%d").strftime("%d %B %Y"),
                               left_title_sub)
        i += 1
        worksheet1.write(i, 0, 'Print Date', left_title_sub)
        worksheet1.merge_range(i, 1, i, 2,
                               ': ' + datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                               left_title_sub)
        i += 2

        worksheet1.merge_range(i, 0, i, 1, 'Customer Name', header_table)
        worksheet1.write(i, 2, 'Customer Number', header_table)
        worksheet1.write(i, 3, 'Product', header_table)
        worksheet1.write(i, 4, 'PO Number', header_table)
        worksheet1.write(i, 5, 'Advertiser', header_table)
        worksheet1.write(i, 6, 'PO Type', header_table)
        worksheet1.write(i, 7, 'Transaction Type', header_table)
        worksheet1.write(i, 8, 'Invoice Number', header_table)
        worksheet1.write(i, 9, 'Invoice Date', header_table)
        worksheet1.write(i, 10, 'Due Days', header_table)
        worksheet1.write(i, 11, 'Due Date', header_table)
        worksheet1.write(i, 12, 'Present Period \n(Period Tayang)', header_table)
        worksheet1.write(i, 13, 'Invoice Amount \n(DPP)', header_table)
        worksheet1.write(i, 14, 'Tax Amout \n(PPn)', header_table)
        worksheet1.write(i, 15, 'Total Invoice Amount', header_table)
        worksheet1.write(i, 16, 'Income Tax \n(PPh 23)', header_table)
        worksheet1.write(i, 17, 'Adjustment', header_table)
        worksheet1.write(i, 18, 'Paid Amount', header_table)
        worksheet1.write(i, 19, 'Outstanding Amount', header_table)
        worksheet1.write(i, 20, 'Ages \n(Days)', header_table)
        worksheet1.write(i, 21, 'Current Amount', header_table)
        worksheet1.write(i, 22, 'Bucket \n1-30 Days', header_table)
        worksheet1.write(i, 23, 'Bucket \n31-60 Days', header_table)
        worksheet1.write(i, 24, 'Bucket \n61-90 Days', header_table)
        worksheet1.write(i, 25, 'Bucket \n91-365 Days', header_table)
        worksheet1.write(i, 26, '> 365 Days', header_table)
        worksheet1.write(i, 27, 'Receipt Number', header_table)
        worksheet1.write(i, 28, 'Receipt Date', header_table)
        worksheet1.write(i, 29, 'Receipt Method', header_table)
        worksheet1.write(i, 30, 'Receipt GL Date', header_table)
        worksheet1.write(i, 31, 'Receipt Amount', header_table)
        i += 1

        query = """ 
                    SELECT mv.id
                        FROM account_move AS mv
                            INNER JOIN res_partner rp ON rp.id=mv.partner_id
                    WHERE mv.partner_id IS NOT NULL AND mv.company_id=%s AND mv.move_type='out_invoice' AND mv.state='posted'
                """
        params = (self.company_id.id,)
        if self.as_of_date:
            query += " AND mv.invoice_date <= %s"
            params += (self.as_of_date,)

        if not self.all_partner:
            query += ' AND mv.partner_id IN %s'
            params += (tuple(self.partner_ids.ids),)

        query += ' ORDER BY rp.name asc'

        self._cr.execute(query, params)
        data_vals = []

        invoice_ids = self.env['account.move'].browse([r[0] for r in self._cr.fetchall()])
        for inv in invoice_ids:

            amount_outstanding = inv.amount_residual
            current_amount = 0
            amount_1_30 = 0
            amount_31_60 = 0
            amount_61_90 = 0
            amount_91_365 = 0
            amount_365 = 0

            due_day = int((datetime.strptime(str(inv.invoice_date_due), "%Y-%m-%d") - datetime.strptime(
                str(inv.invoice_date), "%Y-%m-%d")).days)
            aged_day = int((datetime.strptime(str(self.as_of_date), "%Y-%m-%d") - datetime.strptime(
                str(inv.invoice_date_due), "%Y-%m-%d")).days)

            if aged_day <= 0:
                current_amount = amount_outstanding
            elif aged_day >= 1 and aged_day <= 30:
                amount_1_30 = amount_outstanding
            elif aged_day >= 31 and aged_day <= 60:
                amount_31_60 = amount_outstanding
            elif aged_day >= 61 and aged_day <= 90:
                amount_61_90 = amount_outstanding
            elif aged_day >= 91 and aged_day <= 365:
                amount_91_365 = amount_outstanding
            elif aged_day > 365:
                amount_365 = amount_outstanding

            data_vals.append({
                'partner_id': inv.partner_id.id,
                'partner_name': inv.partner_id.name,
                'partner_number': inv.partner_id.partner_no,
                'product_name': inv.product_gen21,
                'po_number': inv.po_numbers,
                'advertiser': inv.advertiser_gen21,
                'po_type': inv.po_type_gen21,
                'transaction_type': inv.transaction_type_id.name,
                'invoice_number': inv.name,
                'invoice_date': inv.invoice_date,
                'due_day': due_day,
                'due_date': inv.invoice_date_due,
                'present_period': '',
                'amount_untaxed': inv.amount_untaxed,
                'amount_ppn': inv.amount_tax,
                'amount_total': inv.amount_total,
                'amount_pph': 0,
                'amount_adjustment': inv.adjustment_amount,
                'amount_paid': inv.amount_total - amount_outstanding,
                'amount_outstanding': amount_outstanding,
                'aged_day': aged_day,
                'current_amount': current_amount,
                'amount_1_30': amount_1_30,
                'amount_31_60': amount_31_60,
                'amount_61_90': amount_61_90,
                'amount_91_365': amount_91_365,
                'amount_365': amount_365,
                'receipt_number': inv.applied_misc_ids[0].misc_id.receipt_number if inv.applied_misc_ids else '',
                'receipt_date': inv.applied_misc_ids[0].transaction_date if inv.applied_misc_ids else '',
                'receipt_method': '',
                'receipt_gl_date': inv.applied_misc_ids[0].misc_id.date if inv.applied_misc_ids else '',
                'receipt_amount': inv.applied_misc_ids[0].misc_id.amount if inv.applied_misc_ids else 0
            })

        grouped = collections.defaultdict(list)
        for item in data_vals:
            grouped[item['partner_id']].append(item)

        for partner, items in grouped.items():
            partner_id = self.env['res.partner'].sudo().browse(partner)

            for item in items:
                worksheet1.merge_range(i, 0, i, 1, item['partner_name'], left_table)
                worksheet1.write(i, 2, item['partner_number'] if item['partner_number'] else '', left_table)
                worksheet1.write(i, 3, item['product_name'] if item['product_name'] else '', left_table)
                worksheet1.write(i, 4, item['po_number'] if item['po_number'] else '', left_table)
                worksheet1.write(i, 5, item['advertiser'] if item['advertiser'] else '', left_table)
                worksheet1.write(i, 6, item['po_type'] if item['po_type'] else '', left_table)
                worksheet1.write(i, 7, item['transaction_type'], left_table)
                worksheet1.write(i, 8, item['invoice_number'], left_table)
                worksheet1.write(i, 9,
                                 datetime.strptime(str(item['invoice_date']), "%Y-%m-%d").strftime("%d-%b-%y") if item[
                                     'invoice_date'] else '', left_table)
                worksheet1.write(i, 10, item['due_day'], int_table)
                worksheet1.write(i, 11,
                                 datetime.strptime(str(item['due_date']), "%Y-%m-%d").strftime("%d-%b-%y") if item[
                                     'due_date'] else '', left_table)
                worksheet1.write(i, 12, item['present_period'], left_table)
                worksheet1.write(i, 13, item['amount_untaxed'], numb_table)
                worksheet1.write(i, 14, item['amount_ppn'], numb_table)
                worksheet1.write(i, 15, item['amount_total'], numb_table)
                worksheet1.write(i, 16, item['amount_pph'], numb_table)
                worksheet1.write(i, 17, item['amount_adjustment'], numb_table)
                worksheet1.write(i, 18, item['amount_paid'], numb_table)
                worksheet1.write(i, 19, item['amount_outstanding'], numb_table)
                worksheet1.write(i, 20, item['aged_day'], int_table)
                worksheet1.write(i, 21, item['current_amount'], numb_table)
                worksheet1.write(i, 22, item['amount_1_30'], numb_table)
                worksheet1.write(i, 23, item['amount_31_60'], numb_table)
                worksheet1.write(i, 24, item['amount_61_90'], numb_table)
                worksheet1.write(i, 25, item['amount_91_365'], numb_table)
                worksheet1.write(i, 26, item['amount_365'], numb_table)
                worksheet1.write(i, 27, item['receipt_number'], left_table)
                worksheet1.write(i, 28, datetime.strptime(str(item['receipt_date']), "%Y-%m-%d %H:%M:%S").strftime(
                    "%d-%b-%y") if item['receipt_date'] else '', left_table)
                worksheet1.write(i, 29, item['receipt_method'], left_table)
                worksheet1.write(i, 30,
                                 datetime.strptime(str(item['receipt_gl_date']), "%Y-%m-%d").strftime("%d-%b-%y") if
                                 item['receipt_gl_date'] else '', left_table)
                worksheet1.write(i, 31, item['receipt_amount'], numb_table)
                i += 1

            worksheet1.merge_range(i, 0, i, 12, 'Sub Total by Customer', right_footer)
            worksheet1.write(i, 13, sum(item['amount_untaxed'] for item in items), numb_footer)
            worksheet1.write(i, 14, sum(item['amount_ppn'] for item in items), numb_footer)
            worksheet1.write(i, 15, sum(item['amount_total'] for item in items), numb_footer)
            worksheet1.write(i, 16, sum(item['amount_pph'] for item in items), numb_footer)
            worksheet1.write(i, 17, sum(item['amount_adjustment'] for item in items), numb_footer)
            worksheet1.write(i, 18, sum(item['amount_paid'] for item in items), numb_footer)
            worksheet1.write(i, 19, sum(item['amount_outstanding'] for item in items), numb_footer)
            worksheet1.write(i, 20, '', right_footer)
            worksheet1.write(i, 21, sum(item['current_amount'] for item in items), numb_footer)
            worksheet1.write(i, 22, sum(item['amount_1_30'] for item in items), numb_footer)
            worksheet1.write(i, 23, sum(item['amount_31_60'] for item in items), numb_footer)
            worksheet1.write(i, 24, sum(item['amount_61_90'] for item in items), numb_footer)
            worksheet1.write(i, 25, sum(item['amount_91_365'] for item in items), numb_footer)
            worksheet1.write(i, 26, sum(item['amount_365'] for item in items), numb_footer)
            worksheet1.write(i, 27, '', right_footer)
            worksheet1.write(i, 28, '', right_footer)
            worksheet1.write(i, 29, '', right_footer)
            worksheet1.write(i, 30, '', right_footer)
            worksheet1.write(i, 31, sum(item['receipt_amount'] for item in items), numb_footer)
            i += 1
            worksheet1.merge_range(i, 0, i, 12, 'Percentage', right_footer)
            worksheet1.write(i, 13, '', right_footer)
            worksheet1.write(i, 14, '', right_footer)
            worksheet1.write(i, 15, '', right_footer)
            worksheet1.write(i, 16, '', right_footer)
            worksheet1.write(i, 17, '', right_footer)
            worksheet1.write(i, 18, '', right_footer)
            worksheet1.write(i, 19, '', right_footer)
            worksheet1.write(i, 20, '', right_footer)
            worksheet1.write(i, 21, sum(item['current_amount'] for item in items) / sum(
                item['amount_outstanding'] for item in items) if sum(
                item['current_amount'] for item in items) > 0 else 0, percent_footer)
            worksheet1.write(i, 22, sum(item['amount_1_30'] for item in items) / sum(
                item['amount_outstanding'] for item in items) if sum(item['amount_1_30'] for item in items) > 0 else 0,
                             percent_footer)
            worksheet1.write(i, 23, sum(item['amount_31_60'] for item in items) / sum(
                item['amount_outstanding'] for item in items) if sum(item['amount_31_60'] for item in items) > 0 else 0,
                             percent_footer)
            worksheet1.write(i, 24, sum(item['amount_61_90'] for item in items) / sum(
                item['amount_outstanding'] for item in items) if sum(item['amount_61_90'] for item in items) > 0 else 0,
                             percent_footer)
            worksheet1.write(i, 25, sum(item['amount_91_365'] for item in items) / sum(
                item['amount_outstanding'] for item in items) if sum(
                item['amount_91_365'] for item in items) > 0 else 0, percent_footer)
            worksheet1.write(i, 26, sum(item['amount_365'] for item in items) / sum(
                item['amount_outstanding'] for item in items) if sum(item['amount_365'] for item in items) > 0 else 0,
                             percent_footer)
            worksheet1.write(i, 27, '', right_footer)
            worksheet1.write(i, 28, '', right_footer)
            worksheet1.write(i, 29, '', right_footer)
            worksheet1.write(i, 30, '', right_footer)
            worksheet1.write(i, 31, '', right_footer)
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ar.aging.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
