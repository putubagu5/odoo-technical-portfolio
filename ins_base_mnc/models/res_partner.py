from odoo import api, fields, models, _
from odoo.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    alias_name = fields.Char('Alias Name')
    partner_no = fields.Char('Partner ID')
    site_ids = fields.One2many('res.sites', 'partner_id', 'Vendor Sites')
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')
    is_blacklist = fields.Boolean('Blacklisted', default=False)
    relation_partner_id = fields.Many2one('res.partner', 'Relation Partner(Customer / Vendor)')
    # email_partner = fields.Char('Email Partner', help='This is secondary email')
    # has_tax = fields.Boolean('Has Tax', default=True)

    def name_get(self):
        result = []
        for rec in self:
            name = f'{rec.name} - {rec.partner_no}'
            result.append((rec.id, name))
        return result

    # @api.constrains('partner_no')
    # def _check_partner_no(self):
    #     """ constrains function to check partner_no duplicate """
    #     domain = [
    #         ('partner_no', '=ilike', self.partner_no),
    #         ('id', '!=', self.id),
    #     ]
    #     rec = self.search(domain)
    #     if rec:
    #         raise Warning('Partner ID already exists!')
