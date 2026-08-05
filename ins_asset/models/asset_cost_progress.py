from odoo import api, fields, models


class AssetCostProgress(models.Model):
    _name = 'asset.cost.progress'
    _description = 'Asset Cost in Progress'

    name = fields.Char('Name', copy=False)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    model_id = fields.Many2one('account.asset', 'Category',
                               domain=[('state', '=', 'model')])
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close'),
    ], 'State', default='open')

    def button_close(self):
        """ function to change state to close """
        for rec in self:
            rec.write({'state', 'close'})
