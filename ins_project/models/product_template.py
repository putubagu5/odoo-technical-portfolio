from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expenditure_type_id = fields.Many2one(
        'project.expenditure.type', 'Expenditure Type')
    group_type_id = fields.Many2one('project.group.type', 'Group Type')
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account")
    is_cost_progress = fields.Boolean('Is CIP', default=False)
