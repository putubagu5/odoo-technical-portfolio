from datetime import date
from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AssetSourceLine(models.Model):
    _name = 'asset.source.line'

    asset_id = fields.Many2one('account.asset', string='Asset')
    # invoice_id = fields.Many2one('account.move',string='Invoice No')
    invoice_name = fields.Char('Invoice No')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_line_number = fields.Integer(string='Invoice Line No')
    # purchase_id = fields.Many2one('purchase.order',string='Purchase Order')
    purchase_name = fields.Char('Purchase Order No')
    purchase_line_number = fields.Integer(string='PO Line No')
    description = fields.Char('Description')
    amount = fields.Float('Amount')
    product_id = fields.Many2one('product.product',string='Product')
    # category_id =