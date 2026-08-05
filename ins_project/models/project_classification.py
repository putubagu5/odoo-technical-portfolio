from odoo import api, fields, models


class ProjectClassification(models.Model):
    _name = 'project.classification'
    _inherit = 'project.mixin'
    _description = 'Project Classification'

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.code}] {rec.name}'
            result.append((rec.id, name))
        return result
