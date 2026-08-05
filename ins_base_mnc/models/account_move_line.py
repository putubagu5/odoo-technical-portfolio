from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError, Warning


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_default_analytic(self):
        """ function to get default analytic """
        # find analytic with is_default true and in the same company
        domain = [('is_default', '=', True), ('company_id', '=', self.company_id.id)]
        analytic = self.env['account.analytic.account'].search(domain, limit=1)
        return analytic

    purchase_line_number = fields.Integer('PO Line No')
    picking_line_number = fields.Integer('Receipt Line No')
    tax_invoice_id = fields.Many2one(related='move_id.tax_invoice_id')
    rate = fields.Float(related='move_id.rate')
    purchase_info_id = fields.Many2one(
        'purchase.order', 'PO info (for printout)',
        compute='_compute_po_id')
    stock_move_gr_match_ids = fields.Many2many('stock.move', 'stock_move_gr_match_rel', string="Stock Moves GR Match")
    po_line_gr_match_ids = fields.Many2many('purchase.order.line', 'po_line_gr_match_rel', string="PO Lines GR Match")
    # ref_invoice = fields.Text('Invoice', related='move_id.ref_invoice')
    ref_receipt = fields.Text('Receipt', related='move_id.ref_receipt')
    ref_misc_receipt = fields.Text('Misc Receipt', related='move_id.ref_misc_receipt')
    # ref_bill = fields.Text('Vendor Bill', related='move_id.ref_bill')
    ref_payment = fields.Text('Payment', related='move_id.ref_payment')
    ref_misc_payment = fields.Text('Misc Payment', related='move_id.ref_misc_payment')
    analytic_account_id = fields.Many2one(default=lambda self: self._get_default_analytic())
    account_move_prepayment_match_id = fields.Many2one('account.move', copy=False,
                                                       string='Matching Prepayment with settlement',
                                                       domain="[('bill_type', '=', 'prepayment')]")
    account_move_line_prepayment_match_id = fields.Many2one('account.move.line', copy=False,
                                                            string='Matching line Prepayment with settlement')
    amount_line_prepayment_applied_for_settlement = fields.Float(default=0, string="Amount of Prepayment Applied for Settlement")
    budget_remaining_corporate = fields.Float(default=0, string="Budget Remaining", readonly=True)

    _sql_constraints = [('match_prepayment_unique','UNIQUE(account_move_prepayment_match_id,move_id,account_move_line_prepayment_match_id)', "Prepayment is already used in this bill, please select another prepayment"),]

    def _compute_po_id(self):
        for record in self:
            purchase_id = self.env['purchase.order'].search([
                ('name', '=', self.move_id.invoice_origin)
            ])
            record.purchase_info_id = purchase_id.id if purchase_id else False

    @api.onchange('analytic_account_id', 'account_id', 'move_id')
    def _budget_remaining_corporate(self):
        for record in self:
            if record.analytic_account_id and record.account_id and record.move_id.date:
                crossovered_budget_line_id = self.env['crossovered.budget.lines'].get_cb_line_by_account(
                    record.account_id, record.analytic_account_id.id, record.move_id.date
                )
                if crossovered_budget_line_id:
                    available, rem_budget = crossovered_budget_line_id.check_budget_availability(
                        0, record)
                    record.budget_remaining_corporate = rem_budget
                else:
                    record.budget_remaining_corporate = 0.0
            else:
                record.budget_remaining_corporate = 0.0

    @api.constrains('account_move_prepayment_match_id')
    def _check_prepayment_match_id(self):
        """ constrains function to check prepayment_match_id duplicate """
        for rec in self:
            domain = [
                ('account_move_prepayment_match_id', '!=', False),
                ('account_move_prepayment_match_id', '=', rec.account_move_prepayment_match_id.id),
                ('id', '!=', rec.id),
                ('move_id', '=', rec.move_id.id),
            ]
            line = rec.search(domain)
            if line:
                raise Warning('Matching Prepayment already exists!')

    @api.onchange('price_unit')
    def _onchange_price_unit_prepayment(self):
        ''' check onchange based on price unit prepayment.
        If the edited line is a amount prepayement, can't edited price unit greater than amount remaining prepayment.
        '''
        for line in self:
            if line.account_move_line_prepayment_match_id:
                if (line.account_move_line_prepayment_match_id.price_unit - line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement) < 0:
                    raise UserError(
                        _('Cannot applied prepaymet to settlement greater than'), line.account_move_line_prepayment_match_id.price_unit - line.account_move_line_prepayment_match_id.amount_line_prepayment_applied_for_settlement)
