from odoo import api, fields, models, _
from odoo.exceptions import MissingError, ValidationError, UserError, Warning

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("returned", "Returned"),
    ("done", "Done"),
    ("closed", "Closed"),
    ("cancel", "Cancelled"),
]


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    note_reason = fields.Text(string="Reason")
    is_post_gen21 = fields.Boolean(string="Is Post Gen21", default=False)
    state = fields.Selection(selection=_STATES, string="Status", index=True, tracking=True, required=True, copy=False, default="draft")
    po_numbers_gen21 = fields.Char(string="PO Numbers Gen21")

    def button_canceled(self):
        check_po = self.env['purchase.order.line'].search([('request_id', '=', self.id)])
        if check_po:
            if len(check_po) > 0:
                for po in check_po:
                    if po.state != "cancel":
                        raise Warning(_("Failed cancel , please cancel po !!!")) 
            else:
                if check_po.state != "cancel":
                    raise Warning(_("Failed cancel , please cancel po !!!"))
        self.mapped("line_ids").do_cancel_pr()
        if self.is_post_gen21:
            keys = self.line_ids.mapped('uniqkey_gen21')
            pc_gen21_lines = self.env['program.costs.line.gen21'].search([('uniqkey', 'in', keys)])
            if pc_gen21_lines:
                for program_cost in pc_gen21_lines:
                    program_cost.program_costs_id_gen21.write({'state': 'wait'})
                    program_cost.write({'state': 'wait'})
        self.write({"state": "cancel"})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        if self.state == 'cancel':
            for line in self.line_ids.filtered(lambda ln: ln.request_state in ['cancel']):
                line.write({"request_state": "draft"})
        else:
            for line in self.line_ids.filtered(lambda ln: ln.request_state in ['draft', 'to_approve', 'approved', 'rejected', 'returned']):
                line.request_state = 'draft'
        return self.write({"state": "draft"})
