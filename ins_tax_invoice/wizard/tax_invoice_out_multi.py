from base64 import urlsafe_b64decode as b64dec
from base64 import urlsafe_b64encode as b64enc
from datetime import date
from io import BytesIO
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import pycompat


class WizardTaxInvoiceOutMulti(models.TransientModel):
    _name = 'wizard.tax.invoice.out.multi'
    _description = 'Export Faktur Pajak Keluaran (Multi)'

    def button_print(self):
        """ function to print report """
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        if not active_ids:
            raise ValidationError('No data to print')

        # active_ids exist, encode to md5
        s_ids = '-'.join([str(x) for x in active_ids])
        enc_ids = b64enc(s_ids.encode()).decode()

        report_date = date.today()
        name = 'efaktur_%s' % (report_date.strftime('%Y_%m_%d'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/efaktur_multi/%s/%s/%s/%s' % (self._name, self.id, name, enc_ids),
            'target': 'new',
        }

    def get_csv(self, headers, titles, data):
        """ function to generate csv report in bytes """
        fp = BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1, delimiter=';')

        # write headers and titles
        writer.writerow(headers)

        for title in titles:
            writer.writerow(title)

        # generate data and write every row
        for line in data:
            writer.writerow(line)

        return fp.getvalue()

    def _generate_headers(self):
        """ helper function to generate list of headers """
        headers = ['FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR',
                   'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP',
                   'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN',
                   'JUMLAH_PPNBM', 'ID_KETERANGAN_TAMBAHAN', 'FG_UANG_MUKA',
                   'UANG_MUKA_DPP', 'UANG_MUKA_PPN', 'UANG_MUKA_PPNBM',
                   'REFERENSI', 'KODE_DOKUMEN_PENDUKUNG']
        return headers

    def _generate_titles(self):
        """ helper function to generate list of titles """
        titles = [
            ['LT', 'NPWP', 'NAMA', 'JALAN', 'BLOK', 'NOMOR', 'RT', 'RW',
             'KECAMATAN', 'KELURAHAN', 'KABUPATEN', 'PROPINSI', 'KODE_POS'
             'NOMOR_TELEPON'],
            ['OF', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG',
             'HARGA_TOTAL', 'DISKON', 'DPP', 'PPN', 'TARIF_PPNBM', 'PPNBM'],
        ]
        return titles

    def _prepare_report_data(self):
        """ function to generate report data """
        report_data = []

        # get active ids
        enc_ids = self._context.get('enc_ids', '')
        if not enc_ids:
            raise ValidationError('Error in processing ids')

        # encode the data, decode by b64dec and decode again to get string
        dec_ids = b64dec(enc_ids.encode()).decode()
        active_ids = dec_ids.split('-')  # then split by -
        active_ids = [int(x) for x in active_ids]

        moves = self.env['account.move'].browse(active_ids)

        company = self.env.user.company_id  # use user active company
        for move in moves:
            partner = move.partner_id
            faktur = move.tax_invoice_id
            d = move.invoice_date.strftime('%Y-%m-%d').split("-")
            date_invoice = "%s/%s/%s" % (d[2], d[1], d[0])
            # append account move information
            faktur_name = str(faktur.name)
            faktur_nodash = faktur_name.replace('-', '')
            faktur_final = faktur_nodash.replace('.', '')
            npwp_name = str(partner.npwp)
            npwp_nodash = npwp_name.replace('-', '')
            npwp_final = npwp_nodash.replace('.', '')
            move_data = [
                'FK',
                faktur_final[0:2],
                faktur_final[2:3],
                faktur_final[3:],
                str(move.masa_pajak),
                str(move.tahun_pajak),
                date_invoice,
                npwp_final,
                partner.name,
                (partner.full_address).replace('\n', ' '),
                0,  # TODO dpp
                0,  # TODO ppn
                0,
                '',
                0,
                0,
                0,
                0,
                move.name,
                1,
            ]
            report_data.append(move_data)

            partner_data = [
                'FAPR',
                company.partner_id.name,
                (company.partner_id.full_address).replace('\n', ' '),
            ]
            report_data.append(partner_data)

            # loop move lines and append
            for line in move.invoice_line_ids:
                # need to calculate tax
                # tax = sum(line.price_subtotal * x.amount for x in line.tax_ids if x.amount)
                tax = line.price_total - line.price_subtotal

                unit_price = line.price_unit
                qty = line.quantity
                subtotal = line.price_subtotal

                line_data = [
                    'OF',
                    '1',
                    line.name or '1',
                    int(round(unit_price, 0)),
                    int(round(qty, 0)),
                    int(round(qty * unit_price, 0)),
                    int(round(unit_price * qty - subtotal, 0)),
                    int(round(subtotal, 0)),
                    round(tax, 0),
                    0,
                    0
                ]
                report_data.append(line_data)

            # update move record TODO

        return report_data
