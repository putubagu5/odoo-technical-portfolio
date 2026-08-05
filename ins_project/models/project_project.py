from odoo import api, fields, models
from odoo.exceptions import Warning


class ProjectProject(models.Model):
    _inherit = 'project.project'

    code = fields.Char('Code', copy=False, default='/')

    @api.model
    def create(self, vals):
        """ inherit create function to assign code to auto-generate """
        if vals.get('code') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.project')
        res = super(ProjectProject, self).create(vals)
        return res

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise Warning('Code already exists!')
