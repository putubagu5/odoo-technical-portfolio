from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_domain(self):
        """ function to get domain for asset_model_ids """
        company = self.company_id.id if self.company_id else self.env.user.company_id.id
        domain = [('company_id', '=', company), ('state', '=', 'model')]
        return domain

    asset_model_ids = fields.Many2many('account.asset', string='Asset Models',
                                       domain=lambda self:[('state','=','model')])

    asset_model_id = fields.Many2one('account.asset', string='Asset Models',
                                     company_dependent=True, domain="[('company_id', '=', current_company_id), ('state', '=', 'model')]")
    is_asset = fields.Boolean('Is Asset', default=False)
