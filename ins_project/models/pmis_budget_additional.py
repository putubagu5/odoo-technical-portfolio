from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PmisBudgetAdditional(models.Model):
    _name = 'pmis.budget.additional'
    _description = 'Budget Additional Item'

    relocate_id = fields.Many2one('pmis.budget.relocate', 'Relocate Data',
                                  ondelete='cascade')
    # NOTE the fields are similar to pmis.budget.line
    no = fields.Integer('No', default=1)
    source_id = fields.Many2one('pmis.budget.line', 'Source Budget Line')
    source_expenditure_type_id = fields.Many2one(
        'project.expenditure.type', 'Source Expenditure Type',
        related='source_id.expenditure_type_id')
    source_item_code = fields.Char('Item Name', related='source_expenditure_type_id.name')
    source_item_name = fields.Char('Item Code', related='source_expenditure_type_id.code')
    description = fields.Text('Description')
    budget = fields.Float('Budget')
    expenditure_type_id = fields.Many2one('project.expenditure.type',
                                          'Expenditure Type',
                                          domain="[('analytic_account_id', '=', destination_analytic_acc_id)]")
    destination_analytic_acc_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='relocate_id.destination_analytic_acc_id')
    subcategory_id = fields.Many2one('project.expenditure.subcategory',
                                     'Expenditure Subcategory',
                                     related='expenditure_type_id.category_id',
                                     store=True)
    category_id = fields.Many2one('project.expenditure.category',
                                  'Expenditure Category',
                                  related='subcategory_id.expenditure_category_id',
                                  store=True)
    item_code = fields.Char('Item Name', related='expenditure_type_id.name', store=True)
    item_name = fields.Char('Item Code', related='expenditure_type_id.code', store=True)
    description = fields.Text('Description')
    pax = fields.Integer('Pax')
    eps = fields.Integer('Eps')
    day = fields.Integer('Day')
    rate = fields.Float('Rate')
    remarks = fields.Text('Remarks')
    average_by_eps = fields.Float('Average by Eps')  # TODO COMPUTE
    total_budget = fields.Float('Total Budget', compute='_compute_budget_average')
    amount_budget_in = fields.Float('Budget In')

    @api.constrains('total_budget', 'budget')
    def _check_total_budget(self):
        """ constrains function to check the total_budget vs budget """
        for rec in self:
            if rec.total_budget > rec.budget:
                raise ValidationError('Total Budget cannot be more than Budget')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ onchange function to return domain to partner_id field """
        partner = False
        active_id = self._context.get('active_id', False)
        if active_id:
            payment = self.env['account.payment'].browse(active_id)
            partner = payment.partner_id if payment else False

        # return domain of partner_id and move_id
        return {
            'domain': {
                'partner_id': [('id', '=', partner.id)],
                'move_ids': [
                    ('partner_id', '=', partner.id),
                    ('payment_state', 'in', ('not_paid', 'in_payment', 'partial')),
                    ('amount_residual', '!=', 0),
                ],
            }
        }

    @api.depends('pax', 'eps', 'day', 'rate')
    def _compute_budget_average(self):
        """ compute function to calculate budget """
        for rec in self:
            budget = 0
            if rec.pax and rec.eps and rec.day and rec.rate:
                budget = rec.pax * rec.eps * rec.day * rec.rate
            rec.total_budget = budget
