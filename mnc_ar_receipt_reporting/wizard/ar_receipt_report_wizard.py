from datetime import date, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ARReceiptReportWizard(models.TransientModel):
    _name = 'ar.receipt.report.wizard'
    _description = 'AR Receipt Report Wizard'

    start_date = fields.Date(
        string='Start Date',
        required=True,
        help='Start date parameter used to filter AR receipt report',
        default=date.today(),
    )

    end_date = fields.Date(
        string='End Date',
        required=True,
        help='End date parameter used to filter AR receipt report',
        default=date.today() + timedelta(days=30),
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

    def generate_ar_receipt_report_xlsx(self):
        return self.env.ref('mnc_ar_receipt_reporting.action_ar_receipt_report_xlsx').\
            report_action(self)
    
    @api.constrains('start_date', 'end_date')
    def constrains_date(self):
        for wizard in self:
            if wizard.start_date > wizard.end_date:
                raise ValidationError(
                    _('Invalid period!')
                )