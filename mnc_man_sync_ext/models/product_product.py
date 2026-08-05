from odoo import api, fields, models, _, tools

import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        _logger.info('di create - before')
        res = super(ProductProduct, self).create(vals)
        # after create, do populate data and send it to oracle atis
        _logger.info('di create')
        _logger.info(res)
        self.send_to_atis_insert(res.id)
        return res

    def write(self, vals):
        _logger.info('di write - before')
        res = super(ProductProduct, self).write(vals)
        # after write, do populate data and send it to oracle atis
        _logger.info('di write')
        _logger.info(res)
        self.send_to_atis_update(self.id)
        return res

    def send_to_atis_insert(self, res_id):
        _logger.info('posisi di send_to_atis_insert')
        _logger.info(res_id)
        sync_log_id = self.env['x.item'].sudo().create_odoo_stg(res_id)
        self.env['x.item'].sudo().create_push_to_atis(sync_log_id.id)
        self.env['x.item'].sudo().count_data_from_atis(sync_log_id.id)

    def send_to_atis_update(self, res_id):
        _logger.info('posisi di send_to_atis_update')
        _logger.info(res_id)
        sync_log_id = self.env['x.item'].sudo().write_odoo_stg(res_id)
        self.env['x.item'].sudo().write_push_to_atis(sync_log_id.id)
        self.env['x.item'].sudo().count_data_from_atis(sync_log_id.id)

