from odoo import api, fields, models
from datetime import datetime, timedelta, date


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    project_names = fields.Char(
        string="Project Names", compute='_compute_project_names')

    def process_scheduler_queue(self):
        for rec in self.search([('state', '=', 'to_approve')]):
            days_default = 30
            limit_datetime = datetime.now() - timedelta(days=days_default)
            limit_date = limit_datetime.date()
            # compare with write_date
            if rec.write_date <= limit_date:
                rec.write({'state': 'rejected'})

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            # if rec.state in ("to_approve", "approved", "rejected", "done"):
            if rec.state in ("approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    @api.depends("line_ids", "line_ids.estimated_cost")
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = sum(
                rec.line_ids.filtered(
                    lambda x: x.request_state != 'cancel'
                    ).mapped("estimated_cost"))

    @api.depends('line_ids.project_ids')
    def _compute_project_names(self):
        for record in self:
            project_name_list = []
            for line in record.line_ids:
                for project_line in line.project_ids:
                    project_name_list.append(project_line.program_id.program_id.name)

            project_name_list = list(set(project_name_list))
            project_name_list.sort()
            project_names = ', '.join(map(str, project_name_list))
            record.project_names = project_names
