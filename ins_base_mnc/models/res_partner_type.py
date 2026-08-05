from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Partner Type'

    name = fields.Char('Name', copy=False)
    code = fields.Char('Code', copy=False)

    @api.constrains('code')
    def _check_code(self):
        self.ensure_one()
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise ValidationError('Code already exists!')
