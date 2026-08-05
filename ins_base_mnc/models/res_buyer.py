from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResBuyer(models.Model):
    _name = 'res.buyer'
    _description = 'Buyer'

    name = fields.Char('Name', copy=False)
    code = fields.Char('Code', copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.constrains('name')
    def _check_name(self):
        """ constrains function to check name duplicate """
        domain = [('name', '=ilike', self.name), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise ValidationError('Name already exists!')

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise ValidationError('Code already exists!')
