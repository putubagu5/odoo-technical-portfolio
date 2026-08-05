from odoo import api, fields, models


class ApprovalHierarchyLine(models.Model):
    _name = 'approval.hierarchy.line'
    _description = 'Approval Hierarchy Line'
    _order = 'level'

    hierarchy_id = fields.Many2one('approval.hierarchy', 'Hierarchy',
                                   ondelete='cascade')
    level = fields.Integer('Level', default=0)
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job')
    parent_job_id = fields.Many2one('hr.job', 'Parent')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    approval_group_id = fields.Many2one('approval.group', 'Approval Group')
    note = fields.Char('Description')

    @api.onchange('department_id', 'job_id')
    def _onchange_department_job(self):
        """ onchange function to add dynamic domain to user_id """
        self.ensure_one()
        return {
            'domain': {
                'employee_ids': [
                    ('department_id', '=', self.department_id.id),
                    ('job_id', '=', self.job_id.id),
                ]
            }
        }

    @api.onchange('level', 'parent_job_id')
    def _onchange_level_parent_job_id(self):
        """ onchange function to empty parent_job_id if level is 0 """
        self.ensure_one()
        if not self.level:
            self.parent_job_id = False
