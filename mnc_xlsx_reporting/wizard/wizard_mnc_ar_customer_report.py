from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter


class WizardMncArCustomerReport(models.TransientModel):
    _name = 'wizard.mnc.ar.customer.report'

    all_partner = fields.Boolean(string="All Customer", default=True)
    partner_ids = fields.Many2many("res.partner", string="Customer")
    file = fields.Binary("File")

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
        #################################################################################
        center_table = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
        center_table.set_font_size('11')
        center_table.set_border()
        #################################################################################
        left_table = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        left_table.set_font_size('11')
        left_table.set_border()
        #################################################################################
        rigth_table = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        rigth_table.set_font_size('11')
        rigth_table.set_border()

        worksheet1 = workbook.add_worksheet("All")
        worksheet1.set_column('A:A', 15)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 25)
        worksheet1.set_column('E:E', 25)
        worksheet1.set_column('F:F', 10)
        worksheet1.set_column('G:G', 35)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 20)
        worksheet1.set_column('K:K', 25)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_column('M:M', 15)
        worksheet1.set_column('N:N', 15)
        worksheet1.set_column('O:O', 15)

        filename = "AR - Customer List"

        worksheet1.merge_range('A1:D1', 'CUSTOMER LIST REPORT', left_title)
        i = 2
        worksheet1.write(i, 0, 'Customer', left_title_sub)
        worksheet1.write(i, 1, 'All' if self.all_partner else self.get_partner_name(), left_title_sub)
        i += 2
        worksheet1.write(i, 0, 'Customer ID', header_table)
        worksheet1.write(i, 1, 'Customer Number', header_table)
        worksheet1.write(i, 2, 'Property', header_table)
        worksheet1.write(i, 3, 'Customer Name', header_table)
        worksheet1.write(i, 4, 'Customer Name NPWP Alphabet', header_table)
        worksheet1.write(i, 5, 'ORG ID', header_table)
        worksheet1.write(i, 6, 'Invoice Address', header_table)
        worksheet1.write(i, 7, 'Country Code', header_table)
        worksheet1.write(i, 8, 'Country Name', header_table)
        worksheet1.write(i, 9, 'NPWP', header_table)
        worksheet1.write(i, 10, 'Tax Address', header_table)
        worksheet1.write(i, 11, 'Original Bill Customer ID', header_table)
        worksheet1.write(i, 12, 'Original Bill Address ID', header_table)
        worksheet1.write(i, 13, 'Original Bill Customer Reff', header_table)
        worksheet1.write(i, 14, 'Original Bill Address Reff', header_table)
        i += 1

        query = """ 
                    SELECT rp.id
                        FROM account_move AS mv
                            INNER JOIN res_partner rp ON rp.id=mv.partner_id
                    WHERE mv.partner_id IS NOT NULL AND mv.move_type='out_invoice' AND mv.state='posted'
                """
        params = ()

        if not self.all_partner:
            query += ' AND mv.partner_id IN %s'
            params += (tuple(self.partner_ids.ids),)
        query += ' GROUP BY rp.id ORDER BY rp.name asc'

        self._cr.execute(query, params)

        partner_ids = self.env['res.partner'].browse([r[0] for r in self._cr.fetchall()])
        for partner in partner_ids:
            worksheet1.write(i, 0, partner.id, left_table)
            worksheet1.write(i, 1, partner.partner_no, left_table)
            worksheet1.write(i, 2, '', left_table)
            worksheet1.write(i, 3, partner.name, left_table)
            worksheet1.write(i, 4, partner.alias_name, left_table)
            worksheet1.write(i, 5, '', left_table)
            worksheet1.write(i, 6, partner.child_ids[0].street if partner.child_ids else '', left_table)
            worksheet1.write(i, 7, partner.country_id.code if partner.country_id.code else '', left_table)
            worksheet1.write(i, 8, partner.country_id.name if partner.country_id.name else '', left_table)
            worksheet1.write(i, 9, partner.npwp, left_table)
            worksheet1.write(i, 10, partner.full_address, left_table)
            worksheet1.write(i, 11, partner.id, left_table)
            worksheet1.write(i, 12, partner.site_ids[0].id if partner.site_ids else '', left_table)
            worksheet1.write(i, 13, partner.partner_no, left_table)
            worksheet1.write(i, 14, '', left_table)
            i += 1

        workbook.close()
        file = base64.encodebytes(fp.getvalue())
        self.write({'file': file})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=wizard.mnc.ar.customer.report&field=file&download=true&id=%s&filename=%s.xlsx' % (
                self.id, filename),
            'target': 'new',
        }
