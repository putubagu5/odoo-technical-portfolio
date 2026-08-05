from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    actual_rate = fields.Float('BI Rate')
    is_pph_amount_info = fields.Boolean('PPH Amount Info')
    pph_amount = fields.Monetary('PPH Amount', compute='_compute_pph_amount')

    @api.onchange('currency_id', 'manual_currency_rate_active',
                  'manual_currency_rate', 'date')
    def _onchange_actual_rate(self):
        """ onchange function to set actual_rate to manual_currency_rate if any """
        self.ensure_one()
        if self.currency_id and self.currency_id.name != 'IDR':
            if not self.manual_currency_rate_active:
                sql = """
                    SELECT actual_rate AS rate
                    FROM res_currency_rate
                    WHERE company_id = %s AND currency_id = %s AND name <= '%s'
                    ORDER BY name DESC LIMIT 1
                """ % (self.company_id.id, self.currency_id.id, self.date)
                self.env.cr.execute(sql)
                currency = self.env.cr.dictfetchone()
                self.actual_rate = currency.get('rate', 1) if currency else 1
            else:
                self.actual_rate = self.manual_currency_rate
        else:
            self.actual_rate = 1

    @api.depends('amount_untaxed', 'is_pph_amount_info')
    def _compute_pph_amount(self):
        """ compute pph amount times 2% """
        for rec in self:
            amount = 0.0
            if rec.is_pph_amount_info is True:
                amount = (2 / 100) * rec.amount_untaxed
            rec.pph_amount = amount
