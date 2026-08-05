from odoo import api, fields, models
from odoo.exceptions import Warning


class PmisBudgetRelocateLine(models.Model):
    _name = 'pmis.budget.relocate.line'
    _description = 'Budget Relocate Line'

    relocate_id = fields.Many2one('pmis.budget.relocate', 'Relocate',
                                  ondelete='cascade')
    no = fields.Integer('No')
    source_id = fields.Many2one('pmis.budget.line', 'Source Budget Line')
    source_expenditure_type_id = fields.Many2one(
        'project.expenditure.type', 'Source Expenditure Type',
        related='source_id.expenditure_type_id')
    source_item_code = fields.Char('Item Name', related='source_expenditure_type_id.name')
    source_item_name = fields.Char('Item Code', related='source_expenditure_type_id.code')
    destination_id = fields.Many2one('pmis.budget.line', 'Destination Budget Line')
    destination_expenditure_type_id = fields.Many2one(
        'project.expenditure.type', 'Destination Expenditure Type',
        related='destination_id.expenditure_type_id')
    destination_item_code = fields.Char('No Item Name', related='destination_expenditure_type_id.name')
    destination_item_name = fields.Char('No Item Code', related='destination_expenditure_type_id.code')
    description = fields.Text('Description')
    budget = fields.Float('Budget')
    amount_transfer = fields.Float('Transfer Budget')

    @api.constrains('budget', 'amount_transfer')
    def _check_budget_amount_transfer(self):
        """ constrains function to check budget with amount_transfer """
        for rec in self:
            if rec.budget < rec.amount_transfer:
                raise Warning('Amount to transfer exceeds Budget!')
