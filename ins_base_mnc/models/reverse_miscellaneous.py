from odoo import _, models, fields
from odoo.exceptions import UserError


class MiscellaneousMiscellaneous(models.Model):
    _name = 'miscellaneous.miscellaneous'
    _inherit = ["miscellaneous.miscellaneous", "account.document.reversal"]

    reverse_date = fields.Date(
        string="Reversed Date"
    )
    reverse_user_by = fields.Many2one(
        comodel_name="res.users",
        string="Reversed By User",
    )
    reverse_reason = fields.Char(
        string="Reversed Reason",
    )

    def cancel_reversal_x(self):
        return self.reverse_document_wizard()

    def action_draft(self):
        """ Case cancel reversal, set to draft allowed only when no moves """
        for rec in self:
            if rec.is_cancel_reversal and rec.invoice_ids:
                raise UserError(_("Cannot set to draft!"))
        return super().action_draft()

    def cancel(self):
        if any(self.mapped("is_cancel_reversal")):
            raise UserError(_("Please use cancel_reversal()"))
        return super().cancel()

    def action_document_reversal(self, date=None, journal_id=None):
        """ Reverse all moves related to this payment + set state to cancel """
        # Check document readiness
        valid_state = (
                len(self.mapped("state")) == 1
                and list(set(self.mapped("state")))[0] == "posted"
        )
        if not valid_state:
            raise UserError(_("Only validated document can be cancelled (reversal)"))
        # Find moves to get reversed
        move_lines = self.mapped("payment_invoice_ids").filtered(
            lambda x: x.payment_id.journal_id == self.mapped("journal_id")[0]
        )
        print(move_lines, 'masuk_reversal')
        moves = move_lines.mapped("move_id")
        print(moves, 'masuk_reversal2')
        # Create reverse entries
        moves._cancel_reversal(journal_id)
        # Set state cancelled and unlink with account.move
        self.write({"state": "cancel"})
        return True

    def action_cancel(self):
        ''' draft -> cancelled '''
        if self.invoice_ids:
            for rec in self.invoice_ids:
                reverse_applied = self.env["account.move"].search([('reversed_entry_id', '=', rec.id)], limit=1)
                if rec.state == 'posted':
                    raise UserError(_(
                        "You have payment / Receipt, "
                        "Please cancel Applied Receipt firstly before cancel this Payment / Receipt."))
                if rec.state == 'cancel' or (rec.state == 'posted' and reverse_applied):
                    self.move_id.button_cancel_reversal()
                    # self.move_id.write({"cancel_reversal": True})
                    # reverse_applied.write({"cancel_reversal": True})
        elif not self.invoice_ids:
            self.move_id.button_cancel_reversal()

        # cancel applied to partner journal
        if self.applied_customer_move_id:
            for rec in self.applied_customer_move_id:
                reverse_applied = self.env["account.move"].search([('reversed_entry_id', '=', rec.id)], limit=1)
                if not reverse_applied:
                    rec.button_cancel_reversal()