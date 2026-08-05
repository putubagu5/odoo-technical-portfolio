from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.move.line'

    project_ids = fields.One2many(
        comodel_name="project.pr.line",
        inverse_name="account_line_id",
        string="Project Details",
    )
