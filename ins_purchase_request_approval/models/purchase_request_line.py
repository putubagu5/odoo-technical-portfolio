from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    def _get_state(self, state):
        """ helper function to get state """
        result = ''
        if state:
            result = dict(self._fields['request_state']._description_selection(self.env)).get(state)
        return result
