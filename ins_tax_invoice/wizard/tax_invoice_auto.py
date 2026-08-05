from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardTaxInvoiceAuto(models.TransientModel):
    _name = 'wizard.tax.invoice.auto'
    _description = 'Wizard for Tax Invoice Auto Assignment'

    date_start = fields.Date('Invoice Date Start')
    date_end = fields.Date('Invoice Date End')
    invoice_ids = fields.Many2many('account.move', string='Invoices')
    qty_found = fields.Integer('Found Invoices', default=0)

    def button_confirm(self):
        domain = [('is_used', '=', False)]  # find unused tax invoice
        tax_invoice_ids = self.env['tax.invoice'].search(domain, order='name asc')
        efaktur_len = len(tax_invoice_ids)
        i = 0
        for inv in self.invoice_ids:
            if i < efaktur_len:
                inv.tax_invoice_id = tax_invoice_ids[i]
            else:
                break
            i += 1

        self.env.cr.commit()
        raise UserError("Selesai penomoran E-Faktur %s invoices(s)!" % i)

    def button_find(self):
        found = 0
        inv_obj = self.env['account.move']
        domain = [
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('state', '=', 'posted'),
            ('tax_invoice_id', '=', False),
            ('move_type', '=', 'out_invoice')
        ]
        invoices = inv_obj.search(domain)
        invoice_ids = []
        for inv in invoices:
            invoice_ids.append((4, inv.id))
            found += 1

        self.invoice_ids = invoice_ids
        self.qty_found = found
        # return the same wizard
        return {
            'name': 'Auto Number eFaktur',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
