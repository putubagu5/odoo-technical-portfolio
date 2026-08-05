from odoo import _, fields, models, api
from datetime import datetime


class WizardUnappliedReceipt(models.Model):
    _name = 'wizard.unapplied.receipt'

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

    month = fields.Selection([
        ('01', 'Jan'),
        ('02', 'Feb'),
        ('03', 'Mar'),
        ('04', 'Apr'),
        ('05', 'May'),
        ('06', 'Jun'),
        ('07', 'Jul'),
        ('08', 'Aug'),
        ('09', 'Sep'),
        ('10', 'Oct'),
        ('11', 'Nov'),
        ('12', 'Dec')
    ], string="Month")
    year = fields.Selection(selection="get_year_selection", default=get_this_year, string="Year")

    # date_start = fields.Date('Start Date', required=True)
    # date_end = fields.Date('End Date', required=True)

    @api.onchange('date_start', 'date_end')
    def onchange_periode(self):
        if self.date_start and self.date_end:
            if self.date_end < self.date_start:
                return {
                    'value': {
                        'date_end': None,
                        'date_start': None
                    },
                    'warning': {
                        'title': 'Warning',
                        'message': 'Cannot back date!'
                    }
                }

    def generate(self):
        print("REPORT UNAPPLIED RECEIPT")
        report = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'mnc_fzn_reporting.unapplied_receipt_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        return report.report_action(self)
