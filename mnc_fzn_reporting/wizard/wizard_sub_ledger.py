# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class WizardSubLedgerDetail(models.TransientModel):
    _name = 'wizard.sub.ledger.detail'
    _description = 'Sub Ledger Detail Wizard'

    def default_account_ids(self):
        account_obj = self.env['account.account']
        company_id = self.env['res.company'].sudo().browse(self.env.user.company_id.id)
        domain = [('company_id', '=', company_id.id)]
        account_id = account_obj.sudo().search(domain)
        return account_id

    date_start = fields.Date('Period Start', required=True)
    date_end = fields.Date('Period End', required=True)
    company_id = fields.Many2many(comodel_name='res.company', string='Company', default=lambda self: self.env.company)
    code = fields.Char(string='Company Code')
    cost_center = fields.Many2one(comodel_name='account.analytic.account', string='Costcenter')
    area = fields.Char(string='Area')
    future_1 = fields.Char(string='Future 1')
    future_2 = fields.Char(string='Future 2')
    # account_id = fields.Many2many(comodel_name='account.account', required=True, string='Account')
    account_id = fields.Many2many(comodel_name='account.account', required=True,
                                  readonly=False, string='Account')
    get_all_account = fields.Boolean()
    # current_user_companies = fields.Many2many(comodel_name='res.company',
    #                                           relation='wizard_sub_ledger_detail_current_user_company_rel',
    #                                           column1='report_id', column2='company_id',
    #                                           string='Current User Allowed Companies',
    #                                           help='Current user allowed companies used to domain company parameter',
    #                                           default=lambda self: self.env.user.company_id.ids)

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

    @api.onchange('get_all_account')
    def _onchange_get_all_account(self):
        if self.get_all_account == True:
            self.account_id = self.default_account_ids()
        else:
            self.account_id = False

    def generate(self):
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'mnc_fzn_reporting.sub_ledger_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        print('TEEEES', report)
        return report.report_action(self)
