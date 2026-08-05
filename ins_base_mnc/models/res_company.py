# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    gain_account_id = fields.Many2one('account.account', help="ABccount used to write the journal item in case of gain while selling an asset")
    loss_account_id = fields.Many2one('account.account', help="ABccount used to write the journal item in case of loss while selling an asset")
    invoice_address_po = fields.Text('Invoice Address')

    def get_fallback_image(self):
        """ function to return the fallback image if not found """
        return '/ins_base_3tv_mncp/static/src/img/mnc_invosa.jpg'

    def get_global_image(self):
        """ function to get res.company.logo record exactly by one """
        company_logo = self.env['res.company.logo'].search([], limit=1)
        return company_logo.image if company_logo else self.get_fallback_image()
