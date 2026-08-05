# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReceiptPeriodLine(models.Model):
    _name = 'receipt.period.line'
    _description = "Receipt Period Line"

    name = fields.Char(string="Period Name", required=True)
    receipt_period_id = fields.Many2one('receipt.period', string="Period", required=True, copy=False)
    date_start = fields.Date(string="Period Start", required=True, copy=False)
    date_end = fields.Date(string="Period End", required=True, copy=False)
    state = fields.Selection([
        ('open', "Open"), ('close', "Close")
    ], string="Status", default='open')

    def close_period(self):
        self.ensure_one()
        search_miscellaneous = [
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('state', '=', 'draft'),
            ('company_id.id', '=', self.receipt_period_id.company_id.id)    
        ]
        unprocessed_receipt_ids = self.env['miscellaneous.miscellaneous'].search(search_miscellaneous)
        if unprocessed_receipt_ids:
            message = "There are receipt that are still in 'Draft' status during this period."
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
                if period.state == 'done' and period.company_id.id == self.receipt_period_id.company_id.id:
                    raise ValidationError('Failed reopen period, because GL accounting period closed!')
        self.state = 'open'
