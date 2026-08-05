from datetime import date
from odoo import api, fields, models
from odoo.exceptions import Warning


class WizardPrintBudget(models.TransientModel):
    _name = 'wizard.print.budget'
    _description = 'PMIS Print Budget'

    date = fields.Date('Print Date', default=date.today())
    note = fields.Char('Note')

    # def _check_records(self):
    #     """ helper function to check record validity """
    #     # only records with state in in_payment, paid and partial are accepted
    #     ids = self._context.get('active_ids', [])
    #     invoices = self.env['account.move'].browse(ids)

    #     empty_partner = any(not x.partner_id for x in invoices)
    #     if invoices and empty_partner:
    #         raise Warning('Cannot process invoice with no partner')

    #     payment_states = ('in_payment', 'paid', 'partial')
    #     states = ('posted',)
    #     invalid = any([
    #         x for x in invoices if x.payment_state not in payment_states and x.state not in states
    #     ])
    #     if invoices and invalid:
    #         raise Warning(
    #             'Only able to process invoices in Payment, Paid, Partial')

    def button_print(self):
        """ function to print selected records """
        # self._check_records()

        # get all selected invoices
        data = {
            'date_print': self.date.strftime('%d %b %Y'),
            'note': self.note,
            }
        return self.env.ref(
            'ins_project.report_budget_summary').report_action(
                None, data=data)
