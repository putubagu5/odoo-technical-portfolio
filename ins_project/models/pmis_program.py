from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.osv import expression


class PmisProgram(models.Model):
    _name = 'pmis.program'
    _inherit = 'project.mixin'
    _description = 'Program'

    name = fields.Char(string='Program Name')
    code = fields.Char(string='Project Code', default='/')
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project',
                                      ondelete='restrict')
    genre_id = fields.Many2one('project.genre', 'Genre')
    category_id = fields.Many2one(
        'project.classification', 'Category / Classification')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', check_company=True)
    budget_type = fields.Selection([
        ('absolute', 'Absolute'),
        ('advisory', 'Advisory'),
    ], 'Budget Type', related='company_id.default_budget_type_project', store=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    create_date = fields.Datetime(string='Created On')
    description = fields.Char('Description')
    reference = fields.Char(string='Reference Number')

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [
            ('code', '!=', '/'),
            ('code', '=ilike', self.code),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Code already exists!')

    @api.constrains('name')
    def _check_name(self):
        """ constrains function to check name duplicate """
        domain = [
            ('name', '!=', '/'),
            ('name', '=ilike', self.name),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Program Name already exists!')

    @api.model
    def create(self, vals):
        """ inherit create function to assign code to auto-generate """
        # get company code and set dept_code to ''
        company_code = self.env.company.company_code or 'False'
        dept_code = ''

        # take sequence from analytic_account_id, but first, check vals
        if vals.get('analytic_account_id', False):
            analytic = self.env['account.analytic.account'].browse(vals.get('analytic_account_id'))

            if analytic.analytic_seq_id:
                # then take from analytic_seq_id
                sequence = analytic.analytic_seq_id._next()

                dept_code = analytic.departement_code

                code = sequence.format(company_code=company_code, dept_code=dept_code)

                vals.update({'code': code})

        res = super(PmisProgram, self).create(vals)
        return res

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

    # @api.model
    # def default_get(self, fields):
    #     res = super(PmisProgram, self).default_get(fields)
    #     company_code = self.env.user.company_id.company_code or ''
    #     dept_code = ''
    #     sequence = '000'
    #     full_code = ''

    #     # if self.company_id.company_code:
    #     #     company_code = self.company_id.departement_code

    #     if self.analytic_account_id.departement_code:
    #         dept_code = self.analytic_account_id.departement_code

    #     full_code = company_code + '-' + dept_code + '-' + sequence
    #     res.update({
    #         'code': full_code,
    #     })
    #     return res
