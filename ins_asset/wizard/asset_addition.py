from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WizardAssetAddition(models.TransientModel):
    _name = 'wizard.asset.addition'
    _description = 'Asset Addition'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_to < self.date_from:
            raise ValidationError('Date From cannot be later than Date To')

    def _prepare_report_data(self):
        result = {}
        # TODO
        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'Asset Addition %s - %s' % (self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def _generate_header(self):
        """ function to generate report headers """
        return ['Account', 'Asset Number - Description', 'Date Placed in Service',
                'Depreciation Method', 'Life (Yr. Mo.)', 'Initial Cost',
                'Year-to-Date Depreciation', 'Initial Depreciation Reserve',
                'Transaction Number']

    def get_xlsx(self, response, data=None):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('Asset Addition')

        row = col = 0

        # title and dates
        dfrom = (self.date_from).strftime('%B-%Y')
        dto = (self.date_to).strftime('%B-%Y')
        ws.write(row, col, 'Asset Addition Report')
        ws.write(row + 1, col, 'Period: %s - %s' % (dfrom, dto))

        row += 3

        # headers
        headers = self._generate_header()
        for idx, header in enumerate(headers):
            ws.write(row, col + idx, header)

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
