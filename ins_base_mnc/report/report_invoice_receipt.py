from odoo import api, fields, models


class ReportInvoiceReceipt(models.AbstractModel):
    _name = 'report.ins_base_mnc.report_invoice_receipt_container'
    _description = 'Invoice Receipt Report'

    def _prepare_report_data(self):
        """ function to return data to print in report """
        # get all active_ids then browse records
        ids = self._context.get('active_ids', [])
        invoices = self.env['account.move'].search([('id', 'in', ids)],
                                                   order='partner_id, name')

        # loop records, construct a dict with partner_id as key, then all
        # invoice records
        data = {}
        for inv in invoices:
            partner_name = inv.partner_id.name if inv.partner_id else ''
            partner_address = '%s %s %s' % (inv.partner_id.street or '',
                                            inv.partner_id.street2 or '',
                                            inv.partner_id.city or '')
            site_address = '%s' % (inv.sites_id.site_address or '')
            delivery_address = '%s' % (inv.sites_id.delivery_address or '')
            data.setdefault(inv.partner_id.id, {
                'partner_name': partner_name,
                'partner_address': partner_address,
                'site_address': site_address,
                'delivery_address': delivery_address,
                'invoices': {},
            })
            inv_data = data[inv.partner_id.id]['invoices']
            inv_data.setdefault(inv.payment_reference, [])
            inv_data[inv.payment_reference] = [
                {
                    'name': x.name,
                    'dpp': '{:,.0f}'.format(x.price_subtotal),
                    'pajak': '{:,.0f}'.format(x.price_total - x.price_subtotal),
                    'total': '{:,.0f}'.format(x.price_total),
                    'dpp_add': x.price_subtotal,
                    'pajak_add': x.price_total - x.price_subtotal,
                    'total_add': x.price_total,
                    'faktur': x.move_id.tax_invoice_id.name if x.move_id.tax_invoice_id else '',
                } for x in inv.invoice_line_ids
            ]

        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        """ inherit function to process report data """
        # convert data to dict (this is from button_print)
        date_print = data['date_print']
        note = data['note']
        invoices = dict(self._prepare_report_data() or {})
        # then clean the dict, remove any context related keys and values
        if invoices.get('context'):
            invoices.pop('context')
        if invoices.get('report_type'):
            invoices.pop('report_type')
        if invoices.get('float_compare'):
            invoices.pop('float_compare')

        result = {
            'date_print': date_print,
            'note': note,
            'invoices': invoices.values(),
        }
        return result
