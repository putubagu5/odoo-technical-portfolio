# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentPeriodLine(models.Model):
    _name = 'payment.period.line'
    _description = "Payment Period Line"

    name = fields.Char(string="Period Name", required=True)
    payment_period_id = fields.Many2one('payment.period', string="Period", required=True, copy=False)
    date_start = fields.Date(string="Period Start", required=True, copy=False)
    date_end = fields.Date(string="Period End", required=True, copy=False)
    state = fields.Selection([
        ('open', "Open"), ('close', "Close")
    ], string="Status", default='open')

    def close_period(self):
        self.ensure_one()
        search_payment = [
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('state', '=', 'draft'),
            ('company_id.id', '=', self.payment_period_id.company_id.id)    
        ]
        unprocessed_payment_ids = self.env['account.payment'].search(search_payment)
        if unprocessed_payment_ids:
            message = "There are payment that are still in 'Draft' status during this period."
            raise ValidationError(message)

        self.state = 'close'

    def reopen_period(self):
        self.ensure_one()
        search_period = [
            ('date_start', '<=', self.date_start),
            ('date_stop', '>=', self.date_end),
            ('company_id', '!=', False),
        ]
        journals = self.env['account.period'].search(search_period)
        if journals:
            for period in journals:
                if period.state == 'done' and period.company_id.id == self.payment_period_id.company_id.id:
                    raise ValidationError('Failed reopen period, because GL accounting period closed!')
        self.state = 'open'
