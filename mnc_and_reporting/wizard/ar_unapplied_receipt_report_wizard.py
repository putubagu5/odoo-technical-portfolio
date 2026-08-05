from odoo import models, fields, api, _


class ARUnappliedReceiptReportWizard(models.TransientModel):
    _name = 'ar.unapplied.receipt.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'AR Unapplied Receipt Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('ar_unapplied_receipt', 'AR Unapplied Receipt')
        ],
    )

    def generate_report_xlsx(self):
        res = super(ARUnappliedReceiptReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'ar_unapplied_receipt':
            return self.env.ref('mnc_and_reporting.action_ar_unapplied_receipt_report_xlsx'). \
                report_action(self)

        return res
