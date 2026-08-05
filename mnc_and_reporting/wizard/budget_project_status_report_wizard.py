from odoo import models, fields, api, _


class BudgetProjectStatusReportWizard(models.Model):
    _name = 'budget.project.status.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Budget Project Status Report Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('budget_project_status_report', 'Budget Project Status Report')
        ],
    )

    def generate_report_xlsx(self):
        res = super(BudgetProjectStatusReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'budget_project_status_report':
            return self.env.ref('mnc_and_reporting.action_budget_project_status_report_xlsx').\
                report_action(self)

        return res
