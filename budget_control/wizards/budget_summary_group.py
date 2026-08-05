# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class BudgetSummaryGroup(models.TransientModel):
    _name = 'budget.summary.group'

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    planned_amount = fields.Monetary('Planned Amount')
    practical_amount = fields.Monetary(string='Practical Amount')
    theoritical_amount = fields.Monetary(string='Theoretical Amount')
    company_id = fields.Many2one('res.company', string='Company')
    analytic_group_id = fields.Many2one('account.analytic.group', 'Analytic Group')

    amount_total_budget = fields.Float(string="Total")
    month1 = fields.Float(string="Jan")
    month2 = fields.Float(string="Feb")
    month3 = fields.Float(string="Mar")
    month4 = fields.Float(string="Apr")
    month5 = fields.Float(string="May")
    month6 = fields.Float(string="Jun")
    month7 = fields.Float(string="Jul")
    month8 = fields.Float(string="Aug")
    month9 = fields.Float(string="Sep")
    month10 = fields.Float(string="Oct")
    month11 = fields.Float(string="Nov")
    month12 = fields.Float(string="Dec")
    pr_reserve_amount = fields.Float(string="PR Reserve")
    po_reserve_amount = fields.Float(string="PO Reserve")
    remaining_amount = fields.Float(string="Budget Remaining")
