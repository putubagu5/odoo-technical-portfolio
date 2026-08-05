from odoo import api, fields, models
from odoo.exceptions import Warning


class PmisCopyBudget(models.Model):
    _name = 'pmis.copy.budget'
    _description = 'Copy Budget'
    _rec_name = 'source_program_id'

    source_program_id = fields.Many2one('pmis.program', 'Program')
    source_task_id = fields.Many2one('pmis.project.task', 'Task')
    destination_program_id = fields.Many2one('pmis.program', 'Program')
    destination_task_id = fields.Many2one('pmis.project.task', 'Task')
    is_selected_all = fields.Boolean('Select All Lines', default=False)
    line_ids = fields.One2many('pmis.copy.budget.line', 'budget_id', 'Lines')

    def _check_group_type(self):
        """ checking group_type_id in source and destination task """
        for rec in self:
            if rec.source_task_id.group_type_id != rec.destination_task_id.group_type_id:
                raise Warning('Budget Copy could only happen with the same group type')

    def button_copy(self):
        """ function to copy the budget from source to destination """
        # make sure one more time that the group_type_id of both task are same
        # then from line_ids with do_copy True, construct data dict and
        # generate new budget with program and task based on destination
        self._check_group_type()
        domain = [
            ('program_id', '=', self.source_program_id.id),
            ('task_id', '=', self.source_task_id.id),
        ]
        budget = self.env['pmis.budget'].search(domain, limit=1)

        lines = []
        for line in self.line_ids.filtered(lambda x: x.do_copy):
            data = {
                'no': line.no,
                'expenditure_type_id': line.expenditure_type_id.id,
                'description': line.description,
                'pax': line.pax,
                'eps': line.eps,
                'day': line.day,
                'rate': line.rate,
                'average_by_eps': line.average_by_eps,
                'budget': line.budget,
                'remarks': line.remarks,
            }
            lines.append((0, 0, data))

        if lines:  # only create if there are lines
            budget_data = {
                'name': '%s COPY' % budget.name,
                'main_project_id': budget.main_project_id.id,
                'program_id': self.destination_program_id.id,
                'task_id': self.destination_task_id.id,
                'date_start': budget.date_start,
                'date_end': budget.date_end,
                'budget_ids': lines,
            }
            self.env['pmis.budget'].create(budget_data)

        return True

    def button_show(self):
        """ function to show the budget from source """
        # find budget with program and the same task, limit 1 and get the line
        # construct into dict with the exact characteristic
        domain = [
            ('program_id', '=', self.source_program_id.id),
            ('task_id', '=', self.source_task_id.id),
        ]
        budget = self.env['pmis.budget'].search(domain, limit=1)
        lines = [(2, x.id) for x in self.line_ids]
        for line in budget.budget_ids:
            data = {
                'no': line.no,
                'expenditure_type_id': line.expenditure_type_id.id,
                'description': line.description,
                'pax': line.pax,
                'eps': line.eps,
                'day': line.day,
                'rate': line.rate,
                'average_by_eps': line.average_by_eps,
                'budget': line.budget,
                'remarks': line.remarks,
            }
            lines.append((0, 0, data))
        self.line_ids = lines
        return True

    def button_select_all_lines(self):
        """ function to select all lines in copy budget """
        for rec in self:
            rec.is_selected_all = True
            for line in rec.line_ids:
                line.do_copy = True
        return True

    def button_unselect_all_lines(self):
        """ function to unselect all lines in copy budget """
        for rec in self:
            rec.is_selected_all = False
            for line in rec.line_ids:
                line.do_copy = False
        return True
