from datetime import date, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ARReceiptReportWizard(models.TransientModel):
    _name = 'ar.receipt.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'AR Receipt Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('ar_receipt', 'AR Receipt')
        ],
    )

    company_ids = fields.Many2many(
        comodel_name='res.company',
        string="Company",
        required=True,
        help='Company used to filter AR receipt report',
        default=lambda self: self.env.user.company_id,
    )

    current_user_companies = fields.Many2many(
        comodel_name='res.company',
        relation='ar_receipt_report_wizard_current_user_company_rel',
        column1='report_id',
        column2='company_id',
        string='Current User Allowed Companies',
        help='Current user allowed companies used to domain company parameter',
        default=lambda self: self.env.user.company_ids.ids,
    )

    def generate_report_xlsx(self):
        res = super(ARReceiptReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'ar_receipt':
            return self.env.ref('mnc_xlsx_reporting.action_ar_receipt_report_xlsx').\
                report_action(self)

        return res