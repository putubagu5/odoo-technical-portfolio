from odoo import fields, models, api


class ReceiptType(models.Model):
    _name = 'receipt.type'
    _description = 'Receipt Type'

    name = fields.Char(
        'Type Name', required=True, copy=False)
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account', required=True)
    category = fields.Selection([
        ('misc', 'Miscellaneous'), ('rcv', 'Payment Receipt')],
        string='Category Type', copy=False, default=None)
    type = fields.Selection(
        selection=[
            ('receive', 'Receipt'),
            ('payment', 'Payment'),
        ], string='Type', default="receive")
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True, help="Set active to false to hide the receipt type without removing it.")
