from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PhaseProjectCip(models.Model):
    _name = 'phase.project.cip'
    _description = 'Phase Project CIP Configuration'

    name = fields.Char('Phase Project Name')
    code = fields.Char('Phase Project Code')
    cip_id = fields.Many2one('cip.configuration', 'CIP')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
