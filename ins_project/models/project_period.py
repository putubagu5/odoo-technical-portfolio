import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError


class ProjectPeriod(models.Model):
    _name = 'project.period'
    _description = 'Project Period Data'

    name = fields.Char('Name', copy=False)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    line_ids = fields.One2many('project.period.line', 'period_id', 'Periods')
    has_lines = fields.Boolean('Has Lines', compute='_compute_has_lines')
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close'),
    ], 'Status', default='open')

    @api.depends('line_ids')
    def _compute_has_lines(self):
        """ compute function to check if record has lines """
        for rec in self:
            rec.has_lines = len(rec.line_ids)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    def unlink(self):
        range_obj = self.env['project.period.line']
        rule_ranges = range_obj.search([('period_id', '=', self.id)])
        if rule_ranges:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(ProjectPeriod, self).unlink()

    def button_generate(self):
        """ function to generate periods """
        self.ensure_one()
        # find months
        months = (self.date_end.year - self.date_start.year) * 12 + (
            self.date_end.month - self.date_start.month
        )
        periods = []
        for i in range(months + 1):
            month = (self.date_start + relativedelta(months=i)).strftime('%m')
            year = (self.date_start + relativedelta(months=i)).strftime('%Y')

            name = '%s/%s' % (month, year)
            dstart = date(int(year), int(month), 1)
            edate = calendar.monthrange(int(year), int(month))[1]
            dend = date(int(year), int(month), edate)

            if int(month) == self.date_start.month:
                dstart = self.date_start

            if int(month) == self.date_end.month:
                dend = self.date_end

            periods.append({'name': name, 'date_start': dstart, 'date_end': dend})

        period_lines = [(2, x.id) for x in self.line_ids]  # precaution, remove
        for period in periods:
            data = {
                'name': period['name'],
                'date_start': period['date_start'],
                'date_end': period['date_end'],
                'state': 'close',
            }
            period_lines.append((0, 0, data))

        self.line_ids = period_lines
        return True

    def action_close(self):
        """ function to close all lines and this record """
        self.ensure_one()
        self.line_ids.action_close()
        self.state = 'close'

    def action_reopen(self):
        """ function to reopen lines """
        self.ensure_one()
        self.line_ids.action_reopen()
        self.state = 'open'
