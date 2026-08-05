from odoo import models, fields, api, _


class InvoicePrepaymentPaidSupplierWizard(models.TransientModel):
    _name = 'invoice.prepayment.paid.supplier.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Invoice Prepayment Paid Supplier Wizard'
    _rec_name = 'report_type'

    report_type = fields.Selection(
        selection_add=[
            ('inv_prepayment_paid_supplier', 'Invoice Prepayment Paid Supplier')
        ],
    )

    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Accounts',
        help='Chart of account used to filter report',
    )

    prepayment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('partial', 'Partially Paid'),
            ('reversed', 'Reversed'),
            ('invoicing_legacy', 'Invoicing App Legacy')
        ],
        string="Prepayment Status",
        help='Prepayment status used to filter report'
    )

    def generate_report_xlsx(self):
        res = super(InvoicePrepaymentPaidSupplierWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'inv_prepayment_paid_supplier':
            return self.env.ref('mnc_and_reporting.action_inv_prepayment_paid_supplier_xlsx'). \
                report_action(self)

        return res

    @api.onchange('account_type')
    def onchange_account_type(self):
        self.account_ids = False
