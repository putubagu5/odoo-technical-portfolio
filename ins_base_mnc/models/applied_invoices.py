from odoo import api, fields, models


class AppliedInvoices(models.Model):
    _inherit = 'applied.invoices'

    receipt_number = fields.Char(related='misc_id.receipt_number')
