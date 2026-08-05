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

    company_ids = fields.Many2many(
        comodel_name='res.company',
        string="Company",
        required=True,
        help='Company used to filter AR unapplied receipt report',
        default=lambda self: self.env.user.company_id,
    )

    current_user_companies = fields.Many2many(
        comodel_name='res.company',
        relation='unapplied_receipt_wizard_current_user_company_rel',
        column1='report_id',
        column2='company_id',
        string='Current User Allowed Companies',
        help='Current user allowed companies used to domain company parameter',
        default=lambda self: self.env.user.company_ids.ids,
    )

    def generate_report_xlsx(self):
        res = super(ARUnappliedReceiptReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'ar_unapplied_receipt':
            return self.env.ref('mnc_xlsx_reporting.action_ar_unapplied_receipt_report_xlsx'). \
                report_action(self)

        return res
