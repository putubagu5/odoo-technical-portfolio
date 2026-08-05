from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections


class WizardMncTrialBalanceReport(models.TransientModel):
    _name = 'wizard.mnc.trial.balance.report'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    account_ids = fields.Many2many("account.account", string="Account")
    partner_ids = fields.Many2many("res.partner", string="Partner")
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
        numb_title_sub = workbook.add_format({'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        numb_title_sub.set_font_size('13')
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
        worksheet1.set_column('A:A', 20)
        worksheet1.set_column('B:B', 2)
        worksheet1.set_column('C:C', 25)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 30)
        worksheet1.set_column('G:G', 25)
        worksheet1.set_column('H:H', 20)
        worksheet1.set_column('I:I', 35)
        worksheet1.set_column('J:J', 70)
        worksheet1.set_column('K:K', 20)
        worksheet1.set_column('L:L', 20)
        worksheet1.set_column('M:M', 20)
        worksheet1.set_column('N:N', 20)
        worksheet1.set_column('O:O', 20)
        worksheet1.set_column('P:P', 20)
        worksheet1.set_column('Q:Q', 20)
        worksheet1.set_column('R:R', 20)
        worksheet1.set_column('S:S', 20)

        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        filename = str(self.company_id.name) + " GL - Trial Balance Detail"

        worksheet1.merge_range('A1:G1', 'TRIAL BALANCE REPORT', left_title)
        worksheet1.merge_range('A2:G2', self.company_id.name, left_title)
        i = 2
        worksheet1.write(i, 0, 'Period', left_title_sub)
        worksheet1.write(i, 1, ':', center_title_sub)
        worksheet1.write(i, 2, datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime("%d-%b-%Y") + ' s/d ' + \
                         datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"), left_title_sub)
        i += 2

        # FREZEE PANE
        worksheet1.freeze_panes(3, 4)

        query = """ 
                    SELECT acc.id
                        FROM account_move_line AS mvl
                            INNER JOIN account_move mv ON mv.id=mvl.move_id
                            INNER JOIN account_account acc ON acc.id=mvl.account_id
                    WHERE mvl.company_id=%s AND mvl.date<=%s AND mv.state='posted'
                """
        params = (self.company_id.id, self.end_date,)
        if self.account_ids:
            query += ' AND mvl.account_id IN %s'
            params += (tuple(self.account_ids.ids),)
        if self.partner_ids:
            query += ' AND mvl.partner_id IN %s'
            params += (tuple(self.partner_ids.ids),)

        query += ' GROUP BY acc.id'

        self._cr.execute(query, params)
        account_ids = self.env['account.account'].sudo().browse([r[0] for r in self._cr.fetchall()])
        for account in sorted(account_ids, key=lambda acc: acc.code):

            query = """ 
                        SELECT mvl.id
                            FROM account_move_line AS mvl
                                INNER JOIN account_move mv ON mv.id=mvl.move_id
                                INNER JOIN account_account acc ON acc.id=mvl.account_id
                        WHERE mvl.company_id=%s AND mvl.account_id=%s AND mvl.date<=%s AND mv.state='posted'
                    """
            params = (self.company_id.id, account.id, self.end_date,)
            if self.partner_ids:
                query += ' AND mvl.partner_id IN %s'
                params += (tuple(self.partner_ids.ids),)

            self._cr.execute(query, params)
            move_ids = self.env['account.move.line'].sudo().browse([r[0] for r in self._cr.fetchall()])

            beginning_balance = sum(
                move.debit - move.credit for move in move_ids.filtered(lambda mv: mv.date < self.start_date)) or 0.0
            ending_balance = sum(move.debit - move.credit for move in move_ids) or 0.0

            worksheet1.write(i, 0, 'Account', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, account.code if account.code else '-', left_title_sub)
            i += 1
            worksheet1.write(i, 0, 'Beginning Balance', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, beginning_balance, numb_title_sub)
            i += 1
            worksheet1.write(i, 0, 'Ending Balance', left_title_sub)
            worksheet1.write(i, 1, ':', center_title_sub)
            worksheet1.write(i, 2, ending_balance, numb_title_sub)
            i += 1

            mutation_ids = move_ids.filtered(lambda mv: mv.date >= self.start_date and mv.date <= self.end_date)
            if mutation_ids:
                worksheet1.merge_range(i, 0, i, 1, 'Effective Date', header_table)
                worksheet1.write(i, 2, 'Source', header_table)
                worksheet1.write(i, 3, 'Category', header_table)
                worksheet1.write(i, 4, 'Invoice Type', header_table)
                worksheet1.write(i, 5, 'Account', header_table)
                worksheet1.write(i, 6, 'Header', header_table)
                worksheet1.write(i, 7, 'Customer/Supplier', header_table)
                worksheet1.write(i, 8, 'Name', header_table)
                worksheet1.write(i, 9, 'Descriptions', header_table)
                worksheet1.write(i, 10, 'Faktur Pajak Local', header_table)
                worksheet1.write(i, 11, 'Pr Number', header_table)
                worksheet1.write(i, 12, 'Po Number', header_table)
                worksheet1.write(i, 13, 'Invoice Number', header_table)
                worksheet1.write(i, 14, 'Voucher Number', header_table)
                worksheet1.write(i, 15, 'JV Number', header_table)
                worksheet1.write(i, 16, 'Debit', header_table)
                worksheet1.write(i, 17, 'Credit', header_table)
                worksheet1.write(i, 18, 'Balance', header_table)
                i += 1

                balance_total = beginning_balance
                for mutation in sorted(mutation_ids, key=lambda move: move.date):
                    balance_total += mutation.debit - mutation.credit

                    worksheet1.merge_range(i, 0, i, 1,
                                           datetime.strptime(str(mutation.date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                           center_table)
                    worksheet1.write(i, 2, dict(mutation.move_id.journal_id._fields['type'].selection).get(
                        mutation.move_id.journal_id.type), left_table)
                    worksheet1.write(i, 3, dict(mutation.move_id.journal_id._fields['type'].selection).get(
                        mutation.move_id.journal_id.type), left_table)
                    worksheet1.write(i, 4, dict(mutation.move_id._fields['bill_type'].selection).get(
                        mutation.move_id.bill_type), left_table)
                    worksheet1.write(i, 5, str(mutation.company_id.company_code) + '.' + str(
                        mutation.account_id.code) + '.000.0000.000.000', left_table)
                    worksheet1.write(i, 6, mutation.journal_id.display_name, left_table)
                    worksheet1.write(i, 7, mutation.partner_id.partner_type_id.name if mutation.partner_id else '',
                                     left_table)
                    worksheet1.write(i, 8, mutation.partner_id.name if mutation.partner_id else '', left_table)
                    worksheet1.write(i, 9, mutation.name if mutation.name else '', left_table)
                    worksheet1.write(i, 10, mutation.tax_invoice_id.name if mutation.tax_invoice_id else '', left_table)
                    worksheet1.write(i, 11, '', left_table)
                    worksheet1.write(i, 12, mutation.move_id.po_numbers if mutation.move_id.po_numbers else '',
                                     left_table)
                    worksheet1.write(i, 13, mutation.move_id.name, left_table)
                    worksheet1.write(i, 14, mutation.move_id.name, left_table)
                    worksheet1.write(i, 15, '', left_table)
                    worksheet1.write(i, 16, mutation.debit, numb_table)
                    worksheet1.write(i, 17, mutation.credit, numb_table)
                    worksheet1.write(i, 18, balance_total, numb_table)
                    i += 1

                worksheet1.write(i, 15, 'Jumlah Total Per ' + str(account.code if account.code else '-'), left_footer)
                worksheet1.write(i, 16, sum(mutation.debit for mutation in mutation_ids), numb_footer)
                worksheet1.write(i, 17, sum(mutation.credit for mutation in mutation_ids), numb_footer)
                worksheet1.write(i, 18, balance_total, numb_footer)
                i += 1

            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.trial.balance.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
