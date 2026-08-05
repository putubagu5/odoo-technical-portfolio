from odoo import models, fields, api, _


class StatementAccountAgencyReportWizard(models.TransientModel):
    _name = 'statement.account.agency.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Statement Account Agency Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('statement_account_agency', 'Statement Account Agency')
        ],
    )

    customer_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Customers',
        help='Customers used to filter report',
    )

    currency_ids = fields.Many2many(
        comodel_name='res.currency',
        string='Currency',
        help='Currency used to filter report',
    )

    @api.onchange('customer_type')
    def onchange_customer_type(self):
        self.customer_ids = False
    
    @api.onchange('currency_type')
    def onchange_currency_type(self):
        self.currency_ids = False

    def generate_report_xlsx(self):
        res = super(StatementAccountAgencyReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'statement_account_agency':
            return self.env.ref('mnc_and_reporting.action_statement_account_agency_report_xlsx').\
            report_action(self)

        return res