# -*- coding: utf-8 -*-q

from odoo import models, fields, api, _
from datetime import datetime


class WizardPurchaseOrderList(models.TransientModel):
    _name = 'wizard.purchase.order'
    _description = 'Purchase Order List Wizard'

    def get_partner_name(self):
        self.ensure_one()

        partner_name = ''
        for partner in self.partner_id:
            if partner_name == '':
                partner_name = partner.name
            else:
                partner_name += ', ' + partner.name
        print("SUPPLIER >>", partner_name)

        return partner_name

    def get_buyer_name(self):
        self.ensure_one()

        buyer_name = ''
        for buyer in self.buyer_id:
            if buyer_name == '':
                buyer_name = buyer.name
            else:
                buyer_name += ', ' + buyer.name
        print("BUYER >>", buyer_name)

        return buyer_name

    @api.model
    def _get_default_company_id(self):
        return self.env.user.company_id.id

    date_start = fields.Date('Period Start')
    date_end = fields.Date('Period End')
    partner_id = fields.Many2many(comodel_name='res.partner', string='Supplier')
    item = fields.Many2one(comodel_name='product.product', string='Item')
    type_pr = fields.Char(string='Type PR')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=_get_default_company_id)
    is_supplier = fields.Boolean(string="All Supplier", default=True)
    as_of = fields.Date(string='As Of Period')
    is_date_range = fields.Boolean(string="Custom Date Range", default=True)
    is_buyer = fields.Boolean(string="All Buyer", default=True)
    buyer_id = fields.Many2many(comodel_name='res.buyer', string='Buyer')

    @api.onchange('date_start', 'date_end')
    def onchange_periode(self):
        if self.date_start and self.date_end:
            if self.date_end < self.date_start:
                return {
                    'value': {
                        'date_end': None,
                        'date_start': None
                    },
                    'warning': {
                        'title': 'Warning',
                        'message': 'Cannot back date!'
                    }
                }

    def generate(self):
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'mnc_fzn_reporting.purchase_order_list_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        print('TEEEES', report)
        return report.report_action(self)
