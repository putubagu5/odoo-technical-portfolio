from odoo import _, fields, models, api


class WizardPurchaseRequisition(models.Model):
    _name = 'wizard.purchase.requisition'

    @api.model
    def _get_default_company_id(self):
        return self.env.user.company_id.id

    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=_get_default_company_id)

    @api.onchange('date_start', 'date_end')
    def onchange_periode(self):
        if self.date_start and self.date_end:
            if self.date_end < self.date_start:
                return {
                    'value': {
                        'date_end': None,
                        'date_start': None
                    },
                    'warning': {
                        'title': 'Warning',
                        'message': 'Cannot back date!'
                    }
                }

    def generate(self):
        report = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'mnc_gln_reporting.purchase_requisition_list_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        return report.report_action(self)
