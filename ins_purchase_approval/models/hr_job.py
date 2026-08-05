from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'

    position_id = fields.Many2one('hr.position', 'Position', ondelete='restrict')

    @api.constrains('position_id', 'department_id')
    def _check_position_department(self):
        """ constrains function to check same record with position and department """
        self.ensure_one()
        domain = [
            ('position_id', '=', self.position_id.id),
            ('department_id', '=', self.department_id.id),
            ('company_id', '=', self.company_id.id),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise ValidationError('Job with Position and Department already exists!')

    @api.onchange('position_id', 'department_id')
    def _onchange_position_department(self):
        """ onchange function to set name """
        if self.position_id and self.department_id:
            self.name = '%s.%s' % (self.department_id.name, self.position_id.name)
