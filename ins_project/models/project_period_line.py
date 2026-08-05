from odoo import api, fields, models
from odoo.exceptions import Warning


class ProjectPeriodLine(models.Model):
    _name = 'project.period.line'
    _description = 'Period Line'

    period_id = fields.Many2one('project.period', 'Period', ondelete='cascade')
    name = fields.Char('Name')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close'),
    ], 'Status', default='open')

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        for rec in self:
            if rec.date_start > rec.date_end:
                raise Warning('Start Date must be earlier than End Date')

    def action_reopen(self):
        """ function to reopen period """
        for rec in self:
            rec.state = 'open'

    def action_close(self):
        """ function to close period """
        for rec in self:
            rec.state = 'close'
