from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetPeriodLine(models.Model):
    _name = 'asset.period.line'
    _description = 'Asset Period Line'

    period_id = fields.Many2one('asset.period', 'Asset Period', ondelete='cascade')
    name = fields.Char('Period Name')
    date_start = fields.Date('Start Date', copy=False)
    date_end = fields.Date('End Date', copy=False)
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close'),
    ], 'Status', default='open')
    asset_ids = fields.One2many('account.asset', 'period_line_id', 'Assets')

    def action_close(self):
        """ function to set to close """
        for rec in self:
            rec.state = 'close'

    def action_reopen(self):
        """ function to set to open """
        for rec in self:
            search_period = [
                ('date_start', '<=', self.date_start),
                ('date_stop', '>=', self.date_end),
                ('company_id', '!=', False),
            ]
            journals = self.env['account.period'].search(search_period)
            if journals:
                for period in journals:
                    if period.state == 'done' and period.company_id.id == self.period_id.company_id.id:
                        raise ValidationError('Failed reopen period, because GL accounting period closed!')
            rec.state = 'open'
