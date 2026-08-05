from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_cost_progress_id = fields.Many2one('cip.configuration', 'CIP')
    created_asset_ids = fields.Many2many('account.asset',
                                         'generate_asset_move_rel',
                                         'move_line_id', 'asset_id',
                                         string='Created Assets')
    asset_analytic_account_id = fields.Many2one('account.analytic.account',
                                                'Asset Analytic')

    @api.depends('product_id', 'account_id', 'partner_id', 'date',
                 'asset_analytic_account_id')
    def _compute_analytic_account_id(self):
        """ inherit compute function to add analytic """
        super(AccountMoveLine, self)._compute_analytic_account_id()
        for rec in self:
            if rec.asset_analytic_account_id:  # check for asset analytic
                rec.analytic_account_id = rec.asset_analytic_account_id
