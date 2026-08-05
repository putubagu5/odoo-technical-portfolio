# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if vals.get('date_order'):
            period_line_id = self.env['purchase.period.line'].search([
                ('date_start', '<=', vals['date_order']), ('date_end', '>=', vals['date_order']),
                ('company_id.id', '>=', self.env.company.id)
            ], limit=1)
            if period_line_id:
                if period_line_id.state == 'open':
                    vals['po_period_line_id']= period_line_id.id
                else:
                    raise ValidationError("Purchase Order Period is Closed.")

        return super(PurchaseOrder, self).create(vals)
    
    def write(self, vals):
        if vals.get('date_order'):
            period_line_id = self.env['purchase.period.line'].search([
                ('date_start', '<=', vals['date_order']), ('date_end', '>=', vals['date_order']),
                ('company_id.id', '>=', self.env.company.id)
            ], limit=1)
            if period_line_id:
                if period_line_id.state == 'open':
                    vals['po_period_line_id']= period_line_id.id
                else:
                    raise ValidationError("Purchase Order Period is Closed.")

        return super(PurchaseOrder, self).write(vals)
