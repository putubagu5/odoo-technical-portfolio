from odoo import models, fields, api, _


class PurchaseReqListReportWizard(models.Model):
    _name = 'purchase.requisition.list.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Purchase Requisition List Report Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('purchase_requisition_list_report', 'POR - Purchase Requisition List')
        ],
    )

    requestor_ids = fields.Many2many(
        comodel_name='res.users',
        string='Requestor',
        help='Requested used to filter report',
    )

    analytic_account_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help='Analytic Account used to filter report',
    )

    # @api.onchange('supplier_type')
    # def onchange_supplier_type(self):
    #     self.supplier_ids = False

    def generate_report_xlsx(self):
        res = super(PurchaseReqListReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'purchase_requisition_list_report':
            return self.env.ref('mnc_and_reporting.action_purchase_requisition_list_xlsx'). \
                report_action(self)

        return res
