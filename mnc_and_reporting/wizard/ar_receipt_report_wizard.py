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

    def generate_report_xlsx(self):
        res = super(ARReceiptReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'ar_receipt':
            return self.env.ref('mnc_and_reporting.action_ar_receipt_report_xlsx'). \
                report_action(self)

        return res
