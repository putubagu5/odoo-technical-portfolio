from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    is_cip = fields.Boolean('Is CIP Product?')
    cip_id = fields.Many2one('cip.configuration', 'CIP')
    project_cip_id = fields.Many2one('phase.project.cip','Project CIP', domain="[('cip_id','=',cip_id)]")

    @api.onchange("product_id")
    def onchange_product_id(self):
        super(PurchaseRequestLine, self).onchange_product_id()
        is_cip = False
        if self.product_id:
            if 'CIP' in self.product_id.display_name:
                is_cip = True
        self.is_cip = is_cip
