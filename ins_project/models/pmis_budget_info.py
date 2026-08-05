from odoo import api, fields, models


class PmisBudgetInfo(models.Model):
    _name = 'pmis.budget.info'
    _description = 'Budget Info'

    program_id = fields.Many2one('pmis.program', 'Program', help='Deprecated')
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project', help='Deprecated')
    main_project_ids = fields.Many2many('pmis.main.project', string='Main Projects', help='NOT USED')

    program_ids = fields.Many2many('pmis.program', string='Programs')
    budget_task_ids = fields.Many2many('pmis.project.task', string='Task/Phase')
    budget_subtask_ids = fields.Many2many(
        'pmis.project.task.line', string='Subtask',
        domain='[("line_id", "in", budget_task_ids)]')
    expenditure_type_ids = fields.Many2many(
        'project.expenditure.type', 'rel_expenditure_info', 'info_id', 'expenditure_id',
        string='Expenditure Type')
    valid_expenditure_type_ids = fields.Many2many(
        'project.expenditure.type', 'rel_valid_expenditure_info', 'info_id', 'expenditure_id',
        string='Expenditure Type', compute='_compute_valid_expenditure_type_ids',
        help='Used as filter')

    line_ids = fields.One2many('pmis.budget.info.line', 'info_id', 'Lines', compute='_compute_lines')
    task_ids = fields.One2many('pmis.budget.info.line', 'task_id', 'Tasks', compute='_compute_lines')
    subtask_ids = fields.One2many('pmis.budget.info.line', 'subtask_id', 'Subtasks', compute='_compute_lines')
    resource_ids = fields.One2many('pmis.budget.info.line', 'resource_id', 'Resources', compute='_compute_lines')

    @api.depends('program_ids', 'budget_task_ids')
    def _compute_valid_expenditure_type_ids(self):
        """ compute function to get the valid expenditures from budget """
        for rec in self:
            exp_ids = False
            if rec.program_ids and rec.budget_task_ids:
                domain = [
                    ('program_id', 'in', rec.program_ids.ids),
                    ('task_status', '=', 'approve'),
                    ('task_id', 'in', rec.budget_task_ids.ids),
                ]
                bgts = self.env['pmis.budget'].search(domain)
                exp_ids = bgts.expenditure_ids.ids if bgts else False
            rec.valid_expenditure_type_ids = exp_ids

    @api.onchange('program_ids')
    def _onchange_program_ids(self):
        """ onchange function to get all data """
        self.ensure_one()
        list_task = [(2, x.id) for x in self.budget_task_ids]
        if self.program_ids:
            # find all pmis.project.task with program_id in program_ids, and
            # state is approve
            domain = [
                ('program_id', 'in', self.program_ids.ids),
                ('state', '=', 'approve'),
            ]
            project_tasks = self.env['pmis.project.task'].search(domain)
            list_task = [(6, 0, project_tasks.ids)]

        self.budget_task_ids = list_task

        list_subtask = [(2, x.id) for x in self.budget_subtask_ids]
        if self.program_ids and self.budget_task_ids:
            # find all pmis.project.task.line with line_id in budget_task_ids
            domain = [
                ('line_id', 'in', self.budget_task_ids.ids),
            ]
            project_task_lines = self.env['pmis.project.task.line'].search(domain)
            list_subtask = [(6, 0, project_task_lines.ids)]
        self.budget_subtask_ids = list_subtask

        list_exp_types = [(2, x.id) for x in self.expenditure_type_ids]
        if self.program_ids and self.budget_task_ids:
            # find all expenditure types taken from budget with task_status approve
            # having same program and task
            domain = [
                ('program_id', 'in', self.program_ids.ids),
                ('task_status', '=', 'approve'),
                ('task_id', 'in', self.budget_task_ids.ids),
            ]
            bgts = self.env['pmis.budget'].search(domain)
            exp_types = bgts.expenditure_ids
            list_exp_types = [(6, 0, exp_types.ids)]

        self.expenditure_type_ids = list_exp_types

    @api.depends('program_ids', 'budget_task_ids', 'budget_subtask_ids', 'expenditure_type_ids')
    def _compute_lines(self):
        """ compute function to get all data in all lines in all tabs """
        # NOTE: the objective of the function is just to group data
        self.ensure_one()  # just one record to process, this acts like a view

        pmis_budget = self.env['pmis.budget']
        pmis_budget_line = self.env['pmis.budget.line']

        line_ids = [(2, x.id) for x in self.line_ids]
        task_ids = [(2, x.id) for x in self.task_ids]
        subtask_ids = [(2, x.id) for x in self.subtask_ids]
        resource_ids = [(2, x.id) for x in self.resource_ids]

        # all elements must be present in order to make this work
        complete = self.program_ids and self.budget_task_ids and self.budget_subtask_ids and self.expenditure_type_ids
        if complete:
            domain = [
                ('program_id', 'in', self.program_ids.ids),
                ('task_status', '=', 'approve'),
            ]
            budget = pmis_budget.search(domain)

            # 1. group by program
            for program in self.program_ids:
                filter_budget = budget.filtered(lambda x: x.program_id == program)
                filter_budget_lines = budget.budget_ids.filtered(lambda x: x.line_id.program_id == program)
                data = {
                    'code': program.code,
                    'name': program.name,
                    'budget': sum(filter_budget.mapped('total_budget')),
                    'amount_pr_reserve': sum(filter_budget_lines.mapped('pr_reserve_amount')),
                    'amount_po_reserve': sum(filter_budget_lines.mapped('po_reserve_amount')),
                    'amount_actual': sum(filter_budget_lines.mapped('actual_budget')),
                }
                line_ids.append((0, 0, data))

            # 2. group by task (pmis.project.task) denoted by budget_task_ids
            domain += [('task_id', 'in', self.budget_task_ids.ids)]
            budget = pmis_budget.search(domain)
            budget_dict = {}
            for b in budget:
                filter_budget = b.budget_info_ids.filtered(lambda x: x.task_id == b.task_id)
                data = {
                    'code': b.task_id.code,
                    'name': b.task_id.name,
                    'budget': 0,
                    'amount_pr_reserve': 0,
                    'amount_po_reserve': 0,
                    'amount_actual': 0,
                }
                budget_dict.setdefault(b.task_id, data)
                budget_dict[b.task_id]['budget'] += b.total_budget
                budget_dict[b.task_id]['amount_pr_reserve'] += sum(filter_budget.mapped('pr_reserve_amount'))
                budget_dict[b.task_id]['amount_po_reserve'] += sum(filter_budget.mapped('po_reserve_amount'))
                budget_dict[b.task_id]['amount_actual'] += sum(filter_budget.mapped('actual_budget'))

            for data in budget_dict.values():
                task_ids.append((0, 0, data))

            # tricky motherfucker
            # 3. group by sub task (pmis.project.task.line) denoted by budget_subtask_ids
            # loop budget_subtask_ids, then add a dict with episode_code as key
            # then try to find the budget line -> budget detail having the same budget_code
            # add to `budget`
            # for every subtask, find the project PR Line from the budget info filtered by subtask
            # and add the respective amount from there to prevent double input
            budget_infos = budget.budget_info_ids
            budget_dict = {}
            for sb in self.budget_subtask_ids:
                dtls = budget_infos.detail_ids.filtered(lambda x: x.code == sb.episode_code)
                project_pr_line = budget_infos.project_pr_line_ids.filtered(lambda x: x.subtask_id.id == sb._origin.id)
                budget_dict.setdefault(sb.episode_code, {
                    'code': sb.episode_code,
                    'name': sb.episode_name,
                    'episode_no': sb.episode_no,
                    'budget': sum(dtls.mapped('amount')),
                    'amount_pr_reserve': 0,
                    'amount_po_reserve': 0,
                    'amount_actual': 0,
                })
                budget_dict[sb.episode_code]['amount_pr_reserve'] += sum(x.budget_line_id.pr_reserve_amount for x in project_pr_line)
                budget_dict[sb.episode_code]['amount_po_reserve'] += sum(x.budget_line_id.po_reserve_amount for x in project_pr_line)
                budget_dict[sb.episode_code]['amount_actual'] += sum(x.budget_line_id.actual_budget for x in project_pr_line)

            for x in budget_dict.values():
                subtask_ids.append((0, 0, x))

            domain = [
                ('line_id.program_id', 'in', self.program_ids.ids),
                ('line_id.task_status', '=', 'approve'),
                ('line_id.task_id', 'in', self.budget_task_ids.ids),
            ]

            # 4. group by pmis.budget.line having certain expenditure
            domain += [('expenditure_type_id', 'in', self.expenditure_type_ids.ids)]
            budget_line = pmis_budget_line.search(domain)
            for bl in budget_line:
                data = {
                    'code': bl.item_code,
                    'name': bl.item_name,
                    'budget': bl.amount_budget_line,
                    'amount_pr_reserve': bl.pr_reserve_amount,
                    'amount_po_reserve': bl.po_reserve_amount,
                    'amount_actual': bl.actual_budget,
                }
                resource_ids.append((0, 0, data))

        self.line_ids = line_ids
        self.task_ids = task_ids
        self.subtask_ids = subtask_ids
        self.resource_ids = resource_ids

    # @api.onchange('program_ids', 'budget_task_ids')
    # def _onchange_program_ids2(self):
    #     """ onchange function to get all """
    #     self.ensure_one()
        # prog_ids = self.program_ids.ids if self.program_ids else []
        # tasks_ids = self.budget_task_ids.ids if self.budget_task_ids else []
        # subtasks_ids = self.budget_subtask_ids.ids if self.budget_subtask_ids else []
        # types_ids = self.expenditure_type_ids.ids if self.expenditure_type_ids else []
        # domain = [
        #     ('program_id', 'in', prog_ids),
        #     ('task_status', '=', 'approve'),
        # ]
        # domain_task = [
        #     ('program_id', 'in', prog_ids),
        #     ('state', '=', 'approve')
        # ]
        # domain_subtask = [
        #     ("line_id", "in", tasks_ids)
        # ]
        # domain_extype = [
        #     ('group_id', 'in', self.budget_task_ids.group_type_id.ids),
        #     ('analytic_account_id', 'in', self.budget_task_ids.analytic_account_id.ids),
        #     ('company_id', '=', self.env.user.company_id.id)
        # ]
        # lines = [(2, x.id) for x in self.line_ids]
        # task_lines = [(2, x.id) for x in self.task_ids]
        # if self.program_ids:
        #     budget = self.env['pmis.budget'].search(domain)
        #     pmis_task_ids = self.env['pmis.project.task'].search(domain_task)
        #     pmis_subtask_ids = self.env['pmis.project.task.line'].search(domain_subtask)
        #     pmis_extype_ids = self.env['project.expenditure.type'].search(domain_extype)

        #     self.budget_task_ids = [(5, 0)]
        #     self.budget_task_ids = [(6, False, list(set(pmis_task_ids.ids)))] if pmis_task_ids else False

        #     self.budget_subtask_ids = [(5, 0)]
        #     self.budget_subtask_ids = [(6, False, list(set(pmis_subtask_ids.ids)))] if pmis_subtask_ids else False

        #     # self.expenditure_type_ids = [(5, 0)]
        #     # self.expenditure_type_ids = [(6, False, pmis_extype_ids.ids)] if pmis_extype_ids else False
        #     for program in self.program_ids:
        #         data1 = {
        #             'code': program.code,
        #             'name': program.name,
        #             'budget': sum(amt.total_budget for amt in budget.filtered(lambda x: x.program_id.code == program.code)),
        #             'amount_pr_reserve': sum(amt.pr_reserve_amount for amt in budget.budget_ids.filtered(lambda x: x.line_id.program_id.code == program.code)),
        #             'amount_po_reserve': sum(amt.po_reserve_amount for amt in budget.budget_ids.filtered(lambda x: x.line_id.program_id.code == program.code)),
        #             'amount_actual': sum(amt.actual_budget for amt in budget.budget_ids.filtered(lambda x: x.line_id.program_id.code == program.code)),
        #         }
        #         lines.append((0, 0, data1))
        #     self.line_ids = lines
        #     # for line in budget:
        #     #     data2 = {
        #     #         'code': line.task_id.code,
        #     #         'name': line.task_id.name,
        #     #         'budget': line.total_budget,
        #     #     }
        #     #     task_lines.append((0, 0, data2))
        #     # self.task_ids = task_lines
        # if not self.program_ids:
        #     self.line_ids = lines
        #     self.task_ids = task_lines
        #     self.budget_task_ids = [(2, x.id) for x in self.budget_task_ids]
        #     self.budget_subtask_ids = [(2, x.id) for x in self.budget_subtask_ids]
        #     self.expenditure_type_ids = [(2, x.id) for x in self.expenditure_type_ids]
        # if self.budget_task_ids:
        #     domain.append(('task_id', 'in', tasks_ids))
        #     budget = self.env['pmis.budget'].search(domain)
        #     pmis_extype_ids = [(5, 0, 0)]
        #     pmis_extype_ids += [(4, x.expenditure_type_id.id) for x in budget.budget_ids if x.expenditure_type_id]
        #     for line in budget:
        #         data = {
        #             'code': line.task_id.code,
        #             'name': line.task_id.name,
        #             'budget': line.total_budget,
        #             'amount_pr_reserve': sum(amt.pr_reserve_amount for amt in line.budget_info_ids.filtered(lambda x: x.task_id == line.task_id)),
        #             'amount_po_reserve': sum(amt.po_reserve_amount for amt in line.budget_info_ids.filtered(lambda x: x.task_id == line.task_id)),
        #             'amount_actual': sum(amt.actual_budget for amt in line.budget_info_ids.filtered(lambda x: x.task_id == line.task_id)),
        #         }
        #         task_lines.append((0, 0, data))
        #     self.task_ids = task_lines
        #     self.expenditure_type_ids = pmis_extype_ids
        #     return {
        #         'domain': {
        #             'expenditure_type_ids': [
        #                 ('group_id', 'in', self.budget_task_ids.group_type_id.ids),
        #                 ('analytic_account_id', 'in', self.budget_task_ids.analytic_account_id.ids),
        #                 ('company_id', '=', self.env.user.company_id.id)
        #             ],
        #         }
        #     }
        # if not self.budget_task_ids:
        #     self.task_ids = task_lines

    # @api.onchange('budget_subtask_ids', 'expenditure_type_ids')
    # def _onchange_lines_ids(self):
    #     """ function to show the budget from source """
    #     # find budget with program and the same task, limit 1 and get the line
    #     # construct into dict with the exact characteristic
    #     self.ensure_one()
    #     prog_ids = self.program_ids.ids if self.program_ids else []
    #     tasks_ids = self.budget_task_ids.ids if self.budget_task_ids else []
    #     subtasks_ids = self.budget_subtask_ids.ids if self.budget_subtask_ids else []
    #     types_ids = self.expenditure_type_ids.ids if self.expenditure_type_ids else []
    #     domain = [
    #             ('line_id.program_id', 'in', prog_ids),
    #             ('line_id.task_id', 'in', tasks_ids),
    #             # ('line_id.task_id.episode_ids', 'in', subtasks_ids),
    #             ('line_id.task_status', '=', 'approve'),
    #         ]
    #     subtask_lines = [(2, x.id) for x in self.subtask_ids]
    #     resource_lines = [(2, x.id) for x in self.resource_ids]
    #     if self.budget_subtask_ids:
    #         budget = self.env['pmis.budget.line'].search(domain)

    #         # create a dictionary to contain the budget grouped by `code`
    #         # this is done by looping the pmis.project.task.line (budget_subtask_ids)
    #         budget_dict = {}
    #         for dt in self.budget_subtask_ids:
    #             budget_dict.setdefault(dt.episode_line_id, {
    #                 'code': dt.episode_code,
    #                 'name': dt.episode_name,
    #                 'episode_no': dt.episode_no,
    #                 'budget': 0,
    #                 'amount_pr_reserve': 0,
    #                 'amount_po_reserve': 0,
    #                 'amount_actual': 0,
    #             })
    #             dtls = budget.detail_ids.filtered(lambda x: x.no in dt.mapped('episode_no'))
    #             budget_dict[dt.episode_line_id]['budget'] = sum(dtls.mapped('amount'))
    #             budget_dict[dt.episode_line_id]['amount_pr_reserve'] += sum(amt.pr_reserve_amount for amt in budget.filtered(lambda x: x.task_id == dt.line_id))
    #             budget_dict[dt.episode_line_id]['amount_po_reserve'] += sum(amt.po_reserve_amount for amt in budget.filtered(lambda x: x.task_id == dt.line_id))
    #             budget_dict[dt.episode_line_id]['amount_actual'] += sum(amt.actual_budget for amt in budget.filtered(lambda x: x.task_id == dt.line_id))

    #         for bd in budget_dict.values():
    #             subtask_lines.append((0, 0, bd))

    #         self.subtask_ids = subtask_lines

    #     if not self.budget_subtask_ids:
    #         self.subtask_ids = subtask_lines

    #     if self.expenditure_type_ids:
    #         domain.append(('expenditure_type_id', 'in', types_ids))
    #         budget = self.env['pmis.budget.line'].search(domain)
    #         for detail in budget:
    #             data = {
    #                     'code': detail.item_name,
    #                     'name': detail.item_code,
    #                     'budget': detail.amount_budget_line,
    #                     'amount_pr_reserve': detail.pr_reserve_amount,
    #                     'amount_po_reserve': detail.po_reserve_amount,
    #                     'amount_actual': detail.actual_budget,
    #                 }
    #             resource_lines.append((0, 0, data))
    #         self.resource_ids = resource_lines

    #     if not self.expenditure_type_ids:
    #         self.resource_ids = resource_lines
