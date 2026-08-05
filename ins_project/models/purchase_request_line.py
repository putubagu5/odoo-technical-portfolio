from odoo import api, fields, models
from odoo.exceptions import Warning


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    project_ids = fields.One2many(
        comodel_name="project.pr.line",
        inverse_name="line_id",
        string="Project Details",
        copy=True,
    )
    episodes = fields.Char('Episodes', compute='_compute_episodes')

    @api.depends('project_ids', 'project_ids.subtask_id')
    def _compute_episodes(self):
        """ compute function to get episodes """
        for rec in self:
            episodes = ''
            if rec.project_ids:
                episodes = ','.join(rec.project_ids.mapped('subtask_id.episode_name'))
            rec.episodes = episodes

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('project_ids', []):  # check if project_ids exist
            lines = vals.get('project_ids', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                line[2].update({'line_number': idx + 1})
        res = super(PurchaseRequestLine, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(PurchaseRequestLine, self).write(vals)
        # find project_ids, rewrite the line number
        for idx, line in enumerate(self.project_ids):
            line.line_number = idx + 1
            # line.amount = self.line_id.estimated_cost * (line.percentage / 100)
        return res


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    # def button_draft(self):
    #     for pr_line in self.line_ids:
    #         for line in pr_line.project_ids:
    #             budget_id = line.program_id
    #             amount_prline = line.amount
    #             for detail in budget_id.budget_info_ids:
    #                 detail.write({
    #                     'pr_reserve_amount': 0,
    #                 })
    #     return super(PurchaseRequest, self).button_draft()

    def button_to_approve(self):
        for pr_line in self.line_ids:
            for line in pr_line.project_ids:
                # NOTE program_id here has pmis.budget data
                total = 0.0
                total += line.percentage
                program = line.program_id
                task = line.task_id
                subtask = line.subtask_id
                category = line.expenditure_type_id.category_id.expenditure_category_id
                subcategory = line.expenditure_type_id.category_id
                budget = 0.0
                # budget_id = line.program_id
                if total > 100:
                    raise Warning('Sum Percentage exceeds 100 percent')
                if subcategory.budget_type == 'absolute':
                    domain = [
                        ('program_id', '=', program.program_id.id),
                        ('task_id', '=', task.id),
                        ('task_status', '=', 'approve'),
                    ]

                    budget_ids = self.env['pmis.budget'].search(domain)
                    for rec in budget_ids:
                        for budget_line in rec.budget_ids.filtered(lambda x: x.subcategory_id.id == subcategory.id):
                            budget += budget_line.remaining_amount
                    if budget < line.amount:
                        raise Warning("Budget exceeds the limit for line number {} by subcategory expenditure.".format(pr_line.line_number))
                    # else:
                    #     for detail in budget_ids.budget_info_ids.filtered(lambda x: x.expenditure_type_id.category_id.id == subcategory.id):
                    #         detail.write({
                    #             'pr_reserve_amount': line.amount,
                    #         })
                else:
                    if category.budget_type == 'absolute':
                        domain = [
                            ('program_id', '=', program.program_id.id),
                            ('task_id', '=', task.id),
                            ('task_status', '=', 'approve'),
                        ]

                        budget_ids = self.env['pmis.budget'].search(domain)
                        for rec in budget_ids:
                            for budget_line in rec.budget_ids.filtered(lambda x: x.category_id.id == category.id):
                                budget += budget_line.remaining_amount
                        if budget < line.amount:
                            raise Warning("Budget exceeds the limit for line number {} by expenditure category.".format(pr_line.line_number))
                        # else:
                        #     for detail in budget_ids.budget_info_ids.filtered(lambda x: x.expenditure_type_id.category_id.expenditure_category_id.id == category.id):
                        #         detail.write({
                        #             'pr_reserve_amount': line.amount,
                        #         })
                    else:
                        if subtask.budget_type == 'absolute':
                            domain = [
                                ('program_id', '=', program.program_id.id),
                                ('task_id', '=', task.id),
                                ('task_status', '=', 'approve'),
                            ]

                            budget_ids = self.env['pmis.budget'].search(domain)
                            for rec in budget_ids:
                                for budget_line in rec.budget_ids.filtered(lambda x: x.expenditure_type_id.id == line.expenditure_type_id.id):
                                    for detail in budget_line.detail_ids.filtered(lambda x: x.no == subtask.episode_no):
                                        budget += detail.amount
                            if budget < line.amount:
                                raise Warning("Budget exceeds the limit for line number {} by sub task.".format(pr_line.line_number))
                            # else:
                            #     for detail in budget_ids.budget_info_ids.filtered(lambda x: x.expenditure_type_id.id == line.expenditure_type_id.id):
                            #         detail.write({
                            #             'pr_reserve_amount': line.amount,
                            #         })
                        else:
                            if task.budget_type == 'absolute':
                                domain = [
                                    ('task_id', '=', task.id),
                                    ('task_status', '=', 'approve'),
                                ]

                                budget_ids = self.env['pmis.budget'].search(domain)
                                for rec in budget_ids:
                                    budget += rec.total_remaining
                                if budget < line.amount:
                                    raise Warning("Budget exceeds the limit for line number {} by task.".format(pr_line.line_number))
                                # else:
                                #     budget_ids.budget_ids.write({
                                #         'pr_reserve_amount': line.amount,
                                #     })
                            else:
                                if program.program_id.budget_type == 'absolute':
                                    domain = [
                                        ('program_id', '=', program.program_id.id),
                                        ('task_status', '=', 'approve'),
                                    ]

                                    budget_ids = self.env['pmis.budget'].search(domain)
                                    for rec in budget_ids:
                                        budget += rec.total_remaining
                                    if budget < line.amount:
                                        raise Warning("Budget exceeds the limit for line number {} by program.".format(pr_line.line_number))
                                    # else:
                                    #     budget_ids.budget_ids.write({
                                    #         'pr_reserve_amount': line.amount,
                                    #     })

        return super(PurchaseRequest, self).button_to_approve()

    # def button_approved(self):
    #     return super(PurchaseRequest, self).button_approved()

    # def button_rejected(self):
    #     return super(PurchaseRequest, self).button_rejected()

    # def button_done(self):
    #     return super(PurchaseRequest, self).button_done()

    # def button_close(self):
    #     self.line_ids._compute_line_state()
    #     return super(PurchaseRequest, self).button_close()
