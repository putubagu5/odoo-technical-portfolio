from odoo import api, fields, models


class ReportBudgetSummary(models.AbstractModel):
    _name = 'report.ins_project.report_budget_summary_container'
    _description = 'Budget Report'

    def _prepare_report_data(self):
        """ function to return data to print in report """
        # get all active_ids then browse records
        ids = self._context.get('active_ids', [])
        budgets = self.env['pmis.budget'].search([('id', 'in', ids)],
                                                 order='program_id')

        # loop records, construct a dict with partner_id as key, then all
        # invoice records
        data = {}
        for bdgt in budgets:
            data.setdefault(bdgt.program_id.id, {
                'item_code': bdgt.program_id.code or '-',
                'description': bdgt.program_id.name or '-',
                'budget': bdgt.total_budget or 0,
                'barter': bdgt.total_budget or 0,
                'total_barter': bdgt.total_budget or 0,
                'barter_eps': bdgt.episode_number or 0,
                'allocation': 100,
            })

        # sort data: loop items, use key from index 1 (the values), sort by code
        data = sorted(data.items(), key=lambda x: x[1]['code'])

        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        """ inherit function to process report data """
        # convert data to dict (this is from button_print)
        date_print = data['date_print']
        note = data['note']
        budgets = dict(self._prepare_report_data() or {})
        # then clean the dict, remove any context related keys and values
        if budgets.get('context'):
            budgets.pop('context')
        if budgets.get('report_type'):
            budgets.pop('report_type')
        if budgets.get('float_compare'):
            budgets.pop('float_compare')

        result = {
            'date_print': date_print,
            'note': note,
            'budgets': budgets.values(),
        }
        return result
