from odoo import api, fields, models


class PmisCopyBudgetLine(models.Model):
    _name = 'pmis.copy.budget.line'
    _description = 'Copy Budget Details'

    budget_id = fields.Many2one('pmis.copy.budget', 'Budget', ondelete='cascade')
    no = fields.Integer('No')
    expenditure_type_id = fields.Many2one('project.expenditure.type',
                                          'Expenditure Type')
    item_code = fields.Char('Item Code', related='expenditure_type_id.name')
    item_name = fields.Char('Item Name', related='expenditure_type_id.code')
    description = fields.Text('Description')
    pax = fields.Integer('Pax')
    eps = fields.Integer('Eps')
    day = fields.Integer('Day')
    rate = fields.Float('Rate')
    average_by_eps = fields.Float('Average by Eps')
    budget = fields.Float('Budget')
    remarks = fields.Text('Remarks')
    do_copy = fields.Boolean('Copy?', default=False)
