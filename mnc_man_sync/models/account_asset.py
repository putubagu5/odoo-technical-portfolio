from odoo import models, fields, api, _


class AccountAssetInherit(models.Model):
    _inherit = 'account.asset'

    total_depreciation = fields.Integer(string='Total Depreciation', compute='_compute_depreciation')

    @api.depends('depreciation_line_ids.move_check')
    def _compute_depreciation(self):
        for record in self:
            total = sum(record.depreciation_line_ids.mapped('move_check'))
            record.total_depreciation = total
