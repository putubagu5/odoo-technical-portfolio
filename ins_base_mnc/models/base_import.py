from odoo import api, fields, models


FIELDS_RECURSION_LIMIT = 4


class BaseImport(models.TransientModel):
    _inherit = 'base_import.import'

    @api.model
    def get_fields(self, model, depth=FIELDS_RECURSION_LIMIT):
        return super(BaseImport, self).get_fields(model, depth)
