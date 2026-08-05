from odoo import fields, models, api


class CFActivityCategory(models.Model):
    _name = 'cashflow.activity.category'
    _description = 'Cash Flow Activity Category'

    name = fields.Char('CF Category Name', required=True)
    code = fields.Char('CF Category Code', required=True)
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the CF Category without removing it.")
