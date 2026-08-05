from odoo import fields, models, api


class AppliedCustomer(models.TransientModel):
    _name = 'applied.customer'
    _inherit = "applied.customer"

