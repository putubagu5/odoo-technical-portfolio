from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.osv import expression


class MainProject(models.Model):
    _name = 'pmis.main.project'
    _description = 'Main Project'

    name = fields.Char('Main Project ID', copy=False, default='/')
    gen21_name = fields.Char('PO number CMS', copy=False)
    main_project_name = fields.Char('Main Project Name')
    company_id = fields.Many2one(
        'res.company', string='Company', store=True,
        default=lambda self: self.env.company)

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.name}] {rec.main_project_name}'
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('main_project_name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    # @api.model
    # def create(self, vals):
    #     """ inherit create function to assign code to auto-generate """
    #     if vals.get('name') == '/':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('main.project')
    #     res = super(MainProject, self).create(vals)
    #     return res

    @api.model
    def create(self, vals):
        """ inherit create function to assign code to auto-generate """
        sequence = self.env['ir.sequence'].next_by_code('main.project')
        res = super(MainProject, self).create(vals)
        company_code = res.company_id.company_code or 'False'
        # task_name = res.main_project_id.main_project_name or 'False'
        # task_desc = res.name or 'False'
        res.write({
             'name': sequence.format(
                company_code=company_code,
                ),
         })
        return res

    @api.constrains('name')
    def _check_name(self):
        """ constrains function to check code duplicate """
        domain = [
            ('name', '!=', '/'),
            ('name', '=ilike', self.name),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Main Project ID already exists!')

    @api.constrains('main_project_name')
    def _check_main_project_name(self):
        """ constrains function to check code duplicate """
        domain = [
            ('main_project_name', '=ilike', self.main_project_name),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Main Project Name already exists!')
