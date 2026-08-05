from num2words import num2words
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    amount_in_words = fields.Char('Amount To Words', compute='amount_to_text')
    amount_in_words_2 = fields.Char('Amount To Words 2', compute='amount_to_text_2')
    assignee_id = fields.Many2one('res.assignee', 'Assignee')

    @api.depends('amount_total', 'currency_id')
    def amount_to_text(self):
        for rec in self:
            if self.currency_id:
                # lang = 'id' if self.currency_id.name == 'IDR' else 'en'
                lang = 'en'
                currency_in_words = rec.currency_id.currency_unit_label
                # convert to integer to remove decimal place
                words_amount = num2words(int(rec.amount_total), lang=lang)
                rec.amount_in_words = words_amount.title() + " " + currency_in_words
            else:
                self.amount_in_words = ''

    @api.depends('amount_total', 'currency_id')
    def amount_to_text_2(self):
        for rec in self:
            if self.currency_id:
                lang_2 = 'id' if rec.currency_id.name == 'IDR' else 'en'
                currency_in_words_2 = rec.currency_id.currency_unit_label
                # convert to integer to remove decimal place
                words_amount_2 = num2words(int(rec.amount_total), lang=lang_2)
                rec.amount_in_words_2 = words_amount_2.title() + " " + currency_in_words_2
            else:
                rec.amount_in_words_2 = ''
