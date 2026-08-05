from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.osv import expression


class ProjectExpenditureCategory(models.Model):
    _name = 'project.expenditure.subcategory'
    _description = 'Project Expenditure Subcategory'

    # name = fields.Char('Name')
    subcategory_code = fields.Char('Expenditure Sub Category Code')
    name = fields.Char('Expenditure Sub Category Name')
    expenditure_category_id = fields.Many2one(
        'project.expenditure.category', 'Expenditure Category',
        domain='[("analytic_account_id", "=", analytic_account_id), ("group_id", "=", group_id)]')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    company_id = fields.Many2one(
        'res.company', string='Company', store=True,
        default=lambda self: self.env.company)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic',
                                          check_company=True)
    group_id = fields.Many2one(
        'project.group.type', 'Group',
        domain='[("analytic_account_id", "=", analytic_account_id)]')
    budget_type = fields.Selection([
        ('absolute', 'Absolute'),
        ('advisory', 'Advisory'),
    ], 'Budget Type', related='company_id.default_budget_type_subcategory', store=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.subcategory_code}] {rec.name}'
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('subcategory_code', operator, name), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    # @api.constrains('code', 'analytic_account_id', 'expenditure_category_id')
    # def _check_code(self):
    #     """ constrains function to check code duplicate """
    #     domain = [
    #         ('code', '=ilike', self.code),
    #         ('id', '!=', self.id),
    #         ('analytic_account_id', '=', self.analytic_account_id.id),
    #         ('expenditure_category_id', '=', self.expenditure_category_id.id)
    #         ]
    #     rec = self.search(domain)
    #     if rec:
    #         pass
