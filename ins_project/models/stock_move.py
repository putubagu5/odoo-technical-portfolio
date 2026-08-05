from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    project_ids = fields.One2many(
        comodel_name="project.pr.line",
        inverse_name="move_line_id",
        string="Project Details",
    )
