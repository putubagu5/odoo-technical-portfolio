from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectPhaseType(models.Model):
    _name = 'project.phase.type'
    _inherit = 'project.mixin'
    _description = 'Project Phase Type'

    is_additional = fields.Boolean('Is Additional', default=False)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')

    def unlink(self):
        range_obj = self.env['pmis.project.task']
        rule_ranges = range_obj.search([('phase_type_id', '=', self.id)])
        if rule_ranges:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(ProjectPhaseType, self).unlink()
