from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_estimate_start = fields.Date('Estimation Date Start')
    date_estimate_end = fields.Date('Estimation Date End')
    phase_type = fields.Selection([
        ('original', 'Original'),
    ], 'Phase Type', default='original')
    # TODO addition to
    episode_number = fields.Char('Episode Number')
    day_number = fields.Integer('Day Number')
    duration = fields.Float('Duration (minutes)')
    group_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], 'Group Type', default='local')
    # TODO manager, executive producer, producer

    @api.constrains('date_estimate_start', 'date_estimate_end')
    def _check_date_estimate_start_end(self):
        """ constrain function to check validity of estimate dates """
        for rec in self:
            if rec.date_estimate_start > rec.date_estimate_end:
                raise ValidationError('Date Start must be earlier than Date End')
