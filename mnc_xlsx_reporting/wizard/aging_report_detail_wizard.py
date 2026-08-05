from odoo import models, fields, api, _


class AgingReportDetailWizard(models.Model):
    _name = 'aging.report.detail.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Aging Report Detail Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('aging_report_detail', 'Aging Report Detail')
        ],
    )

    customer_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Customers',
        help='Customers used to filter report',
        domain=['|', ('parent_id', '=', False), ('is_company', '=', True)]
    )

    def generate_report_xlsx(self):
        res = super(AgingReportDetailWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'aging_report_detail':
            return self.env.ref('mnc_xlsx_reporting.action_aging_report_detail_xlsx').\
                report_action(self)

        return res
