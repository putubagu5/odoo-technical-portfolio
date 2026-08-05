# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CrossoveredBudgetPriod(models.Model):
    _name = 'crossovered.budget.period'
    _description = "Budget Period"

    name = fields.Char(string="Year", required=True, copy=False)
    date_start = fields.Date(string="Start Date", required=True, copy=False)
    date_end = fields.Date(string="End Date", required=True, copy=False)
    state = fields.Selection([
        ('open', "Open"), ('close', "Close")],
        string="Status", default='open')
    company_id = fields.Many2one(
        'res.company', string='Company', store=True,
        default=lambda self: self.env.company)

    def set_to_open(self):
        self.ensure_one()
        self.state = 'open'

    def set_to_close(self):
        self.ensure_one()
        self.state = 'close'
        budget_ids = self.env['crossovered.budget'].search([('period_id','=',self.id)])
        for budget_id in budget_ids:
            budget_id.action_budget_done()

    @api.constrains('name')
    def _check_name(self):
        """ constrains function to check name duplicate """
        domain = [
            ('name', '=ilike', self.name),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Name already exists!')
