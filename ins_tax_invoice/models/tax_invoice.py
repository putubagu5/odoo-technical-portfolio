from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TaxInvoice(models.Model):
    _name = 'tax.invoice'
    _description = 'Tax Invoice Number'

    name = fields.Char('eFaktur Number')
    year = fields.Integer('Year')
    is_used = fields.Boolean('Is Used', compute='_compute_is_used', store=True)
    invoice_ids = fields.One2many('account.move', 'tax_invoice_id', 'Invoices')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    state = fields.Selection([
        ('open', 'Open'),
        ('cancel', 'Cancel'),
    ], 'Status', default='open')

    @api.depends('invoice_ids')
    def _compute_is_used(self):
        """ compute function to set is_used based on invoice_ids existence """
        for rec in self:
            rec.is_used = True if rec.invoice_ids else False

    def button_cancel(self):
        """ function to set state to cancel """
        for rec in self:
            if rec._check_invoices():  # check first
                raise ValidationError('Invoices are already paid/in payment!')
            # TODO all good, cancel invoice
            rec.write({'state': 'cancel'})

    def _check_invoices(self):
        """ helper function to check invoices status before cancellation """
        # find if any invoice is in payment process
        return any(x.state in ('in_payment', 'paid', 'partial') for x in self.invoice_ids)
