# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    currency_id = fields.Many2one('res.currency', 'Currency', readonly=False,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  required=True)
    po_numbers = fields.Char(string="PO Numbers", compute='_compute_po_numbers')
    # po_numbers_store = fields.Char(string="PO Numbers", compute='_compute_po_numbers_store', store=True)

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for record in self:
            if record.state in ['to_approve']:
                for line in record.line_ids.filtered(lambda li: li.request_state in ['draft', 'to_approve', 'returned']):
                    if line.crossovered_budget_line_id:
                        available, rem_budget = line.crossovered_budget_line_id.check_budget_availability(
                            line.estimated_cost, pr_line=line)

                        # available budget = remaining budget - estimated cost
                        # dikarenakan estimated cost sudah direserve karena status PR sudah bukan draft
                        available_budget = line.remaining_budget_amount
                        # available_budget = rem_budget - line.estimated_cost
                        if line.crossovered_budget_line_id.general_budget_id.budget_type == 'abs' and \
                                line.crossovered_budget_line_id and line.estimated_cost > available_budget:
                            raise ValidationError(
                                "Remaining Budget for Line Number {} with Product {} is insufficient.".format(
                                    line.line_number, line.product_id.name))
                    else:
                        raise ValidationError("There is no Budget for Line Number {} with Product {}.".format(
                            line.line_number, line.product_id.name))

        return res

    def button_to_approve(self):
        for line in self.line_ids:
            if line.crossovered_budget_line_id:
                available, rem_budget = line.crossovered_budget_line_id.check_budget_availability(
                    line.estimated_cost, pr_line=line)
                available_budget = rem_budget - line.estimated_cost
                if line.crossovered_budget_line_id.general_budget_id.budget_type == 'abs' and \
                        line.crossovered_budget_line_id and not available and line.estimated_cost > available_budget:
                    raise ValidationError("Remaining Budget for Line Number {} with Product {} is insufficient.".format(
                        line.line_number, line.product_id.name))
            else:
                raise ValidationError("There is no Budget for Line Number {} with Product {}.".format(
                    line.line_number, line.product_id.name))

        return super(PurchaseRequest, self).button_to_approve()

    @api.depends('line_ids.purchase_lines')
    def _compute_po_numbers(self):
        for record in self:
            po_number_list = []
            for line in record.line_ids:
                for po_line in line.purchase_lines:
                    po_number_list.append(po_line.order_id.name)

            po_number_list = list(set(po_number_list))
            po_number_list.sort()
            po_numbers = ', '.join(po_number_list)
            record.po_numbers = po_numbers

    # @api.depends('po_numbers')
    # def _compute_po_numbers_store(self):
    #     for record in self:
    #         record.po_numbers_store = record.po_numbers

    # @api.constrains('line_ids')
    # def _constraint_no_budget(self):
    #     for record in self:
    #         for line in record.line_ids:
    #             if line.crossovered_budget_line_id:
    #                 available, rem_budget = line.crossovered_budget_line_id.check_budget_availability(
    #                     line.estimated_cost, pr_line=line)
    #                 if line.crossovered_budget_line_id and not available:
    #                     raise ValidationError(
    #                         "Remaining Budget for Line Number {} is insufficient.".format(line.line_number))
    #             else:
    #                 raise ValidationError("There is no Budget for Line Number {}.".format(line.line_number))


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    crossovered_budget_line_id = fields.Many2one(
        'crossovered.budget.lines', 'Budget', compute='_compute_set_crossovered_budget', store=True)
    remaining_budget_amount = fields.Float('Remaining Budget',
                                           compute='_compute_set_crossovered_budget')
    account_id = fields.Many2one('account.account', 'Account')
    is_storable_service = fields.Boolean('Storable/Service Product',
                                         compute='_compute_is_storable_service',
                                         store=False)

    @api.depends('product_id')
    def _compute_is_storable_service(self):
        """ compute function to check is product_id is storable/service """
        for rec in self:
            rec.is_storable_service = rec.product_id.type in ('service', 'product')

    @api.onchange('product_id')
    def onchange_product_filter_analytic_account(self):
        for record in self:
            if record.product_id:
                account_id = False
                cost = 0

                # split and check by type
                # rules:
                # 1. Storable -> estimated_cost = standard_price,
                # account categ_id.property_stock_valuation_account_id
                # 2. Service -> estimated_cost = 1, account property_account_expense_id
                # 3. Consumable -> estimated_cost = standard_price,
                # account property_account_expense_id
                if record.product_id.type == 'product':  # storable
                    account_id = record.product_id.categ_id.property_stock_valuation_account_id
                    cost = record.product_id.standard_price
                elif record.product_id.type == 'consu':
                    cost = record.product_id.standard_price
                    account_id = record.product_id.property_account_expense_id
                elif record.product_id.type == 'service':
                    cost = 1
                    account_id = record.product_id.property_account_expense_id

                if not account_id:
                    raise ValidationError(_("{} does not have an Account.").format(record.product_id.name))

                record.account_id = account_id.id
                record.estimated_cost = cost

                budgetary_pos_ids = self.env['account.budget.post'].search([
                    ('account_ids', '=', account_id.id)
                ])

                analytic_account_ids = []
                if budgetary_pos_ids:
                    budget_ids = self.env['crossovered.budget'].search([
                        ('crossovered_budget_line.general_budget_id', 'in', budgetary_pos_ids.ids)
                    ])
                    for budget in budget_ids:
                        for budget_line in budget.crossovered_budget_line:
                            if budget_line.general_budget_id.id in budgetary_pos_ids.ids:
                                analytic_account_ids.append(budget_line.analytic_account_id.id)

                return {'domain': {'analytic_account_id': [('id', 'in', analytic_account_ids)]}}

    @api.onchange('account_id')
    def onchange_account_filter_analytic_account(self):
        for record in self:
            if record.account_id:
                budgetary_pos_ids = self.env['account.budget.post'].search([
                    ('account_ids', '=', record.account_id.id)
                ])

                analytic_account_ids = []
                if budgetary_pos_ids:
                    budget_ids = self.env['crossovered.budget'].search([
                        ('crossovered_budget_line.general_budget_id', 'in', budgetary_pos_ids.ids)
                    ])
                    for budget in budget_ids:
                        for budget_line in budget.crossovered_budget_line:
                            if budget_line.general_budget_id.id in budgetary_pos_ids.ids:
                                analytic_account_ids.append(budget_line.analytic_account_id.id)

                return {'domain': {'analytic_account_id': [('id', 'in', analytic_account_ids)]}}

    @api.onchange('account_id', 'analytic_account_id', 'estimated_cost','date_required')
    @api.depends('analytic_account_id')
    def _compute_set_crossovered_budget(self):
        for record in self:
            account_id = record.account_id
            # if record.product_id.type in ['consu', 'service']:
            #     account_id = record.product_id.property_account_expense_id.id if \
            #         record.product_id.property_account_expense_id else False
            # else:
            #     if record.product_id.categ_id.property_valuation == 'real_time':
            #         account_id = record.product_id.categ_id.property_stock_valuation_account_id.id if \
            #             record.product_id.categ_id.property_stock_valuation_account_id else False
            #     else:
            #         account_id = record.product_id.property_account_expense_id.id if \
            #             record.product_id.property_account_expense_id else False

            if record.analytic_account_id and account_id:
                crossovered_budget_line_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
                    account_id, record.analytic_account_id.id, record.date_required
                )
                if crossovered_budget_line_id:
                    record.crossovered_budget_line_id = crossovered_budget_line_id.id
                    available, rem_budget = crossovered_budget_line_id.check_budget_availability(
                        record.estimated_cost, record)
                    record.remaining_budget_amount = rem_budget
                else:
                    record.crossovered_budget_line_id = False
                    record.remaining_budget_amount = 0.0
            else:
                record.crossovered_budget_line_id = False
                record.remaining_budget_amount = 0.0

    # def create(self,vals):
    #     res = super(PurchaseRequestLine, self).create(vals)
    #     crossovered_budget_line_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
    #                 res.account_id, res.analytic_account_id.id, res.date_required
    #             )
    #     if crossovered_budget_line_id:
    #         if crossovered_budget_line_id.general_budget_id.budget_type == 'abs' and res.estimated_cost > res.remaining_budget_amount:
    #             raise ValidationError(_('Over Budget'))
    #     return res
    #
    # def write(self,vals):
    #     res = super(PurchaseRequestLine, self).write(vals)
    #     crossovered_budget_line_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
    #                 res.account_id, res.analytic_account_id.id, res.date_required
    #             )
    #     if crossovered_budget_line_id:
    #         if crossovered_budget_line_id.general_budget_id.budget_type == 'abs' and res.estimated_cost > res.remaining_budget_amount:
    #             raise ValidationError(_('Over Budget'))
    #     return res
