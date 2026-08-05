# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RejectBudgetReason(models.TransientModel):
    _name = 'reject.budget.reason'

    budget_id = fields.Many2one('crossovered.budget', string="Budget")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id)
    date_reject = fields.Date(string="Date", default=fields.Date.context_today)
    reason = fields.Text(string="Reason", required=True)

    def submit(self):
        self.budget_id.write({
            'state': 'cancel',
            'reject_user_id': self.user_id.id,
            'reject_date_reject': self.date_reject,
            'reject_reason': self.reason,
        })
