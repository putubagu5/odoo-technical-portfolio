from odoo import api, fields, models, _, tools

import logging
_logger = logging.getLogger(__name__)

class SL(models.Model):
    _inherit = "stock.picking"
    #
    # @api.model
    # def create(self, vals):
    #     _logger.info('di create - before')
    #     res = super(SL, self).create(vals)
    #     # after create, do populate data and send it to oracle atis
    #     _logger.info('di create')
    #     _logger.info(res)
    #     self.send_to_atis_insert(res.id)
    #     return res
    #


    def write(self, vals):
        _logger.info('di write - before')
        res = super(SL, self).write(vals)
        # after write, do populate data and send it to oracle atis
        _logger.info('di write')
        _logger.info(res)
        _logger.info(self.id)
        _logger.info(vals)
        _logger.info(self.state)

        if self.state == 'done':
            _logger.info('state berubah menjadi done')
            self.env['r12.po.receives'].send_one_to_atis(self.id)
            _logger.info('send_all_to_atis ditekan')
        return res

