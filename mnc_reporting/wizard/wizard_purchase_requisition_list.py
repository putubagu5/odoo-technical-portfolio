from odoo import _, fields, models, api


class WizardPurchaseRequisition(models.Model):
    _name = 'wizard.purchase.requisition'

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    def default_analytic_account_ids(self):
        account_obj = self.env['account.analytic.account']
        company_id = self.env['res.company'].sudo().browse(self.env.user.company_id.id)
        domain = [('company_id', '=', company_id.id)]
        analytic_account_ids = account_obj.sudo().search(domain)
        return analytic_account_ids

    def default_requestor_ids(self):
        requestor_obj = self.env['res.users']
        company_id = self.env['res.company'].sudo().browse(self.env.user.company_id.id)
        domain = [('company_id', '=', company_id.id)]
        users_ids = requestor_obj.sudo().search(domain)
        return users_ids

    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    get_all_requestor = fields.Boolean(default=True)
    users_ids = fields.Many2many(comodel_name='res.users', string='Requestor')
    get_all_account = fields.Boolean(default=True)
    analytic_account_ids = fields.Many2many(comodel_name='account.analytic.account', string='Cost Center')

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

    @api.onchange('get_all_account')
    def _onchange_get_all_account(self):
        if self.get_all_account:
            self.analytic_account_ids = self.default_analytic_account_ids()
        else:
            self.analytic_account_ids = False

    @api.onchange('get_all_requestor')
    def _onchange_get_all_requestor(self):
        if self.get_all_requestor:
            self.users_ids = self.default_requestor_ids()
        else:
            self.users_ids = False

    def generate(self):
        report = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'mnc_reporting.purchase_requisition_list_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        return report.report_action(self)
