from odoo import models, fields, api, _


class CollectionSummaryReportWizard(models.Model):
    _name = 'collection.summary.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Collection Summary Report Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('collection_summary_report', 'Collection Summary Report')
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
        res = super(CollectionSummaryReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'collection_summary_report':
            return self.env.ref('mnc_and_reporting.action_collection_summary_report_xlsx').\
                report_action(self)

        return res
