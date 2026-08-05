from odoo import models, fields, api, _


class SalesIncentiveReportWizard(models.Model):
    _name = 'sales.incentive.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Sales Incentive Report Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('sales_incentive_report', 'Sales Incentive Report')
        ],
    )

    customer_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Customers',
        help='Customers used to filter report',
    )

    @api.onchange('customer_type')
    def onchange_customer_type(self):
        self.customer_ids = False

    def generate_report_xlsx(self):
        res = super(SalesIncentiveReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'sales_incentive_report':
            return self.env.ref('mnc_and_reporting.action_sales_incentive_report_xlsx').\
                report_action(self)

        return res
