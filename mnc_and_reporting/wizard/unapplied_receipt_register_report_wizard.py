from odoo import models, fields, api, _


class UnappliedReceiptRegisterReportWizard(models.TransientModel):
    _name = 'unapplied.receipt.register.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Unapplied Receipt Register Report Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('unapplied_receipt_register', 'Unapplied Receipt Register Details')
        ],
    )

    currency_ids = fields.Many2many(
        comodel_name='res.currency',
        string='Currency',
        help='Currency used to filter report',
    )

    @api.onchange('currency_type')
    def onchange_currency_type(self):
        self.currency_ids = False

    def generate_report_xlsx(self):
        res = super(UnappliedReceiptRegisterReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'unapplied_receipt_register':
            return self.env.ref('mnc_and_reporting.action_unapplied_receipt_register_report_xlsx'). \
                report_action(self)

        return res

    @api.onchange('currency_type')
    def onchange_currency_type(self):
        self.currency_ids = False
