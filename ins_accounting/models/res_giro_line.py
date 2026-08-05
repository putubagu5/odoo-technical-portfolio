from odoo import api, fields, models
from odoo.exceptions import AccessError


class ResGiroLine(models.Model):
    _name = 'res.giro.line'
    _description = 'Giro Line'

    giro_id = fields.Many2one('res.giro', 'Related Giro')
    # journal_id = fields.Many2one('account.journal', related="giro_id.journal_id", 'Related Journal')
    series = fields.Char('Series')
    name = fields.Char('Giro Number')
    is_used = fields.Boolean('Used', compute='_compute_is_used',
                             inverse='_inverse_is_used', store=True)
    manual_used = fields.Boolean('Manual Used')
    cancelled = fields.Boolean('Cancelled', default=False)
    payment_id = fields.Many2one('account.payment', 'Payment')
    batch_payment_id = fields.Many2one('account.batch.payment', 'Batch Payment')

    def name_get(self):
        result = []
        for rec in self:
            name = '%s' % (rec.name)
            result.append((rec.id, name))
        return result

    @api.depends('payment_id', 'batch_payment_id', 'manual_used')
    def _compute_is_used(self):
        """ compute function to set is_used based on payment and batch """
        for rec in self:
            rec.is_used = rec.manual_used or bool(rec.payment_id) or bool(rec.batch_payment_id)

    @api.onchange('is_used')
    def _inverse_is_used(self):
        for rec in self:
            rec.manual_used = rec.is_used if rec.is_used else False

    def unlink(self):
        """ inherit function to check if is_used """
        for rec in self:
            if rec.is_used:
                raise AccessError('Cannot delete used data')
