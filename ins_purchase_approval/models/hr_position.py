from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrPosition(models.Model):
    _name = 'hr.position'
    _description = 'Position of Employee'

    name = fields.Char('Name', copy=True)
    code = fields.Char('Code', copy=True)
    active = fields.Boolean('Active', default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        name = default.get('name') if default else ''
        code = default.get('code') if default else ''
        new_name = name or '%sCOPY' % self.name
        new_code = code or '%sCOPY' % self.code
        default = dict(default or {}, name=new_name, code=new_code)
        return super(HrPosition, self).copy(default)

    @api.constrains('code')
    def _check_code(self):
        self.ensure_one()
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise ValidationError('Code already exists!')
