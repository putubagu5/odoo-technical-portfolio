from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = 'line_number asc, id desc'

    line_number = fields.Integer('Line No')
