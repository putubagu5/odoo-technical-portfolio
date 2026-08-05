from odoo import api, fields, models


class ApprovalHistoryMixin(models.AbstractModel):
    _name = 'approval.history.mixin'
    _description = 'Approval History Mixin'
    _order = 'level'

    level = fields.Integer('Level', default=0)
    employee_id = fields.Many2one('hr.employee', 'Approved By')
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job')
    approval_group_id = fields.Many2one('approval.group', 'Approval Group',
                                        copy=False)
    date = fields.Datetime('Date', copy=False)
    state = fields.Selection([
        ('draft', 'Submit'),
        ('ask', 'Ask'),
        ('answer', 'Answer'),
        ('approve', 'Approved'),
        ('approve_delegate', 'Approved by Delegatee'),
        ('forward', 'Forward'),
        ('reject', 'Rejected'),
    ], 'State', default='draft', copy=False)
    note = fields.Text('Note', copy=False)
    is_forward = fields.Boolean('Forwarded', default=False)
