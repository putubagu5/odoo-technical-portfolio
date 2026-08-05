from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    words1 = fields.Char(string="Words 1", compute="_compute_words")
    words2 = fields.Char(string="Words 2", compute="_compute_words")
    iban = fields.Char('IBAN')

    @api.depends('amount_in_words_2')
    def _compute_words(self):
        for record in self:
            words1 = ''
            words2 = ''
            if record.amount_in_words_2:
                txt_split = record.amount_in_words_2.split()
                if len(txt_split) > 0:
                    is_words2 = False
                    for text in txt_split:
                        if len(words1 + text) < 78 and is_words2 == False:
                            words1 = words1 + text + ' '
                        else:
                            is_words2 = True
                            words2 = words2 + text + ' '
                    record.words1 = words1
                    record.words2 = words2