from odoo import api, fields, models


class PmisBudgetInfoLine(models.Model):
    _name = 'pmis.budget.info.line'
    _description = 'Budget Info Line'

    code = fields.Char('Code')
    name = fields.Char('Name')
    episode_no = fields.Char('Episode No')
    budget = fields.Float('Budget')
    amount_po_reserve = fields.Float('PO Reserve')
    amount_pr_reserve = fields.Float('PR Reserve')
    amount_actual = fields.Float('Actual')
    amount_remaining = fields.Float('Budget Remaining', compute='_compute_budget_remaining')
    info_id = fields.Many2one('pmis.budget.info', 'Related Line', ondelete='cascade')
    task_id = fields.Many2one('pmis.budget.info', 'Related Task', ondelete='cascade')
    subtask_id = fields.Many2one('pmis.budget.info', 'Related Subtask', ondelete='cascade')
    resource_id = fields.Many2one('pmis.budget.info', 'Related Resource', ondelete='cascade')

    @api.depends('budget', 'amount_pr_reserve', 'amount_po_reserve', 'amount_actual')
    def _compute_budget_remaining(self):
        """ compute function to calculate budget remaining """
        for rec in self:
            rec.amount_remaining = rec.budget - rec.amount_pr_reserve - rec.amount_po_reserve - rec.amount_actual

    def action_open_pr_entries(self):
        """ function to get the PR entries """
        # the chain of data works from info_id -> pmis.budget via domain
        # -> budget_ids -> project_pr_line_ids -> line_id, map by request_id
        self.ensure_one()
        request_lines = False
        domain = [
            ('program_id', 'in', self.info_id.program_ids.ids),
            ('task_status', '=', 'approve'),
        ]
        if self.info_id and self.info_id.program_ids:
            budgets = self.env['pmis.budget'].search(domain)
            request_lines = budgets.mapped('budget_ids.project_pr_line_ids.line_id.request_id')

        if request_lines:
            return {
                'name': 'Purchase Request',
                'view_mode': 'tree,form',
                'res_model': 'purchase.request',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', request_lines.ids)],
            }

    def action_open_po_entries(self):
        """ function to get the PO entries """
        # the chain of data works from info_id -> pmis.budget via domain
        # -> budget_ids -> project_pr_line_ids -> po_line_id, map by order_id
        self.ensure_one()
        purchase_lines = False
        domain = [
            ('program_id', 'in', self.info_id.program_ids.ids),
            ('task_status', '=', 'approve'),
        ]
        if self.info_id and self.info_id.program_ids:
            budgets = self.env['pmis.budget'].search(domain)
            purchase_lines = budgets.mapped('budget_ids.project_pr_line_ids.po_line_id.order_id')

        if purchase_lines:
            return {
                'name': 'Purchase Order',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', purchase_lines.ids)],
            }

    def action_open_budget_entries(self):
        return True
