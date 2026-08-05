from odoo import api, fields, models
from odoo.exceptions import Warning


class RejectTaskReason(models.TransientModel):
    _name = 'wizard.reject.task.reason'
    _description = 'Reject Task Reason Wizard'

    task_id = fields.Many2one('pmis.budget', string="Budget", required=True)
    reason = fields.Text(string="Reason", required=True)

    def submit(self):
        self.task_id.task_status = 'reject'
        self.task_id.task_id.state = 'reject'
