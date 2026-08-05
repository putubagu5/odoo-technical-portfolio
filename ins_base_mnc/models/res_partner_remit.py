from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerRemit(models.Model):
    _name = 'res.partner.remit'
    _description = 'Partner Remit'

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company, required="True")
    partner_ids = fields.Many2many('res.partner', string='Partners')
    bank_ids = fields.Many2many('res.partner.bank', string='Banks', domain="[('company_id', '=', company_id)]")
