from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MultipleRemitted(models.TransientModel):
    _name = "multiple.remitted"
    _description = "Multiple remitted"

    transaction_date = fields.Date('Transaction Date', default=fields.Date.context_today)

    def action_multiple_remitted(self):
        for record in self._context.get('active_ids'):
            payments = self.env[self._context.get('active_model')].browse(record)
            for pick in payments:
                if not pick.remittance_flag:
                    pick.remittance_flag = True
                    pick.remittance_date = self.transaction_date

    def action_multiple_unremitted(self):
        for record in self._context.get('active_ids'):
            payments = self.env[self._context.get('active_model')].browse(record)
            for pick in payments:
                if pick.remittance_flag:
                    pick.remittance_flag = False
                    pick.un_remittance_date = self.transaction_date
