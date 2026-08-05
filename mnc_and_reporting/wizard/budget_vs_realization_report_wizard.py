from odoo import models, fields, api, _


class BudgetVSRealizationReportWizard(models.Model):
    _name = 'budget.vs.realization.report.wizard'
    _inherit = ['and.report.wizard']
    _description = 'Budget VS Realization Report Wizard'

    report_type = fields.Selection(
        selection_add=[
            ('budget_vs_realization_report', 'Budget VS Realization Report')
        ],
    )

    program_code_ids = fields.Many2many(
        comodel_name='pmis.project.task.line',
        string='Program Codes',
        help='Program codes used to filter report',
    )

    item_code_ids = fields.Many2many(
        comodel_name='project.expenditure.type',
        relation='budget_vs_realization_wizard_project_expenditure_type_rel',
        string='Item Codes',
        help='Item codes used to filter report',
    )

    @api.onchange('program_code_type')
    def onchange_program_code_type(self):
        self.program_code_ids = False

    @api.onchange('item_code_type')
    def onchange_item_code_type(self):
        self.item_code_ids = False

    def generate_report_xlsx(self):
        res = super(BudgetVSRealizationReportWizard, self).generate_report_xlsx()
        if self.report_type and self.report_type == 'budget_vs_realization_report':
            return self.env.ref('mnc_and_reporting.action_budget_vs_realization_report_xlsx'). \
                report_action(self)

        return res
