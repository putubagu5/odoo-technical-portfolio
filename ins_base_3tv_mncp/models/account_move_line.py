from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ou_id = fields.Many2one('mnc.operating.unit', 'OU', ondelete='restrict')
    operating_unit_ids = fields.Many2many(
        'operating.unit', string="Area", domain="[('user_ids', '=', uid)]",
        store='True'
    )
    asset_location_id = fields.Many2one('asset.location', 'Location')

    @api.onchange('ou_id')
    def _onchange_ou_id(self):
        """ onchange function to set label """
        for rec in self:
            if rec.ou_id:
                rec.name = rec.ou_id.name
