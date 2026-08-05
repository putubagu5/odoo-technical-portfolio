from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.osv import expression


class ProjectExpenditureCategory(models.Model):
    _name = 'project.expenditure.category'
    _inherit = 'project.mixin'
    _description = 'Project Expenditure Category'

    group_id = fields.Many2one(
        'project.group.type', 'Group',
        domain='[("analytic_account_id", "=", analytic_account_id)]'
        )
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    company_id = fields.Many2one(
        'res.company', string='Company', store=True,
        default=lambda self: self.env.company)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic',
                                          check_company=True)
    budget_type = fields.Selection([
        ('absolute', 'Absolute'),
        ('advisory', 'Advisory'),
    ], 'Budget Type', related='company_id.default_budget_type_category', store=True)

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    @api.constrains('code', 'analytic_account_id', 'group_id')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [
            ('code', '=ilike', self.code),
            ('id', '!=', self.id),
            ('analytic_account_id', '=', self.analytic_account_id.id),
            ('group_id', '=', self.group_id.id)
            ]
        rec = self.search(domain)
        if rec:
            pass

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.code}] {rec.name}'
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
