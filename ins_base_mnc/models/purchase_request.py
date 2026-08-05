from base64 import urlsafe_b64encode as b64e
from datetime import date
from num2words import num2words
import zlib
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    amount_in_words = fields.Char('Amount To Words', compute='amount_to_text')
    amount_in_words_2 = fields.Char('Amount To Words 2', compute='amount_to_text_2')
    assignee_id = fields.Many2one('res.assignee.pr', 'Assignee')
    assignee2_id = fields.Many2one('res.assignee.pr', 'Assignee 2')
    attachment_form_ids = fields.Many2many('ir.attachment', string="Attachment")
    rr_numbers = fields.Char(string="RR Numbers", compute='_compute_rr_numbers')
    amount_total_pr = fields.Float('Amount Total PR',
                                   compute='_compute_amount_total_pr', store=True)
    origin = fields.Char(copy=False)
    pr_type_id = fields.Many2one('purchase.request.type', 'Purchase Request Type 1')
    pr_type_second_id = fields.Many2one('purchase.request.type.second', 'Purchase Request Type 2')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    partner_id = fields.Many2one("res.partner", string="Vendor")
    department_id = fields.Many2one('hr.department', string='Department (unused)')
    analytic_acc_id = fields.Many2one('account.analytic.account', string='Department')
    is_all_done = fields.Boolean('Is All Done', compute='_compute_is_all_done')

    def _show_selected_approvers(self):
        """ helper function to get valid data for showing selected_approver_ids """
        self.ensure_one()
        return self.is_rejected or self.env.user.has_group('ins_base_mnc.group_super_admin')

    @api.depends('line_ids')
    def _compute_is_all_done(self):
        """ compute function to check if all lines are in done state """
        for rec in self:
            rec.is_all_done = all(x == 'done' for x in rec.line_ids.mapped('request_state'))

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"date_start": date.today()})
        return super(PurchaseRequest, self).copy(default)

    @api.constrains('origin')
    def _check_origin(self):
        """ constrains function to check unique origin """
        for rec in self:
            if rec.origin:
                domain = [('id', '!=', rec.id), ('origin', '=ilike', rec.origin)]
                found = rec.search(domain)
                if found:
                    raise ValidationError('Source Document must be unique')

    @api.onchange('pr_type_id')
    def _check_pr_type_id(self):
        """ onchange function to check unique pr_type_id """
        for rec in self:
            if rec.pr_type_id:
                return {
                    'domain': {
                        'pr_type_second_id': [
                            ('type1_ids', '=', rec.pr_type_id.id),
                        ],
                    }
                }

    @api.depends('line_ids.original_price', 'line_ids.product_qty')
    def _compute_amount_total_pr(self):
        for rec in self:
            rec.amount_total_pr = sum(x.original_price * x.product_qty for x in rec.line_ids)

    @api.depends('line_ids.purchase_lines')
    def _compute_rr_numbers(self):
        for record in self:
            rr_number_list = []
            for line in record.line_ids:
                for po_line in line.purchase_lines:
                    rr_number_list.append(po_line.order_id.rr_numbers)

            rr_number_list = list(set(rr_number_list))
            rr_number_list.sort()
            rr_numbers = ', '.join(rr_number_list)
            record.rr_numbers = rr_numbers

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('line_ids', []):  # check if line_ids exist
            lines = vals.get('line_ids', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                line[2].update({'line_number': idx + 1})
                if line[2].get('date_required'):
                    period_line_id = self.env['purchase.request.period.line'].search([
                        ('date_start', '<=', line[2]['date_required']), ('date_end', '>=', line[2]['date_required']),
                        ('pr_period_id.company_id.id', '=', self.company_id.id), ('state', '=', 'close')
                    ])
                    if period_line_id:
                        raise ValidationError("Purchase Request Period is Closed.")

        res = super(PurchaseRequest, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        if vals.get('line_ids', []):  # check if line_ids exist
            lines = vals.get('line_ids', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                if line and line[2] and ((line[2].get('date_required') and line[0] == 0) or (line[2].get('date_required') and line[0] == 1)):
                    period_line_id = self.env['purchase.request.period.line'].search([
                        ('date_start', '<=', line[2]['date_required']), ('date_end', '>=', line[2]['date_required']),
                        ('pr_period_id.company_id.id', '=', self.company_id.id), ('state', '=', 'close')
                    ])
                    if period_line_id:
                        raise ValidationError("Purchase Request Period is Closed.")

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
                                line.crossovered_budget_line_id and line.estimated_cost > available_budget and \
                                not line.account_id.is_none_budget and not line.analytic_account_id.is_none_budget:
                            raise ValidationError(
                                "Remaining Budget for Line Number {} with Product {} is insufficient.".format(
                                    line.line_number, line.product_id.name))
                    else:
                        if not line.account_id.is_none_budget:
                            raise ValidationError("There is no Budget for Line Number {} with Product {}.".format(
                                line.line_number, line.product_id.name))

        # find line_ids, rewrite the line number
        for idx, line in enumerate(self.line_ids):
            line.line_number = idx + 1
        return res

    @api.depends('estimated_cost', 'currency_id')
    def amount_to_text(self):
        for rec in self:
            # lang = 'id' if self.currency_id.name == 'IDR' else 'en'
            lang = 'en'
            currency_in_words = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount = num2words(int(rec.estimated_cost), lang=lang)
            rec.amount_in_words = words_amount.title() + " " + currency_in_words

    @api.depends('estimated_cost', 'currency_id')
    def amount_to_text_2(self):
        for rec in self:
            lang_2 = 'id' if rec.currency_id.name == 'IDR' else 'en'
            currency_in_words_2 = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount_2 = num2words(int(rec.estimated_cost), lang=lang_2)
            rec.amount_in_words_2 = words_amount_2.title() + " " + currency_in_words_2

    def _obscure_param(self, data: bytes) -> bytes:
        return b64e(zlib.compress(data, 9))

    def button_to_approve(self):
        for line in self.line_ids:
            if line.crossovered_budget_line_id:
                available, rem_budget = line.crossovered_budget_line_id.check_budget_availability(
                    line.estimated_cost, pr_line=line)
                # available_budget = rem_budget - line.estimated_cost
                available_budget = line.remaining_budget_amount
                if line.crossovered_budget_line_id.general_budget_id.budget_type == 'abs' and \
                        line.crossovered_budget_line_id and not available and line.estimated_cost > available_budget and \
                        not line.account_id.is_none_budget or not line.analytic_account_id.is_none_budget:
                    raise ValidationError("Remaining Budget for Line Number {} with Product {} is insufficient.".format(
                        line.line_number, line.product_id.name))
            else:
                if not line.account_id.is_none_budget or not line.analytic_account_id.is_none_budget:
                    raise ValidationError("There is no Budget for Line Number {} with Product {}.".format(
                        line.line_number, line.product_id.name))

        return super(PurchaseRequest, self).button_to_approve()

    # Commented by Deden. Returned PR can be set to draft, even if a PO already exists.
    # def button_draft(self):
    #     """ inherit function to check if rfq_is_created """
    #     if self.rfq_is_created:
    #         raise ValidationError('Cannot set to draft. Purchase Order already exists')
    #     return super(PurchaseRequest, self).button_draft()

    # def button_to_approve(self):
    #     for pr_line in self.line_ids:
    #         for line in pr_line.project_ids:
    #             total = 0.0
    #             total += line.percentage
    #             subtask = line.subtask_id
    #             program = line.task_id.program_id
    #             budget = 0.0
    #             budget_id = line.program_id
    #             if total > 100:
    #                 raise ValidationError('Sum Percentage exceeds 100 percent')
    #             if subtask.budget_type == 'absolute':
    #                 for detail in budget_id.budget_ids:
    #                     budget = budget_id.episode_number * detail.rate
    #                     if budget < line.amount:
    #                         # return {'warning': {
    #                         #     'title': _("Information Error"),
    #                         #     'message': _("Budget exceeds the limit")
    #                         # }}
    #                         raise ValidationError('Budget exceeds the limit')
    #             if subtask.budget_type == 'advisory' and program.budget_type == 'absolute':
    #                 for detail in budget_id:
    #                     budget = detail.total_budget
    #                     if budget < line.amount:
    #                         # return {'warning': {
    #                         #     'title': _("Information Error"),
    #                         #     'message': _("Budget exceeds the limit")
    #                         # }}
    #                         raise ValidationError('Budget exceeds the limit')

    #     return super(PurchaseRequest, self).button_to_approve()

    def _get_attachment_report_id(self):
        """ function to get attachment report id in string """
        return 'ins_base_mnc.ins_base_mnc_report_purchase_request_portrait'

    def _get_attachment(self):
        """ override function to get attachment from attachment_form_ids """
        return self.attachment_form_ids

    def _get_approval_template(self):
        """ function to return mail template for approval """
        return 'ins_base_mnc.mnc_mail_purchase_request_approval'

    def _get_question_template(self):
        """ function to return mail template for question """
        return 'ins_base_mnc.mnc_mail_purchase_request_question'

    def _get_info_template(self):
        """ function to return mail template for info """
        return 'ins_base_mnc.mnc_mail_purchase_request_info'
