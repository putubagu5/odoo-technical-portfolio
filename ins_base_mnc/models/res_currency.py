from odoo import api, fields, models, _


class ResCurrency(models.Model):
    _inherit = "res.currency"

    actual_rate = fields.Float(compute='_compute_current_actual_rate', string='Current BI Rate', digits=0,
                               help='The BI rate of the currency to the currency of rate 1.')
    actual_rate_date = fields.Date(compute='_compute_current_actual_rate', string='Current BI Rate Date')

    def _get_actual_rates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush(['actual_rate', 'currency_id', 'company_id', 'name'])
        query = """SELECT c.id,
                          COALESCE((SELECT r.actual_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    def _get_actual_dates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush(['actual_rate', 'currency_id', 'company_id', 'name'])
        query = """SELECT c.id,
                          COALESCE((SELECT r.name FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), NULL) AS date
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_dates = dict(self._cr.fetchall())
        return currency_dates

    @api.depends('rate_ids.actual_rate')
    def _compute_current_actual_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
        # the subquery selects the last BI rate before 'date' for the given currency/company
        currency_rates = self._get_actual_rates(company, date)
        currency_dates = self._get_actual_dates(company, date)
        # last_rate = self.env['res.currency.rate']._get_last_actual_rates_for_companies(company)
        for currency in self:
            currency.actual_rate = currency_rates.get(currency.id) or 1.0
            currency.actual_rate_date = currency_dates.get(currency.id) or False
            # currency.inverse_rate = 1 / currency.actual_rate
            # if currency != company.currency_id:
            #     currency.rate_string = '1 %s = %.6f %s' % (company.currency_id.name, currency.actual_rate, currency.name)
            # else:
            #     currency.rate_string = ''


# class ResCurrencyRate(models.Model):
#     _inherit = "res.currency.rate"

#     def _get_last_actual_rates_for_companies(self, companies):
#         return {
#             company: company.currency_id.rate_ids.filtered(lambda x: (
#                 x.actual_rate
#                 and x.company_id == company or not x.company_id
#             )).sorted('name')[-1:].actual_rate or 1
#             for company in companies
#         }
