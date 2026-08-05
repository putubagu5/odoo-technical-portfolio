from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning


class ResSites(models.Model):
    _name = 'res.sites'
    _description = 'Sites'

    name = fields.Char('Site Name', required=True)
    code = fields.Char('Site Code', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner Name', ondelete='cascade', required=True)
    partner_no = fields.Char('Partner ID/Reference', related="partner_id.partner_no")
    type = fields.Selection([
        ('customer', 'Customers'),
        ('vendor', 'Vendor'),
    ], string="Type", required=True)

    alternatif_name = fields.Char(string="Alternatif Name")
    phone_number = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    site_number = fields.Char(string="Site Number")
    site_address = fields.Text(string="Site Address")

    bank_id = fields.Many2one('res.bank', 'Bank Name', required=True)
    account_name = fields.Char('Account Name', required=True)
    account_no = fields.Char('Account No', required=True)
    address = fields.Char('Address')

    tax_npwp = fields.Char(string="No NPWP")
    tax_name = fields.Char(string="Name")
    tax_address = fields.Text(string="Address")

    delivery_address = fields.Text(string="Delivery Address")

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    partners = fields.Many2many('res.partner', 'rel_partner_sites', 'model_id',
                                'partner_id', string='Partners')
    contact_person = fields.Char('Contact Person', copy=False)

    _sql_constraints = [
        ('code_uniq', 'CHECK(1=1)', "A sites the same code already exists."),
    ]

    # @api.constrains('partner_id', 'company_id', 'code')
    # def _check_partner_company(self):
    #     """ constrains function to check code duplicate """
    #     domain = [
    #         ('id', '!=', self.id),
    #         ('partner_id', '=', self.partner_id.id),
    #         ('code', '=ilike', self.code),
    #         ('company_id', '=', self.company_id.id)
    #     ]
    #     rec = self.search(domain)
    #     if rec:
    #         raise Warning('Partner with company already exists!')
