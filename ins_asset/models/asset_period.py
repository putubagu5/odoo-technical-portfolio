import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class AssetPeriod(models.Model):
    _name = 'asset.period'
    _description = 'Asset Period'

    name = fields.Char('Period Name')
    company_id = fields.Many2one('res.company', 'Company', ondelete='restrict')
    date_start = fields.Date('Start Date', copy=False)
    date_end = fields.Date('End Date', copy=False)
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close'),
    ], 'Status', default='open')
    line_ids = fields.One2many('asset.period.line', 'period_id', 'Periods')

    def button_generate_period(self):
        """ function to generate period """
        months = (self.date_end.year - self.date_start.year) * 12 + (self.date_end.month - self.date_start.month)
        periods = []
        for i in range(months + 1):
            month = (self.date_start + relativedelta(months=i)).strftime('%m')
            year = (self.date_start + relativedelta(months=i)).strftime('%Y')

            name = '%s/%s' % (month, year)
            dstart = date(int(year), int(month), 1)
            dend = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])

            if int(month) == self.date_start.month:
                dstart = self.date_start

            if int(month) == self.date_end.month:
                dend = self.date_end

            periods.append({'name': name, 'date_start': dstart, 'date_end': dend})

        lines = []
        for period in periods:
            data = {
                'name': period['name'],
                'date_start': period['date_start'],
                'date_end': period['date_end'],
                'state': 'close',  # default to close
            }
            lines.append((0, 0, data))

        self.line_ids = lines
        return

    def button_close(self):
        """ function to close """
        for rec in self:
            rec.line_ids.write({'state': 'close'})
            rec.state = 'close'

    def button_reopen(self):
        """ function to reopen """
        for rec in self:
            rec.line_ids.write({'state': 'open'})
            rec.state = 'open'
