from odoo import api, fields, models


class VendorSite(models.Model):
    _name = 'vendor.site'
    _description = 'Vendor Site'

    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='cascade')
    name = fields.Char('Site Name', copy=False)
    code = fields.Char('Site Code', copy=False)
    account_name = fields.Char('Account Name', copy=False)
    bank_id = fields.Many2one('res.bank', 'Bank')
    account_no = fields.Char('Account No', copy=False)
    address = fields.Char('Address', copy=False)
    contact_person = fields.Char('Contact Person', copy=False)
