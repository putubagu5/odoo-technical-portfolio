from odoo import models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """ inherit action_confirm to check credit limit """
        # check if partner_id.allow_overlimit is True, proceed, False, return
        if not self.partner_id.allow_overlimit:
            # if credit_limit > amount_total + partner_id.credit, error
            total_due = self.amount_total + self.partner_id.credit
            if self.partner_id.credit_limit < total_due:
                raise ValidationError('Amount exceeds Credit Limit')
        res = super(SaleOrder, self).action_confirm()
        return res
