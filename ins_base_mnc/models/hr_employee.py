from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('job_id')
    def _onchange_job_id(self):
        """ onchange function to add department_id """
        if self.job_id:
            self.department_id = self.job_id.department_id.id
            return {
                'domain': {
                    'department_id': [
                        ('id', '=', self.job_id.department_id.id),
                    ]
                }
            }
