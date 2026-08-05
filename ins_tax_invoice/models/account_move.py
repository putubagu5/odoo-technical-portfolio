from babel.numbers import format_currency
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_invoice_id = fields.Many2one('tax.invoice', 'Nomor Seri Faktur',
                                     copy=False, domain='[("company_id", "=", company_id)]')
    masa_pajak = fields.Char('Masa Pajak', compute='_compute_masa_pajak')
    tahun_pajak = fields.Char('Tahun Pajak', compute='_compute_masa_pajak')
    tax_invoice_no = fields.Char('Nomor Seri Faktur Pajak', help='For vendor')
    is_efaktur_exported = fields.Boolean('Is eFaktur Exported')
    date_efaktur_exported = fields.Datetime('eFaktur Exported Date')
    ar_receipt_type = fields.Selection(
        selection=[
            ('iklan', 'Iklan'),
            ('non_iklan', 'Non Iklan'),
        ], string='AR Receipt Type')

    @api.depends('invoice_date')
    def _compute_masa_pajak(self):
        """ compute function to get masa and tahun pajak from invoice_date """
        valid_type = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        for rec in self:
            masa = tahun = ''
            if rec.invoice_date and rec.move_type in valid_type:
                masa = rec.invoice_date.strftime('%m')
                tahun = rec.invoice_date.strftime('%Y')
            rec.masa_pajak = masa
            rec.tahun_pajak = tahun

    @api.onchange('ar_receipt_type')
    def _onchange_ar_receipt_type(self):
        """ onchange function to autofill tax_invoice_id """
        self.ensure_one()
        if self.ar_receipt_type:
            first = self.env['tax.invoice'].search([
                ('is_used', '=', False),
                ('company_id', '=', self.company_id.id),
            ])
            # first = first.filtered(lambda x: not x.is_used)
            if first:
                self.tax_invoice_id = first[0].id
            # else:
            #     raise ValidationError('No more usable tax number.')

    def action_post(self):
        """ inherit action_post function to set is_efaktur_exported to False """
        res = super(AccountMove, self).action_post()
        for rec in self:
            rec.is_efaktur_exported = False
        return res

    def localize_amount(self, amount):
        """ helper function to accept number and localize using babel """
        return format_currency(amount, 'IDR', u'#,##0.00', locale='id_ID',
                               currency_digits=False)
