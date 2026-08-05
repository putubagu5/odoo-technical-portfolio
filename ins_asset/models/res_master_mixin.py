from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResMasterMixin(models.AbstractModel):
    _name = 'res.master.mixin'
    _description = 'Mixin for Master Data'

    name = fields.Char('Name', copy=True)
    code = fields.Char('Code', copy=True)
    note = fields.Text('Note')
    active = fields.Boolean('Active', default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        name = default.get('name') if default else ''
        code = default.get('code') if default else ''
        new_name = name or _('%sCOPY') % self.name
        new_code = code or _('%sCOPY') % self.code
        default = dict(default or {}, name=new_name, code=new_code)
        return super(ResMasterMixin, self).copy(default)

    @api.constrains('code')
    def _check_code(self):
        self.ensure_one()
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise ValidationError('Code already exists!')
