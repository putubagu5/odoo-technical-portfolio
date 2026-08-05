from odoo import api, fields, models


class WizardMassCipDetail(models.TransientModel):
    _name = 'wizard.mass.cip.detail'
    _description = 'Mass CIP Detail'

    # rules
    # 1. PO: validated
    # 2. Picking: done
    # 3. Invoice: paid
    # 4. Product: consumable
    generate_id = fields.Many2one('wizard.mass.cip.generate', 'Generate')
    company_id = fields.Many2one('res.company', 'Company',
                                 related='generate_id.company_id')
    type = fields.Selection(related='generate_id.type')
    selected = fields.Boolean('Selected', default=True)
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    partner_id = fields.Many2one('res.partner', 'Vendor',
                                 related='purchase_id.partner_id')
    picking_id = fields.Many2one('stock.picking', 'Receipt Ref.')
    product_id = fields.Many2one('product.product', 'Product',
                                 related='invoice_line_id.product_id')
    product_code = fields.Char('Product Code', related='product_id.default_code')
    invoice_id = fields.Many2one('account.move', 'Invoice')
    invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line')
    qty = fields.Float('Qty')
    date_acquisition = fields.Date('Acquisition Date')
    amount = fields.Float('Acquisition Value')
    price_unit = fields.Float('Price Unit')
    cip_id = fields.Many2one('cip.configuration','CIP', related='product_id.cip_id')
    model_id = fields.Many2one('account.asset', 'Asset Category',
                               related='product_id.asset_model_id')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='invoice_line_id.analytic_account_id')
    purchase_line_number = fields.Integer('PO line no')
