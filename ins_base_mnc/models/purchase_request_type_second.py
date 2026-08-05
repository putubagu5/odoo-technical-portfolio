from odoo import fields, models


class PurchaseRequestType(models.Model):
    _name = 'purchase.request.type.second'
    _description = 'Purchase Request Type 2'

    name = fields.Char('Name', copy=False)
    description = fields.Char('Description', copy=False)
    type1_ids = fields.Many2many(
        'purchase.request.type',
        string='Purchase Request Type 1')
