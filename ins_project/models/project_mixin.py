from odoo import api, fields, models
from odoo.exceptions import Warning


class ProjectMixin(models.AbstractModel):
    _name = 'project.mixin'
    _description = 'Project Mixin'

    name = fields.Char('Name', copy=False)
    code = fields.Char('Code', copy=False, default='/')
    note = fields.Text('Description')

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise Warning('Code already exists!')
