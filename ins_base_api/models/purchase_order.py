from odoo import api, fields, models


class PurchaseOrders(models.Model):
    _inherit = 'purchase.order'
    
    po_numbers_gen21 = fields.Char(string="PO Numbers Gen21", compute='_compute_po_numbers_gen21', store=True)
    
    @api.depends('order_line')
    def _compute_po_numbers_gen21(self):
        for record in self:
            po_number_list = []
            for line in record.order_line:
                if line.request_id:
                    if line.request_id.po_numbers_gen21:
                        po_number_list.append(line.request_id.po_numbers_gen21)  
            po_number_list = list(set(po_number_list))
            po_number_list.sort()
            po_numbers = ', '.join(po_number_list)
            record.po_numbers_gen21 = po_numbers
