from datetime import date
from io import BytesIO
from odoo import api, fields, models
from odoo.tools import pycompat


class TaxInvoiceIn(models.TransientModel):
    _name = 'wizard.tax.invoice.in'
    _description = 'Tax Invoice Faktur Masukan Export'

    def _generate_headers(self):
        """ helper function to generate list of headers """
        headers = ['FM', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR',
                   'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP',
                   'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN',
                   'JUMLAH_PPNBM', 'IS_CREDITABLE']
        return headers

    def _prepare_report_data(self):
        """ function to generate report data """
        report_data = []

        # get invoices (account.move)
        domain = [
            ('is_efaktur_exported', '=', False),
            ('state', '=', 'open'),
            ('tax_invoice_no', '!=', ''),
            ('move_type', '=', 'in_invoice')
        ]
        moves = self.env['account.move'].search(domain)

        for move in moves:
            partner = move.partner_id
            faktur = move.tax_invoice_id
            d = move.invoice_date.strftime('%Y-%m-%d').split("-")
            date_invoice = "%s/%s/%s" % (d[2], d[1], d[0])
            faktur_name = str(faktur.name)
            faktur_nodash = faktur_name.replace('-', '')
            faktur_final = faktur_nodash.replace('.', '')
            move_data = [
                'FM',
                faktur_final[0:2],
                faktur_final[2:3],
                faktur_final[3:],
                str(move.masa_pajak),
                str(move.tahun_pajak),
                date_invoice,
                partner.name,
                partner.full_address,
                int(round(move.amount_untaxed)),
                round(move.amount_tax),
                0,
                1,
            ]
            report_data.append(move_data)

        return report_data

    def button_print(self):
        """ function to print report """
        self.ensure_one()
        report_date = date.today()
        name = 'efaktur_%s' % (report_date.strftime('%Y_%m_%d'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/efaktur/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_csv(self):
        """ function to generate csv report """
        fp = BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1, delimiter=';')

        # write headers
        writer.writerow(self._generate_headers())

        # generate data and write every row
        data = self._prepare_report_data()
        for line in data:
            writer.writerow(line)

        return fp.getvalue()
