from odoo import _, fields, models, api


class WizardTrialBalance(models.Model):
    _name = 'wizard.trial.balance'

    @api.model
    def _get_default_company_id(self):
        return self.env.user.company_id.id

    def default_account_ids(self):
        account_obj = self.env['account.account']
        company_id = self.env['res.company'].sudo().browse(self.env.user.company_id.id)
        domain = [('company_id', '=', company_id.id)]
        account_ids = account_obj.sudo().search(domain)
        return account_ids

    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    get_all_account = fields.Boolean()
    account_ids = fields.Many2many('account.account', string='Account', required=True, readonly=False)
    company_id = fields.Many2one('res.company', default=_get_default_company_id)

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
        if self.get_all_account == True:
            self.account_ids = self.default_account_ids()
        else:
            self.account_ids = False

    def generate(self):
        report = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'mnc_gln_reporting.trial_balance_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        return report.report_action(self)
