from odoo import models, fields, api, _


class SubledgerDetailsReportWizard(models.TransientModel):
    _name = 'subledger.details.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Subldeger Details Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('subledger_details', 'Subledger Details')
        ],
    )

    analytic_account_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help='Analytic account used to filter report',
    )

    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Accounts',
        help='Chart of account used to filter report',
    )

    def generate_report_xlsx(self):
        res = super(SubledgerDetailsReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'subledger_details':
            return self.env.ref('mnc_and_reporting.action_subledger_details_report_xlsx'). \
                report_action(self)

        return res

    @api.onchange('account_type')
    def onchange_account_type(self):
        self.account_ids = False

    @api.onchange('analytic_account_type')
    def onchange_analytic_account_type(self):
        self.analytic_account_ids = False
