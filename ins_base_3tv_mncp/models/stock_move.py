from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    ou_id = fields.Many2one('mnc.operating.unit', 'Operating Unit')
    wilayah_id = fields.Many2one(
        'operating.unit', string="Wilayah",
        store='True'
    )

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value,
                                       credit_value, debit_account_id,
                                       credit_account_id, description):
        """ inherit function to add ou_id to credit and debit lines """
        self.ensure_one()
        res = super(StockMove, self)._generate_valuation_lines_data(
            partner_id, qty, debit_value, credit_value, debit_account_id,
            credit_account_id, description)
        # take the credit and debit dict inside, add new key ou_id
        res['credit_line_vals']['ou_id'] = self.ou_id.id
        res['debit_line_vals']['ou_id'] = self.ou_id.id
        return res
