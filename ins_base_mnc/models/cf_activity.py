from odoo import fields, models, api


class CFActivity(models.Model):
    _name = 'cashflow.activity'
    _description = 'Cash FLow Activity'

    name = fields.Char('CF Activity Name', required=True)
    code = fields.Char('CF Activity Code', required=True)
    cf_category_id = fields.Many2one(
        'cashflow.activity.category', 'CF Category', required=True)
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company)
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the CF Activity without removing it.")
    cf_type = fields.Selection([
        ('receipt', 'Receipt'),
        ('payment', 'Payment'),
    ], 'CF Type', default='receipt')
