from odoo import api, fields, models


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    budget_category_id = fields.Many2one('account.budget.category', 'Category',
                                         ondelete='restrict')
