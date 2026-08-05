from datetime import date
from odoo import api, fields, models


class AssetAssignment(models.Model):
    _name = 'asset.assignment'
    _description = 'Asset Assignment'
    _check_company_auto = True

    name = fields.Char('Name', copy=False, default='/')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    asset_id = fields.Many2one('account.asset', 'Asset', ondelete='restrict')
    date = fields.Date('Date', default=date.today())
    last_assignee_id = fields.Many2one('hr.employee', 'Last Assignee')
    last_analytic_account_id = fields.Many2one('account.analytic.account',
                                               'Last Analytic Account',
                                               check_company=True)
    new_assignee_id = fields.Many2one('hr.employee', 'New Assignee')
    new_analytic_account_id = fields.Many2one('account.analytic.account',
                                              'New Analytic Account',
                                              check_company=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], 'State', default='draft')

    @api.model
    def create(self, vals):
        """ inherit create function to assign sequence """
        if vals.get('name') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('asset.assignment')
        res = super(AssetAssignment, self).create(vals)
        return res

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        """ onchange function to set last analytic and assignee """
        if self.asset_id:
            self.last_analytic_account_id = self.asset_id.account_analytic_id
            self.last_assignee_id = self.asset_id.assignee_id

    def button_done(self):
        """ function to set analytic account and assignee to asset """
        for rec in self:
            rec.asset_id.write({
                'account_analytic_id': rec.new_analytic_account_id.id,
                'assignee_id': rec.new_assignee_id.id,
            })
            rec.write({'state': 'done'})
