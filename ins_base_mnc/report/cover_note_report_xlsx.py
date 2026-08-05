from odoo import api, models, fields, tools
from datetime import datetime
from pytz import timezone, UTC


class CoverNoteReportXlsx(models.AbstractModel):
    _name='report.ins_base_mnc.cover_note_report_xlsx'
    _inherit='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Cover Note Summary Report')
        sheet.set_column('A:A', 5)
        sheet.set_column('B:D', 25)
        sheet.set_column('E:E', 40)
        sheet.set_column('F:F', 25)

        text_top_style = workbook.add_format({'font_size': 12, 'bold': True, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True})
        text_style = workbook.add_format({'font_name': 'Times'})

        text_top_style.set_border(1)
        text_top_style.set_align('center')
        header_style.set_border(1)
        header_style.set_align('center')
        text_style.set_border(1)

        sheet.merge_range('A1:F1', "COVER NOTE UNTUK PEMBAYARAN",text_top_style)
        sheet.write(1, 0, 'No.', header_style)
        sheet.write(1, 1, 'Tanggal', header_style)
        sheet.write(1, 2, 'NAMA PENERIMA', header_style)
        sheet.write(1, 3, 'REKENING', header_style)
        sheet.write(1, 4, 'Keterangan', header_style)
        sheet.write(1, 5, 'Nominal', header_style)

        row = 2
        number = 1
        total = 0
        for line in wizard.move_ids:
            sheet.write(row, 0, number, text_style)
            sheet.write(row, 1, line.date, text_style)
            sheet.write(row, 2, line.partner_id.name, text_style)
            sheet.write(row, 3, line.sites_id.account_no, text_style)
            sheet.write(row, 4, line.ref_desc, text_style)
            sheet.write(row, 5, line.amount_total, text_style)

            row += 1
            number += 1
            total += line.amount_total

        sheet.write(row, 5, total)
