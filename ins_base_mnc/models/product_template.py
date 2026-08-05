from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_buyer_id_domain(self):
        """ domain to get buyer_id using active company """
        return [('company_id', '=', self.env.company.id)]

    price_tolerance = fields.Float('Percent Value', default=5)
    buyer_id = fields.Many2one('res.buyer', 'Buyer (Deprecated)', domain=_get_buyer_id_domain,
                               help='NOTE: Obsolete')
    buyer_ids = fields.Many2many('res.buyer', 'rel_buyer_product',
                                 'product_id', 'buyer_id', string='Buyer',
                                 domain=_get_buyer_id_domain)

    @api.constrains('price_tolerance')
    def _check_price_tolerance(self):
        """ constrains function to check price_tolerance range """
        self.ensure_one()
        if self.price_tolerance > 100 or self.price_tolerance < 0:
            raise ValidationError('Percent Value must be between 0 - 100')

    @api.constrains('buyer_ids')
    def _check_buyer_ids(self):
        """ constrains function to check relation between product and buyer """
        self.ensure_one()
        if self.buyer_ids:
            # check if the buyer_ids are only 1 or nothing
            if len(self.buyer_ids) not in (0, 1):
                current_buyer = '\n'.join(self.buyer_ids.mapped('name'))
                raise ValidationError('Choose only 1 Buyer! You choose:\n%s' % current_buyer)
