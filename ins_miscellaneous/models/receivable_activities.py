from odoo import fields, models, api


class ReceivableActivities(models.Model):
    _name = 'receivable.activities'
    _description = 'Receivable Activities'

    name = fields.Char(
        'Receivable Name', required=True)
    description_name = fields.Char(
        'Description')
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account', required=True)
    type = fields.Selection(
        selection=[
            ('receive', 'Receipt'),
            ('payment', 'Payment'),
        ], string='Type', default="receive")
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True, help="Set active to false to hide the receipt type without removing it.")
    receivable_activity_category = fields.Selection(
        selection=[
            ('iklan', 'Iklan'),
            ('non_iklan', 'Non Iklan'),
        ], string='Receivable Activity Category')
