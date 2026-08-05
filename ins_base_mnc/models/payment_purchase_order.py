from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class PaymentPurchaseOrder(models.Model):
    _name = 'payment.purchase.order'
    _description = 'Payment Purchase Order'

    name = fields.Char(string="Payment Number", default='/')
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    pr_numbers = fields.Char("PR Numbers", related="purchase_id.pr_numbers")
    rr_numbers = fields.Text("RR Numbers", related="purchase_id.rr_numbers")
    request_date = fields.Date(string='Request Date', default=datetime.today())
    due_date = fields.Date(string='Due Date')
    paid_on_behalf = fields.Char(string="Paid On Behalf Of")
    invoice_number = fields.Char(string="Nomor Kwitansi / Invoice")
    faktur_number = fields.Char(string="Nomor Faktur Pajak")
    berita_acara_number = fields.Char(string="No Berita Acara")
    contract = fields.Char(string="Contract")
    uat = fields.Char(string="UAT")
    description_payment = fields.Text(string="Keterangan Pembayaran")
    currency_id = fields.Many2one('res.currency', 'Currency')
    dpp_amount = fields.Monetary(
        currency_field='currency_id', string="Dasar Penganaan Pajak")
    vat = fields.Integer(string="Vat(%)", default=0)
    vat_amount = fields.Monetary(
        currency_field='currency_id', string="Vat Amount",
        compute='_compute_vat_amount', readonly=True, default=0)
    income_tax = fields.Integer(string="Income Tax(%)", default=0)
    income_tax_amount = fields.Monetary(
        currency_field='currency_id', string="Income Tax Amount",
        compute='_compute_income_tax_amount', readonly=True, default=0)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        result = super(PaymentPurchaseOrder, self).create(vals)
        if result.name == '/':
            number = self.env['ir.sequence'].get('payment.purchase.order') or '/'
            result.write({'name': number})
        return result
    
    @api.constrains('vat')
    def _check_vat(self):
        if self.vat > 100 or self.vat < 0:
            raise ValidationError(_('Enter Value Between 0-100.'))

    @api.constrains('income_tax')
    def _check_income_tax(self):
        if self.income_tax > 100 or self.income_tax < 0:
            raise ValidationError(_('Enter Value Between 0-100.'))

    @api.depends('dpp_amount', 'vat')
    def _compute_vat_amount(self):
        for rec in self:
            vat_amount = 0
            if rec.dpp_amount > 0 and rec.vat > 0:
                vat_amount = rec.dpp_amount * (rec.vat / 100)
            rec.vat_amount = vat_amount

    @api.depends('dpp_amount', 'income_tax')
    def _compute_income_tax_amount(self):
        for rec in self:
            income_tax_amount = 0
            if rec.dpp_amount > 0 and rec.income_tax > 0:
                income_tax_amount = rec.dpp_amount * (rec.income_tax / 100)
            rec.income_tax_amount = income_tax_amount
