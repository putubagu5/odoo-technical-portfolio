from odoo import api, fields, models


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    def _str_domain_for_mv_line(self, search_str):
        res = super(AccountReconciliationWidget, self)._str_domain_for_mv_line(search_str)
        add = ['|', ('payment_id.multi_payment_reference', 'ilike', search_str)] + res
        return add
