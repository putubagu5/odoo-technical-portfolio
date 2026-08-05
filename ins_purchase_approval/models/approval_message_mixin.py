from odoo import api, fields, models
from odoo.tools.misc import format_datetime


class ApprovalMessageMixin(models.AbstractModel):
    _name = 'approval.message.mixin'
    _description = 'Approval Message Mixin'
    _order = 'date desc'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    date = fields.Datetime('Date')
    note = fields.Char('Note', copy=False)
    state = fields.Selection([
        ('draft', 'Submit'),
        ('ask', 'Ask'),
        ('answer', 'Answer'),
        ('approve', 'Approved'),
        ('approve_delegate', 'Approved by Delegatee'),
        ('forward', 'Forward'),
        ('reject', 'Rejected'),
    ], 'State', default='draft', copy=False)

    def format_date(self):
        """ helper function to return formatted date with Asia/Jakarta timezone """
        self.ensure_one()
        fmt = 'dd-MM-YYYY H:mm-ss'
        return format_datetime(self.env, self.date, tz='Asia/Jakarta', dt_format=fmt)
