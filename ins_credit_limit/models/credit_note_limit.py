# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CreditNoteLimit(models.Model):
    _name = 'credit.note.limit'
    _description = "User Credit Note Limit"
    _order = 'id asc'

    user_id = fields.Many2one('res.users', string="User", required=True)
    limit_usage = fields.Selection([
        ('credit_note', "Credit Memo"), ('ar_adjustment', "Adjustment AR")
    ], string="Limit Type", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    amount_from = fields.Monetary(string="From Amount", currency_field='currency_id')
    amount_to = fields.Monetary(string="To Amount", currency_field='currency_id')
