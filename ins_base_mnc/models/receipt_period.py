# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReceiptPeriod(models.Model):
    _name = 'receipt.period'
    _description = "Receipt Period"

    name = fields.Char(string="Period Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', ondelete='restrict')
    date_start = fields.Date(string="Start Date", required=True, copy=False)
    date_end = fields.Date(string="End Date", required=True, copy=False)
    state = fields.Selection([
        ('open', "Open"), ('close', "Close")
    ], string="Status", default='open')
    period_line_ids = fields.One2many('receipt.period.line', 'receipt_period_id', string="Periods")

    def generate_periods(self):
        self.ensure_one()

        months = (self.date_end.year - self.date_start.year) * 12 + (self.date_end.month - self.date_start.month)
        periods = []
        for i in range(months + 1):
            month_number = (self.date_start + relativedelta(months=i)).strftime('%m')
            month_year = (self.date_start + relativedelta(months=i)).strftime('%Y')

            name = month_number + "/" + month_year
            start_date = date(int(month_year), int(month_number), 1)
            end_date = date(
                int(month_year), int(month_number), calendar.monthrange(int(month_year), int(month_number))[1]
            )

            if int(month_number) == self.date_start.month:
                start_date = self.date_start

            if int(month_number) == self.date_end.month:
                end_date = self.date_end

            periods.append({'name': name, 'date_start': start_date, 'date_end': end_date})

        period_line_ids = []
        for period in periods:
            period_line_ids.append((0, 0, {
                'name': period['name'],
                'date_start': period['date_start'],
                'date_end': period['date_end'],
            }))

        self.period_line_ids = period_line_ids

    def close_all_lines(self):
        self.ensure_one()
        for line in self.period_line_ids:
            line.close_period()

        self.state = 'close'

    def reopen_all_lines(self):
        self.ensure_one()
        for line in self.period_line_ids:
            line.reopen_period()

        self.state = 'open'
