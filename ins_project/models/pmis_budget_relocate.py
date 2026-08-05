from odoo import api, fields, models
from odoo.exceptions import Warning


class PmisBudgetRelocate(models.Model):
    _name = 'pmis.budget.relocate'
    _description = 'Budget Relocate'
    _rec_name = 'main_project_id'

    main_project_id = fields.Many2one('pmis.main.project', 'Main Project')
    source_program_id = fields.Many2one('pmis.program', 'Program')
    source_task_id = fields.Many2one('pmis.project.task', 'Task')
    source_analytic_acc_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='source_task_id.analytic_account_id')
    destination_program_id = fields.Many2one('pmis.program', 'Program')
    destination_task_id = fields.Many2one('pmis.project.task', 'Task')
    destination_analytic_acc_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='destination_task_id.analytic_account_id')
    line_ids = fields.One2many('pmis.budget.relocate.line', 'relocate_id', 'Lines')
    valid_destination_budget_line_ids = fields.Many2many(
        'pmis.budget.line', 'rel_destination_budget_line', 'relocate_id',
        'budget_line_id', 'Valid Destination Budget Lines',
        compute='_compute_valid_destination_budget_line_ids')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], 'State', default='draft')
    additional_ids = fields.One2many('pmis.budget.additional', 'relocate_id',
                                     'Additional Items')
    reference = fields.Char(string='Document Reference')

    @api.depends('destination_program_id', 'destination_task_id')
    def _compute_valid_destination_budget_line_ids(self):
        """ compute function to get the valid destination budget line """
        # NOTE this is used as filters for destination lines
        for rec in self:
            # find budget having main project and program
            domain = [
                ('main_project_id', '=', self.main_project_id.id),
                ('program_id', '=', self.destination_program_id.id),
                ('task_id', '=', self.destination_task_id.id),
            ]
            budget = self.env['pmis.budget'].search(domain)
            valid_lines = [(6, 0, [x.id for x in budget.budget_ids])]
            rec.valid_destination_budget_line_ids = valid_lines

    @api.constrains('source_task_id', 'destination_task_id')
    def _check_difference_task(self):
        """ constrains function to check budget with amount_transfer """
        if self.source_task_id.analytic_account_id != self.destination_task_id.analytic_account_id:
            raise Warning('Source and Destination Analytic Account must be the same!')

    @api.onchange('budget_line_id')
    def _onchange_budget_line_id(self):
        """ onchange function to trigger line creation """
        for rec in self:
            lines = [(2, x.id) for x in rec.line_ids]
            if rec.budget_line_id:
                lines += [
                    (0, 0, {'no': x.no, 'amount': x.amount}) for x in rec.budget_line_id.detail_ids
                ]
            rec.line_ids = lines

    def _get_previous_relocate(self):
        """ helper function to get the previous relocate data exactly one """
        domain = [
            ('main_project_id', '=', self.main_project_id.id),
            ('source_program_id', '=', self.source_program_id.id),
            ('destination_program_id', '=', self.destination_program_id.id),
            ('id', '!=', self.id),
            ('id', '<', self.id),
        ]
        relocate = self.env['pmis.budget.relocate'].search(domain, order='id DESC')
        return relocate

    def _get_same_source_line(self, lines, line):
        """ helper function to get the same line and return the record """
        return lines.filtered(lambda x: x.source_id == line.source_id)

    def button_show_budget(self):
        """ function to show budget data """
        # find pmis.budget data with main_project_id and source_program_id
        # then add and show in lines
        domain = [
            ('main_project_id', '=', self.main_project_id.id),
            ('program_id', '=', self.source_program_id.id),
            ('task_id', '=', self.source_task_id.id),
            ('task_status', '=', 'approve'),
            ('company_id', '=', self.main_project_id.company_id.id),
        ]
        budget = self.env['pmis.budget'].search(domain)
        lines = [(2, x.id) for x in self.line_ids]
        add_lines = [(2, x.id) for x in self.additional_ids]
        for line in budget.budget_info_ids:
            data = {
                'no': line.no,
                'source_id': line.id,
                'description': line.description,
                'budget': line.remaining_amount,
            }
            lines.append((0, 0, data))

            add_data = {
                'no': line.no,
                'source_id': line.id,
                'description': '',
                'budget': line.remaining_amount,
            }
            add_lines.append((0, 0, add_data))

        self.line_ids = lines
        self.additional_ids = add_lines

    def button_draft(self):
        """ function to set to draft """
        for rec in self:
            rec.write({'state': 'draft'})

    # def button_approve(self):
    #     """ function to set to approve """
    #     for rec in self:
    #         # NOTE: when approved, assign to each source and destination lines
    #         # for destination_id, write the amount_budget_in
    #         # for source_id, write the amount_budget_out
    #         # consider also the previous relocate data, we must take
    #         # amount_transfer based on lines with same source in lines
    #         prev_relocate = rec._get_previous_relocate()  # get previous data
    #         for line in rec.line_ids:
    #             same_line = False
    #             if prev_relocate:  # exists, then get the same source line
    #                 same_line = rec._get_same_source_line(prev_relocate.line_ids, line)
    #             amt_trf = sum(same_line.mapped('amount_transfer')) if same_line else 0
    #             # line.destination_id.write({'amount_budget_in': line.amount_transfer + amt_trf})
    #             # line.source_id.write({'amount_budget_out': line.amount_transfer + amt_trf})
    #             line.destination_id.amount_budget_in = line.amount_transfer + amt_trf
    #             line.source_id.amount_budget_out = line.amount_transfer + amt_trf

    #         # update amount_budget_out using the amount_budget_in from the line
    #         # only take lines with expenditure_type_id
    #         no = 0
    #         for line in rec.additional_ids.filtered(lambda x: x.expenditure_type_id):
    #             same_line = False
    #             if prev_relocate:  # exists, then get the same source line
    #                 same_line = rec._get_same_source_line(prev_relocate.line_ids, line)
    #             if same_line:
    #                 tmp_out = line.source_id.amount_budget_out
    #                 line.source_id.amount_budget_out = line.amount_budget_in + tmp_out
    #                 # line.source_id.write({
    #                 #     'amount_budget_out': line.amount_budget_in + line.source_id.amount_budget_out,
    #                 # })

    #                 # find the budget of the destination
    #                 destination_budget = same_line.destination_id.line_id
    #                 if destination_budget and line.expenditure_type_id:
    #                     # get the latest number add by one and construct data
    #                     no = len(destination_budget.budget_ids) + 1
    #                     dest_data = {
    #                         'no': no,
    #                         'expenditure_type_id': line.expenditure_type_id.id,
    #                         'description': line.description,
    #                         'pax': line.pax,
    #                         'eps': line.eps,
    #                         'day': line.day,
    #                         'rate': line.rate,
    #                         'amount_budget_in': line.amount_budget_in,
    #                     }
    #                     destination_budget.budget_ids = [(0, 0, dest_data)]

    #         rec.write({'state': 'approve'})

    def button_approve(self):
        """ function to set to approve """
        for rec in self:
            # NOTE: when approved, assign to each source and destination lines
            # for destination_id, write the amount_budget_in
            # for source_id, write the amount_budget_out
            # consider also the previous relocate data, we must take
            # amount_transfer based on lines with same source in lines
            prev_relocate = rec._get_previous_relocate()  # get previous data
            for line in rec.line_ids:
                # same_line = False
                # if prev_relocate:  # exists, then get the same source line
                #     same_line = rec._get_same_source_line(prev_relocate.line_ids, line)
                # amt_trf = sum(same_line.mapped('amount_transfer')) if same_line else 0
                line.destination_id.amount_budget_in = line.amount_transfer + line.destination_id.amount_budget_in
                line.source_id.amount_budget_out = line.amount_transfer + line.source_id.amount_budget_out

            # update amount_budget_out using the amount_budget_in from the line
            # only take lines with expenditure_type_id
            no = 0
            for line in rec.additional_ids.filtered(lambda x: x.expenditure_type_id):
                same_line = False
                if prev_relocate:  # exists, then get the same source line
                    same_line = rec._get_same_source_line(prev_relocate.line_ids, line)
                if same_line:
                    line.source_id.write({
                        'amount_budget_out': line.total_budget + line.source_id.amount_budget_out,
                    })

                    # find the budget of the destination
                    destination_budget = line.relocate_id.destination_program_id
                    domain = [
                        ('program_id', '=', destination_budget.id),
                        ('task_id', '=', rec.destination_task_id.id),
                    ]
                    destination_budget = self.env['pmis.budget'].search(domain, limit=1)
                    if destination_budget and line.expenditure_type_id:
                        # get the latest number add by one and construct data
                        no = len(destination_budget.budget_ids) + 1
                        dest_data = {
                            'no': no,
                            'expenditure_type_id': line.expenditure_type_id.id,
                            'description': line.description,
                            'pax': line.pax,
                            'eps': line.eps,
                            'day': line.day,
                            'rate': line.rate,
                        }
                        destination_budget.budget_ids = [(0, 0, dest_data)]

            rec.write({'state': 'approve'})

    def button_confirm(self):
        """ function to set to confirm """
        for rec in self:
            rec.write({'state': 'confirm'})

    def button_cancel(self):
        """ function to set to cancel """
        for rec in self:
            rec.write({'state': 'cancel'})
