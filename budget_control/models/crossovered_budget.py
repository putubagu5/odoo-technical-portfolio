# -*- coding: utf-8 -*-

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class CrossOverredBudget(models.Model):
    _inherit = 'crossovered.budget'

    crossovered_budget_line_add = fields.One2many('crossovered.budget.lines', 'crossovered_budget_id', string="Add Line")
    period_id = fields.Many2one('crossovered.budget.period', string="Period")
    year = fields.Char(string="Year")
    budget_allocation_ids = fields.One2many('budget.allocation', 'crossovered_budget_id', string="Budget Allocations")
    show_done_btn = fields.Boolean(string="Show Done button?", compute="_compute_show_button")
    reject_user_id = fields.Many2one('res.users', string="User")
    reject_date_reject = fields.Date(string="Date")
    reject_reason = fields.Text(string="Reason")

    @api.constrains('name','period_id')
    def _check_name(self):
        """ constrains function to check name duplicate """
        domain = [
            ('id', '!=', self.id),
            ('period_id', '=', self.period_id.id),
            ('name', '=ilike', self.name),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Name and period already exists!')

    @api.constrains('crossovered_budget_line_add')
    def _constraint_check_crossovered_budget_line_add(self):
        for record in self:
            for line in record.crossovered_budget_line_add:
                if line.amount_total_budget <= 0.0:
                    raise ValidationError(_("Budget Line '{}' value cannot be zero.".format(
                        line.general_budget_id.name
                    )))

    @api.depends('date_to')
    def _compute_show_button(self):
        for record in self:
            if record.date_to and date.today() >= record.date_to:
                record.show_done_btn = True
            else:
                record.show_done_btn = False

    @api.onchange('period_id')
    def _onchange_period_set_date_and_year(self):
        for record in self:
            if record.period_id:
                record.year = record.period_id.name
                record.date_from = record.period_id.date_start
                record.date_to = record.period_id.date_end
            else:
                record.year = False
                record.date_from = False
                record.date_to = False

    @api.depends('crossovered_budget_line')
    def _compute_amount_total(self):
        for record in self:
            record.amount_practical_total = sum(record.crossovered_budget_line.mapped(lambda cbl: cbl.practical_amount))
            record.amount_planned_total = 0.0

    def search_crossovered_budget_lines(self):
        self.ensure_one()
        return {
            "name": _("Search Budget Line"),
            "view_mode": "form",
            "res_model": "search.crossovered.budget.lines",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {'default_crossovered_budget_id': self.id},
        }

    def action_budget_draft(self):
        if self.reject_user_id and self.reject_date_reject and self.reject_reason:
            msg = """
                <ul>
                    <li>User: {}</li>
                    <li>Date: {}</li>
                    <li>Reason: {}</li>
                </ul>
            """.format(self.reject_user_id.name, self.reject_date_reject.strftime("%d/%m/%Y"), self.reject_reason)
            self.message_post(body=msg, subject="Budget Cancelled")

        self.write({
            'state': 'draft',
            'reject_user_id': False,
            'reject_date_reject': False,
            'reject_reason': False,
        })

    def action_budget_cancel(self):
        return {
            "name": _("Cancel Budget"),
            "view_mode": "form",
            "res_model": "reject.budget.reason",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {'default_budget_id': self.id},
        }


class CrossOverredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    amount_total_budget = fields.Float(string="Total", compute='_compute_amount_total')
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
    emcumbren_month1 = fields.Float(string="Jan", compute='_compute_emcumbren_month1')
    emcumbren_month2 = fields.Float(string="Feb", compute='_compute_emcumbren_month2')
    emcumbren_month3 = fields.Float(string="Mar", compute='_compute_emcumbren_month3')
    emcumbren_month4 = fields.Float(string="Apr", compute='_compute_emcumbren_month4')
    emcumbren_month5 = fields.Float(string="May", compute='_compute_emcumbren_month5')
    emcumbren_month6 = fields.Float(string="Jun", compute='_compute_emcumbren_month6')
    emcumbren_month7 = fields.Float(string="Jul", compute='_compute_emcumbren_month7')
    emcumbren_month8 = fields.Float(string="Aug", compute='_compute_emcumbren_month8')
    emcumbren_month9 = fields.Float(string="Sep", compute='_compute_emcumbren_month9')
    emcumbren_month10 = fields.Float(string="Oct", compute='_compute_emcumbren_month10')
    emcumbren_month11 = fields.Float(string="Nov", compute='_compute_emcumbren_month11')
    emcumbren_month12 = fields.Float(string="Dec", compute='_compute_emcumbren_month12')
    actual_month1 = fields.Float(string="Jan", compute='_compute_actual_month1')
    actual_month2 = fields.Float(string="Feb", compute='_compute_actual_month2')
    actual_month3 = fields.Float(string="Mar", compute='_compute_actual_month3')
    actual_month4 = fields.Float(string="Apr", compute='_compute_actual_month4')
    actual_month5 = fields.Float(string="May", compute='_compute_actual_month5')
    actual_month6 = fields.Float(string="Jun", compute='_compute_actual_month6')
    actual_month7 = fields.Float(string="Jul", compute='_compute_actual_month7')
    actual_month8 = fields.Float(string="Aug", compute='_compute_actual_month8')
    actual_month9 = fields.Float(string="Sep", compute='_compute_actual_month9')
    actual_month10 = fields.Float(string="Oct", compute='_compute_actual_month10')
    actual_month11 = fields.Float(string="Nov", compute='_compute_actual_month11')
    actual_month12 = fields.Float(string="Dec", compute='_compute_actual_month12')
    purchase_request_ids = fields.One2many('purchase.request.line', 'crossovered_budget_line_id',
                                           string="Purchase Request Lines")
    pr_reserve_amount = fields.Float(string="PR Reserve", compute='_compute_total_reserve_remaining')
    po_reserve_amount = fields.Float(string="PO Reserve", compute='_compute_total_reserve_remaining')
    remaining_amount = fields.Float(string="Budget Remaining", compute='_compute_total_reserve_remaining')
    operating_unit_id = fields.Many2one(
        'operating.unit', string="Wilayah", domain="[('user_ids', '=', uid)]"
    )
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', required=True)
    budget_type = fields.Selection([
        ('abs', "Absolute"), ('adv', "Advisory")
    ], string="Budget Type", related='general_budget_id.budget_type')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True)

    def _compute_emcumbren_month1(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 1 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month1 = emcumbren_month

    def _compute_emcumbren_month2(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 2 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month2 = emcumbren_month

    def _compute_emcumbren_month3(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 3 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month3 = emcumbren_month

    def _compute_emcumbren_month4(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 4 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month4 = emcumbren_month

    def _compute_emcumbren_month5(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 5 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month5 = emcumbren_month

    def _compute_emcumbren_month6(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 6 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month6 = emcumbren_month

    def _compute_emcumbren_month7(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 7 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month7 = emcumbren_month

    def _compute_emcumbren_month8(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 8 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month8 = emcumbren_month

    def _compute_emcumbren_month9(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 9 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month9 = emcumbren_month

    def _compute_emcumbren_month10(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 10 and r.state == 'purchase')
            emcumbren_month = 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month10 = emcumbren_month

    def _compute_emcumbren_month11(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 11 and r.state == 'purchase')
            emcumbren_month = 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month11 = emcumbren_month

    def _compute_emcumbren_month12(self):
        for record in self:
            po_lines = record.purchase_request_ids.purchase_lines.filtered(lambda r: r.date_order.month == 12 and r.state == 'purchase')
            emcumbren_month= 0
            for po_line in po_lines:
                quantity_balance = po_line.product_qty - po_line.qty_received
                price_subtotal = quantity_balance * po_line.price_unit
                emcumbren_month += price_subtotal
            record.emcumbren_month12 = emcumbren_month

    def _compute_actual_month1(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==1)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month1 = practical_amount
    
    def _compute_actual_month2(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==2)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month2 = practical_amount
            
    def _compute_actual_month3(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==3)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month3 = practical_amount
    
    def _compute_actual_month4(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==4)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month4 = practical_amount
    
    def _compute_actual_month5(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==5)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month5 = practical_amount
    
    def _compute_actual_month6(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==6)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month6 = practical_amount
            
    def _compute_actual_month7(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==7)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month7 = practical_amount
    
    def _compute_actual_month8(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==8)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month8 = practical_amount
    
    def _compute_actual_month9(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==9)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month9 = practical_amount
    
    def _compute_actual_month10(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==10)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month10 = practical_amount
            
    def _compute_actual_month11(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==11)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month11 = practical_amount
    
    def _compute_actual_month12(self):
        for record in self:
            aml_obj = self.env['account.move.line'].search([
                ('account_id', 'in', record.general_budget_id.account_ids.ids),
                ('move_id.state', '=', 'posted')])
            aml_obj = aml_obj.filtered(lambda r:r.date.month==12)
            practical_amount = sum(aml_obj.mapped('credit')) - sum(aml_obj.mapped('debit'))
            practical_amount = abs(practical_amount)
            record.actual_month12 = practical_amount

    def _compute_total_reserve_remaining(self):
        for record in self:
            pr_lines = record.purchase_request_ids.filtered(
                lambda pr: pr.request_state in ['to_approve', 'approved', 'done'])
            pr_reserved_amount = 0.0
            for prs_line in pr_lines:
                if not prs_line.purchase_lines.ids:
                    pr_reserved_amount += prs_line.estimated_cost
                else:
                    for po_line in prs_line.purchase_lines:
                        if po_line.order_id.state in ['draft', 'cancel']:
                            estimated_amount = po_line.product_qty * po_line.price_unit
                            pr_reserved_amount += estimated_amount

            po_lines = record.purchase_request_ids.filtered(
                lambda pr: pr.request_state in ['approved', 'done']
            )
            po_reserved_amount = 0.0
            for pr_line in po_lines:
                for po_line in pr_line.purchase_lines:
                    price_subtotal = 0.0
                    if po_line.order_id.state == 'to approve':
                        price_subtotal = po_line.product_qty * po_line.price_unit
                    elif po_line.order_id.state == 'purchase':
                        quantity_balance = po_line.product_qty - po_line.qty_received
                        price_subtotal = quantity_balance * po_line.price_unit

                    po_reserved_amount += price_subtotal

            residual_amount = record.planned_amount - pr_reserved_amount - po_reserved_amount + record.practical_amount
            record.pr_reserve_amount = pr_reserved_amount
            record.po_reserve_amount = po_reserved_amount
            record.remaining_amount = residual_amount

    def get_av_budget_by_month(self, month):
        self.ensure_one()
        month = int(month) - 1
        budget_by_month = [
            self.month1, self.month2, self.month3, self.month4, self.month5, self.month6,
            self.month7, self.month8, self.month9, self.month10, self.month11, self.month12,
        ]
        return budget_by_month[month]

    def get_res_budget_by_month(self, month, pr_line=False):
        self.ensure_one()
        budget = self.get_av_budget_by_month(month)
        if pr_line:
            pr_reserved_amount = sum(self.purchase_request_ids.filtered(
                lambda pr: pr.request_id.state in ['to_approve', 'approved',
                                                   'rejected'] and pr.date_required.month == int(
                    month) and pr.id != pr_line.id and not pr.purchase_lines
            ).mapped(lambda prl: prl.estimated_cost))
        else:
            pr_reserved_amount = sum(self.purchase_request_ids.filtered(
                lambda pr: pr.request_id.state in ['to_approve', 'approved',
                                                   'rejected'] and pr.date_required.month == int(
                    month) and not pr.purchase_lines
            ).mapped(lambda prl: prl.estimated_cost))
        pr_po_lines = self.purchase_request_ids.filtered(
            lambda pr: pr.request_id.state == 'approved' and pr.date_required.month == int(month) and pr.purchase_lines
        )
        po_reserved_amount = 0.0
        for pr_line in pr_po_lines:
            for po_line in pr_line.purchase_lines:
                if po_line.order_id.state == 'purchase' and not po_line.order_id.invoice_ids:
                    po_reserved_amount += po_line.price_subtotal

        pr_po_reserved = pr_reserved_amount + po_reserved_amount
        residual_amount = budget - pr_po_reserved
        return residual_amount

    def get_prev_residual_budget(self, current_month):
        prev_residual_amount = 0.0
        for month in range(1, current_month + 1):
            if current_month == month:
                continue

            prev_residual_amount += self.get_res_budget_by_month(month)

        return prev_residual_amount

    def get_res_budget_all_month(self, pr_line):
        # Get Purchase Request reserved amount (PR with state to_approve, approved, rejected) with no purchase_lines
        if pr_line:
            pr_reserved_amount = sum(self.purchase_request_ids.filtered(
                lambda pr: pr.request_id.state in ['to_approve', 'approved', 'rejected'] and pr.id != pr_line.id and not pr.purchase_lines
            ).mapped(lambda prl: prl.estimated_cost))
        else:
            pr_reserved_amount = sum(self.purchase_request_ids.filtered(
                lambda pr: pr.request_id.state in ['to_approve', 'approved', 'rejected'] and not pr.purchase_lines
            ).mapped(lambda prl: prl.estimated_cost))

        # Get Purchase Request that has Purchase Order with state purchase, but no Invoice
        pr_po_lines = self.purchase_request_ids.filtered(
            lambda pr: pr.request_id.state == 'approved' and pr.purchase_lines
        )
        po_reserved_amount = 0.0
        for prpo_line in pr_po_lines:
            for po_line in prpo_line.purchase_lines:
                if po_line.order_id.state == 'purchase' and not po_line.order_id.invoice_ids:
                    po_reserved_amount += po_line.price_subtotal

        # Remaining amount (practical_amount have minus amount, so change minus (-) to plus (+))
        residual_amount = self.planned_amount - pr_reserved_amount - po_reserved_amount + self.practical_amount
        return residual_amount

    def check_budget_availability(self, amount, pr_line=False):
        self.ensure_one()
        # available_budget = self.get_res_budget_all_month(pr_line)
        available_budget = self.remaining_amount
        # Check budgetary position type:
        # if abs (absolute), give checking, otherwise proceed
        if available_budget < amount and self.general_budget_id.budget_type == 'abs':
            return False, available_budget

        return True, available_budget

    def get_cb_line_by_account(self, account, analytic_account, date):
        # Find self that general_budget_id.account_ids, analytic_account_id, crossovered_budget_id.state match
        # with args
        line_id = self.search([
            ('general_budget_id.account_ids', '=', int(account)),
            ('analytic_account_id', '=', int(analytic_account)),
            ('crossovered_budget_id.state', '=', 'validate'),
            ('date_from', '<=', date),
            ('date_to', '>=', date)
        ], limit=1)

        if line_id:
            return line_id

        return False

    def action_open_po_res_entries(self):
        self.ensure_one()
        po_lines = self.purchase_request_ids.filtered(
            lambda pr: pr.purchase_lines
        )
        po_ids = []
        for pr_line in po_lines:
            for po_line in pr_line.purchase_lines:
                if po_line.order_id.state in ['to approve', 'purchase']:
                    rem_qty = po_line.product_qty - po_line.qty_received
                    if rem_qty > 0:
                        po_ids.append(po_line.order_id.id)

        po_ids = list(set(po_ids))
        return {
            "name": _("Purchase Order"),
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
            "domain": [('id', 'in', po_ids)],
        }

    def action_open_pr_res_entries(self):
        self.ensure_one()
        pr_lines = self.purchase_request_ids.filtered(
            lambda pr: pr.request_id.state in ['to_approve', 'approved', 'rejected'])
        pr_ids = []
        for prs_line in pr_lines:
            if not prs_line.purchase_lines:
                pr_ids.append(prs_line.request_id.id)
            else:
                for prc_line in prs_line.purchase_lines:
                    if prc_line.order_id.state == 'draft':
                        pr_ids.append(prs_line.request_id.id)

        return {
            "name": _("Purchase Request"),
            "view_mode": "tree,form",
            "res_model": "purchase.request",
            "type": "ir.actions.act_window",
            "domain": [('id', 'in', pr_ids)],
        }

    @api.onchange(
        'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
        'month7', 'month8', 'month9', 'month10', 'month11', 'month12',
    )
    @api.depends(
        'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
        'month7', 'month8', 'month9', 'month10', 'month11', 'month12',
    )
    def _compute_amount_total(self):
        for record in self:
            record.amount_total_budget = record.month1 + record.month2 + record.month3 + record.month4 + \
                                            record.month5 + record.month6 + record.month7 + record.month8 + \
                                            record.month9 + record.month10 + record.month11 + record.month12

    @api.onchange(
        'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
        'month7', 'month8', 'month9', 'month10', 'month11', 'month12',
    )
    def _onchange_months_set_planned_amount(self):
        for record in self:
            record.planned_amount = record.month1 + record.month2 + record.month3 + record.month4 + \
                                         record.month5 + record.month6 + record.month7 + record.month8 + \
                                         record.month9 + record.month10 + record.month11 + record.month12
