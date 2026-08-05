from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    org_id = fields.Char('ORG ID')

    @api.constrains('org_id')
    def _check_org_id(self):
        """ constrains function to check the duplicate org_id """
        self.ensure_one()
        domain = [
            ('id', '!=', self.id),
            ('org_id', '=', self.org_id),
        ]
        companies = self.env['res.company'].with_user(SUPERUSER_ID).search_count(domain)
        if companies:
            raise ValidationError('ORG ID already exists')
