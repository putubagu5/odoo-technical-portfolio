import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WizardTaxInvoiceGenerate(models.TransientModel):
    _name = 'wizard.tax.invoice.generate'
    _description = 'Wizard for Tax Invoice Number Generator'

    start = fields.Char('Start')
    end = fields.Char('End')
    year = fields.Integer('Year')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)

    def button_confirm(self):
        """ function to generate tax invoice records """
        # OLD: 017-17-34018714
        # NEW: 000.017-17.34018714
        pattern = r'(?P<code>\d{3}).(?P<branch>\d{3})-(?P<year>\d{2}).(?P<series>\d{8})'
        start = re.search(pattern, self.start)
        end = re.search(pattern, self.end)

        if not start or not end:
            raise ValidationError('Pattern must be xxx.xxx-xx.xxxxxxxx')

        start_dict = start.groupdict()
        end_dict = end.groupdict()

        tax_invoice_data = []
        for i in range(int(start_dict.get('series', 0)), int(end_dict.get('series', 0)) + 1):
            nomor = '%s.%s-%s.%08d' % (
                start_dict.get('code', ''),
                start_dict.get('branch', ''),
                start_dict.get('year', ''),
                i)
            data = {
                'year': self.year,
                'name': nomor,
            }
            tax_invoice_data.append(data)
        self.env['tax.invoice'].create(tax_invoice_data)
        return True
