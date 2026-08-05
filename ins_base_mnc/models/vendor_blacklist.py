from datetime import date
from odoo import api, fields, models


class VendorBlacklist(models.Model):
    _name = 'vendor.blacklist'
    _description = 'Vendor Blacklist'

    partner_id = fields.Many2one('res.partner', 'Vendor')
    npwp = fields.Char(related='partner_id.npwp')
    reason = fields.Text('Reason')
    date_approved = fields.Date('Approved Date')
    date_cancelled = fields.Date('Cancelled Date')
    state = fields.Selection([
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
    ], 'Status')

    def button_approve(self):
        """ function to approve blacklist """
        for rec in self:
            rec.partner_id.is_blacklist = True
            rec.write({'date_approved': date.today(), 'state': 'approve'})

    def button_cancel(self):
        """ function to cancel blacklist """
        for rec in self:
            rec.partner_id.is_blacklist = False
            rec.write({'date_cancelled': date.today(), 'state': 'cancel'})
