from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_cost_progress = fields.Boolean('Is CIP', default=False)
    cip_id = fields.Many2one('cip.configuration', 'CIP Configuration', company_dependent=True, domain="[('company_id', '=', current_company_id)]")
