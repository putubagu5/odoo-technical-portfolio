from datetime import date
from io import BytesIO
from odoo import api, fields, models
from odoo.tools import pycompat


class ProductTemplate(models.TransientModel):
    _name = 'wizard.product.template'
    _description = 'Tax Invoice Product Template Export'

    def _generate_headers(self):
        """ helper function to generate list of headers """
        headers = ['OB', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN']
        return headers

    def _prepare_report_data(self):
        """ function to generate report data """
        report_data = []

        # get products with is_efaktur_exported = False
        domain = []
        products = self.env['product.template'].search(domain)
        for product in products:
            line_data = [
                'OB',
                product.default_code,
                product.name,
                product.list_price,
            ]
            report_data.append(line_data)

        return report_data

    def button_print(self):
        """ function to print report """
        self.ensure_one()
        report_date = date.today()
        name = 'product_%s' % (report_date.strftime('%Y_%m_%d'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/efaktur/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_csv(self):
        """ function to generate csv report """
        fp = BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        # write headers
        writer.writerow(self._generate_headers())

        # generate data and write every row
        data = self._prepare_report_data()
        for line in data:
            writer.writerow(line)

        return fp.getvalue()
