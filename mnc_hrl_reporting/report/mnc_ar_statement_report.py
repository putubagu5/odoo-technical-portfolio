from odoo import fields, api, models, _
from odoo.exceptions import UserError


class MncArStatementReport(models.AbstractModel):
    _name = 'report.mnc_hrl_reporting.mnc_ar_statement_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env[data['model']].browse(data['ids'])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'data': data['form']
        }
