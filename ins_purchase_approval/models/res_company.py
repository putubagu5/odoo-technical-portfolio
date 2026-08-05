from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_dynamic_approval = fields.Boolean('Purchase Dynamic Approval',
                                               default=False)
