from odoo import fields, models


class PurchaseRequestType(models.Model):
    _name = 'purchase.request.type'
    _description = 'Purchase Request Type'

    name = fields.Char('Name', copy=False)
    description = fields.Char('Description', copy=False)
