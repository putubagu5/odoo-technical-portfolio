from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResProjectMain(models.Model):
    _name = 'res.project.main'
    _description = 'Main Project'

    name = fields.Char('Main Project Name')
    code = fields.Char('Main Project ID')
    gen21_code = fields.Char('Gen21 ID')
    company_id = fields.Many2one('res.company', 'Company', ondelete='restrict')

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code uniqueness """
        self.ensure_one()
        domain = [
            ('id', '!=', self.id),
            ('code', 'ilike', self.code),
        ]
        existing = self.env['res.project.main'].search_count(domain)
        if existing:
            raise ValidationError('Project with the same code already exists')
