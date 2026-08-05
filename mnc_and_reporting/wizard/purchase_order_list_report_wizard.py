from odoo import models, fields, api, _


class PurchaseOrderListReportWizard(models.Model):
    _name = 'purchase.order.list.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Purchase Order List Report Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('purchase_order_list_report', 'Purchase Order List Report')
        ],
    )

    supplier_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Suppliers',
        help='Suppliers used to filter report',
    )

    buyer_ids = fields.Many2many(
        comodel_name='res.buyer',
        string='Buyers',
        help='Buyers used to filter report'
    )

    type_pr_ids = fields.Many2one(
        comodel_name='purchase.request.type.second',
        string='Type PR',
        help='Type PR used to filter report'
    )

    item_ids = fields.Many2many(
        comodel_name='product.product',
        string='Item',
        help='Item used to filter report'
    )

    @api.onchange('supplier_type')
    def onchange_supplier_type(self):
        self.supplier_ids = False

    def generate_report_xlsx(self):
        res = super(PurchaseOrderListReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'purchase_order_list_report':
            return self.env.ref('mnc_and_reporting.action_purchase_order_list_report_xlsx'). \
                report_action(self)

        return res
