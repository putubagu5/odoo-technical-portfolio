from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.osv import expression


class ProjectExpenditureType(models.Model):
    _name = 'project.expenditure.type'
    _inherit = 'project.mixin'
    _description = 'Project Expenditure Type'

    category_id = fields.Many2one(
        'project.expenditure.subcategory',
        'Expenditure Sub Category',
        domain='[("analytic_account_id", "=", analytic_account_id), ("group_id", "=", group_id)]',
        ondelete='restrict')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          check_company=True)
    group_id = fields.Many2one(
        'project.group.type', 'Group',
        domain='[("analytic_account_id", "=", analytic_account_id)]')

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

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    @api.constrains('code', 'analytic_account_id', 'category_id')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [
            ('code', '=ilike', self.code),
            ('id', '!=', self.id),
            ('analytic_account_id', '=', self.analytic_account_id.id),
            ('category_id', '=', self.category_id.id)
            ]
        rec = self.search(domain)
        if rec:
            pass
