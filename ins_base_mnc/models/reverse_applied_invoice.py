from odoo import _, models, fields, api
from odoo.exceptions import UserError


class MiscellaneousMiscellaneous(models.Model):
    _name = 'applied.invoices'
    _inherit = ["applied.invoices", "account.document.reversal"]

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
    cancel_method = fields.Selection(
        [
            ("normal", "Normal (remove journal entries)"),
            ("reversal", "Reversal (create reversed journal entries)"),
        ],
        string="Cancel Method",
        default="normal",
        required=True,
        related='journal_id.cancel_method'
    )

    @api.onchange('invoice_id')
    def _onchange_misc_partner_id(self):
        default_journal = self.env['account.journal'].search([('is_applied_invoice', '=', True)])
        if default_journal:
            self.journal_id = default_journal

    def cancel_reversal_x(self):
        return self.reverse_document_wizard()

    def action_draft(self):
        """ Case cancel reversal, set to draft allowed only when no moves """
        for rec in self:
            if rec.is_cancel_reversal:
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
        print(move_lines, 'masuk_applied_reversal')
        moves = move_lines.mapped("move_id")
        print(moves, 'masuk_applied_reversal2')
        # Create reverse entries
        moves._cancel_reversal(journal_id)
        # Set state cancelled and unlink with account.move
        self.write({"state": "cancel"})
        return True

    def action_unapplied_invoice(self):
        self.ensure_one()
        reverse_move = self.env["account.move"].search([('reversed_entry_id', '=', self.move_id.id)], limit=1)
        if reverse_move:
            raise UserError(_(
                    "The Applied invoice is Reversed, You Can't Reverse again"))
        if self.invoice_id:
            self.invoice_id.amount_residual_signed = self.invoice_id.amount_residual_signed + \
                                                     self.applied_amount + \
                                                     self.payment_difference
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            if self.invoice_id.amount_residual_signed == self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'not_paid'
            elif self.invoice_id.amount_residual_signed < self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'partial'
            # elif self.invoice_id.amount_residual_signed > self.invoice_id.amount_total_signed:
            #     raise UserError(_(
            #         "You can't unapplied amount greater than applied amount. please set amount correctly"))
        if self.misc_id:
            self.misc_id.applied_amount = self.misc_id.applied_amount - self.applied_amount
        if self.move_id and self.journal_id.cancel_method != 'normal':
            print("masuk reversal invoice?")
            self.move_id.button_cancel_reversal()
        if self.move_id and self.journal_id.cancel_method == 'normal':
            self.move_id.button_cancel()
            # self.move_id.button_cancel()
        self.transaction_type = 'unapply'
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.invoices.form")])
        action = {
            'name': _("Applied Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.view_applied_invoices_form"': '',
        }
        if self.id:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

    def action_unapplied_bill(self):
        self.ensure_one()
        if self.invoice_id:
            self.invoice_id.amount_residual_signed = self.invoice_id.amount_residual_signed + self.applied_amount
            self.invoice_id.amount_residual = self.invoice_id.amount_residual_signed
            if self.invoice_id.amount_residual_signed == self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'not_paid'
            elif self.invoice_id.amount_residual_signed < self.invoice_id.amount_total:
                self.invoice_id.payment_state = 'partial'
            # elif self.invoice_id.amount_residual_signed > self.invoice_id.amount_total_signed:
            #     raise UserError(_(
            #         "You can't unapplied amount greater than applied amount. please set amount correctly"))
        if self.misc_id:
            self.misc_id.applied_amount = self.misc_id.applied_amount - self.applied_amount
        if self.move_id:
            print("masuk reversal bill?")
            self.move_id.button_cancel_reversal()
            # self.move_id.button_cancel()
        self.transaction_type = 'unapply'
        view_id_form = self.env['ir.ui.view'].search([('name', '=', "applied.bill.form")])
        action = {
            'name': _("Applied Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'applied.invoices',
            'context': {'create': False},
            'views': [(view_id_form[0].id, 'form')],
            'view_id ref="ins_miscellaneous.view_applied_bill_form"': '',
        }
        if self.id:
            action.update({
                'view_mode': 'form',
                'res_id': self.id,
            })
        return action

