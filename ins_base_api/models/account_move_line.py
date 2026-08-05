from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    total_spots_gen21 = fields.Float(string="Total Spots")
    total_gross_gen21 = fields.Float(string="Total Gross")
    agency_commision_gen21 = fields.Float(string="Agency Commision")
    agency_discount_gen21 = fields.Float(string="Agency Discount")
