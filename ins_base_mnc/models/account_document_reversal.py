from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReverseAccountDocument(models.TransientModel):
    """
    Document reversal wizard, it cancel by reverse document journal entries
    """

    _inherit = "reverse.account.document"
    _description = "Account Document Reversal"

    def action_cancel(self):
        model = self._context.get("active_model")
        active_ids = self._context.get("active_ids")
        print("masuk cancel", model, active_ids)
        if model == 'account.move':
            documents = self.env[model].browse(active_ids)
            documents.action_document_reversal(self.date, self.journal_id.id)
            documents.reverse_reason = self.reverse_reason
            documents.reverse_user_by = self.reverse_user_by
            documents.reverse_date = self.date
        elif model == 'account.payment':
            documents = self.env[model].browse(active_ids)
            moves = documents.move_id.id
            reverse = self.env["account.move"].browse([moves])
            reverse.mapped("line_ids").filtered(
                lambda x: x.account_id.reconcile
            ).remove_move_reconcile()
            documents.reverse_reason = self.reverse_reason
            documents.reverse_user_by = self.reverse_user_by
            documents.reverse_date = self.date
            # documents.is_matched: False
            # documents.cancel_reversal: True
            reverse.action_document_reversal(self.date, self.journal_id.id)
            print(documents, 'account_document_reversal ins_base_mnc')
        elif model == 'miscellaneous.miscellaneous':
            print("masuk misc")
            documents = self.env[model].browse(active_ids)
            if documents.move_id.id and not documents.applied_customer_move_id.id:
                moves = documents.move_id.id
                print("masuk moves", moves)
                reverse = self.env["account.move"].browse([moves])
                misc = self.env["account.move"].search([('reversed_entry_id', '=', reverse.id)], limit=1)
                print("masuk reverse", reverse, misc)
                reverse.mapped("line_ids").filtered(
                    lambda x: x.account_id.reconcile
                ).remove_move_reconcile()
                reverse.action_document_reversal(self.date, self.journal_id.id)
                documents.reverse_reason = self.reverse_reason
                documents.reverse_user_by = self.reverse_user_by
                documents.reverse_date = self.date
                documents.cancel_reversal = True
            elif documents.move_id.id and documents.applied_customer_move_id.id:
                moves = documents.move_id.id
                applied = documents.applied_customer_move_id.id
                print("masuk moves", moves)
                reverse = self.env["account.move"].browse([moves])
                revese_move = self.env["account.move"].search([('reversed_entry_id', '=', reverse.id)], limit=1)
                reverse_applied = self.env["account.move"].browse([applied])
                print("masuk reverse misc ada applied yang sudah reverse.", reverse, reverse_applied)
                if not revese_move:
                    reverse_applied.action_document_reversal(self.date, self.journal_id.id)
                    reverse.action_document_reversal(self.date, self.journal_id.id)
                    documents.reverse_reason = self.reverse_reason
                    documents.reverse_user_by = self.reverse_user_by
                    documents.reverse_date = self.date
                    documents.cancel_reversal = True

        elif model == 'applied.invoices':
            print("masuk applied invoice")
            documents = self.env[model].browse(active_ids)
            moves = documents.move_id.id
            print("masuk move applied invoice", moves)
            reverse = self.env["account.move"].browse([moves])
            print("masuk reverse applied invoice", reverse)
            if documents.misc_id.misc_type == 'payment':
                reverse.mapped("line_ids").filtered(
                    lambda x: x.account_id.reconcile
                ).remove_move_reconcile()
                documents.action_unapplied_bill()
            elif documents.misc_id.misc_type == 'receive':
                reverse.mapped("line_ids").filtered(
                    lambda x: x.account_id.reconcile
                ).remove_move_reconcile()
                documents.action_unapplied_invoice()
            reverse.action_document_reversal(self.date, self.journal_id.id)
            documents.reverse_reason = self.reverse_reason
            documents.reverse_user_by = self.reverse_user_by
            documents.reverse_date = self.date

        elif model == 'applied.prepayment.to.bill':
            print("masuk applied prepayment to bill")
            documents = self.env[model].browse(active_ids)
            moves = documents.move_id.id
            print("masuk move applied prepayment to bill", moves)
            reverse = self.env["account.move"].browse([moves])
            print("masuk reverse applied prepayment to bill", reverse)
            if documents.prepayment_id:
                reverse.mapped("line_ids").filtered(
                    lambda x: x.account_id.reconcile
                ).remove_move_reconcile()
            reverse.action_document_reversal(self.date, self.journal_id.id)
            documents.reverse_reason = self.reverse_reason
            documents.reverse_user_by = self.reverse_user_by
            documents.reverse_date = self.date

        return {"type": "ir.actions.act_window_close"}


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _cancel_reversal(self, journal_id):
        self.mapped("line_ids").filtered(
            lambda x: x.account_id.reconcile
        ).remove_move_reconcile()
        Reversal = self.env["account.move.reversal"]
        res = Reversal.with_context(
            active_ids=self.ids, active_model="account.move"
        ).default_get([])
        res.update(
            {"journal_id": journal_id, "refund_method": "cancel", "move_type": "entry"}
        )
        reversal = Reversal.create(res)
        print(res, reversal,'masuk ke sini misc ?')
        reversal.with_context(cancel_reversal=True).reverse_moves()
        payment = self.env["account.move"].browse(self.ids)
        misc = self.env["miscellaneous.miscellaneous"].search([('move_id', 'in', self.ids)], limit=1)
        misc_applied = self.env["miscellaneous.miscellaneous"].search([('applied_customer_move_id', 'in', self.ids)], limit=1)
        invoice_applied = self.env["applied.invoices"].search([('move_id', 'in', self.ids)], limit=1)
        print(misc, 'dapat nilai misc ?')
        if payment.payment_id:
            default_values_list = [{
                'ref': payment.name,
                'date': reversal.date,
                'invoice_date': payment.invoice_date or False,
                'journal_id': journal_id,
                'invoice_payment_term_id': payment.invoice_payment_term_id.id,
                'invoice_user_id': payment.invoice_user_id.id,
                'auto_post': False

            }]
            self._reverse_moves(default_values_list, cancel=True)
        if misc:
            default_values_list = [{
                'ref': misc_applied.move_id.name,
                'date': reversal.date,
                'invoice_date': misc_applied.move_id.invoice_date or False,
                'journal_id': journal_id,
                'invoice_payment_term_id': misc_applied.move_id.invoice_payment_term_id.id,
                'invoice_user_id': misc_applied.move_id.invoice_user_id.id,
                'auto_post': False

            }]
            self._reverse_moves(default_values_list, cancel=True)
        if misc_applied:
            default_values_list = [{
                'ref': misc.move_id.name,
                'date': reversal.date,
                'invoice_date': misc.move_id.invoice_date or False,
                'journal_id': journal_id,
                'invoice_payment_term_id': misc.move_id.invoice_payment_term_id.id,
                'invoice_user_id': misc.move_id.invoice_user_id.id,
                'auto_post': False

            }]
            self._reverse_moves(default_values_list, cancel=True)
        if invoice_applied:
            default_values_list = [{
                'ref': invoice_applied.move_id.name,
                'date': reversal.date,
                'invoice_date': invoice_applied.move_id.invoice_date or False,
                'journal_id': journal_id,
                'invoice_payment_term_id': invoice_applied.move_id.invoice_payment_term_id.id,
                'invoice_user_id': invoice_applied.move_id.invoice_user_id.id,
                'auto_post': False

            }]
            self._reverse_moves(default_values_list, cancel=True)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        """ Set flag on the moves and the reversal moves being reversed """
        print(default_values_list, 'disini default ?')
        if self._context.get("cancel_reversal"):
            self.write({"cancel_reversal": True})
        reverse_moves = super()._reverse_moves(default_values_list, cancel)
        if self._context.get("cancel_reversal"):
            reverse_moves.write({"cancel_reversal": True})
        return reverse_moves
