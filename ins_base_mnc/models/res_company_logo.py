from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompanyLogo(models.Model):
    _name = 'res.company.logo'
    _description = 'Company Logo Data'

    active = fields.Boolean('Active')
    image = fields.Image('Logo', attachment=True)

    @api.constrains('active')
    def _check_active(self):
        """ constrains function to check active record to limit only one """
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('active', '=', True),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError('You could only have one active record')
