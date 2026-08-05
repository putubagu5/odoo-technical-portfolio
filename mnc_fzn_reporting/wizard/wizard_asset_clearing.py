from odoo import _, fields, models, api


class WizardAssetClearing(models.Model):
    _name = 'wizard.asset.clearing'

    def _get_account(self):
        return self.env['account.account'].search([('code', '=', '1239001')], limit=1)

    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    account_id = fields.Many2one(comodel_name='account.account', string='Account', default=_get_account)

    # receipt_num = fields.Char(string='Receipt Num')

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
            [('report_name', '=', 'mnc_fzn_reporting.asset_clearing_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        return report.report_action(self)
