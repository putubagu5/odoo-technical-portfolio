from odoo import api, fields, models, _
from odoo.exceptions import MissingError, ValidationError, UserError, Warning


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    uniqkey_gen21 = fields.Char(string="Uniqkey Gen21")
    header_attribute4 = fields.Char(string="Episode No")
    is_post_line_gen21 = fields.Boolean(string="Is Post Gen21", related="request_id.is_post_gen21")

    def do_cancel_pr(self):
        for rec in self:
            if rec.is_post_line_gen21:
                if rec.is_post_line_gen21 and rec.cancelled is not True and rec.request_State != "cancel":
                    rec.write({"cancelled": True, "request_state": "cancel"})
            else:
                rec.write({"cancelled": True, "request_state": "cancel"})

    def button_canceled_gen21(self):
        """Actions to perform when cancelling a purchase request line."""
        pc_gen21_lines = self.env['program.costs.line.gen21'].search([('uniqkey', '=', self.uniqkey_gen21)])
        if pc_gen21_lines:
            pc_gen21_lines.write({'state': 'wait'})
            pc_gen21_lines.program_costs_id_gen21.write({'state': 'wait'})
        self.write({"cancelled": True, "request_state": "cancel"})
