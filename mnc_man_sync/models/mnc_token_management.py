from odoo import api, fields, models, _, tools
import secrets, string
import logging

_logger = logging.getLogger(__name__)


class MncTokenManagement(models.Model):
    _name = 'mnc.token.management'
    _description = 'MNC Token Management'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='set default', select=True)
    model_name = fields.Char(related='model_id.model', string="Model Name")
    token = fields.Char(string='Token', required=True)
    prev_token = fields.Char(string='Previous Token')
    state = fields.Boolean(string='Status', default=True)

    ora_atis_user = fields.Char(String="ATIS - DB Username", help="ATIS - Oracle Staging - DB Username")
    ora_atis_pass = fields.Char(String="ATIS - DB Password", help="ATIS - Oracle Staging - DB Password")
    ora_atis_dsn = fields.Char(String="ATIS - DSN",
                               help="ATIS - Oracle Staging - DSN =   arjuna.mncgroup.com:1523/rcti")

    def btn_gen_token(self):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(89))
        #
        _logger.info(password)
        #
        self.prev_token = self.token
        self.token = password

    def get_token(self, model_name):
        o_token = self.env['mnc.token.management'].search([
            ('model_name', '=', model_name),
            ('state', '=', True),
        ], limit=1)
        #
        return o_token.token

    def get_ora_atis_user(self, model_name):
        o_token = self.env['mnc.token.management'].search([
            ('model_name', '=', model_name),
            ('state', '=', True),
        ], limit=1)
        #
        return o_token.ora_atis_user

    def get_ora_atis_pass(self, model_name):
        o_token = self.env['mnc.token.management'].search([
            ('model_name', '=', model_name),
            ('state', '=', True),
        ], limit=1)
        #
        return o_token.ora_atis_pass

    def get_ora_atis_dsn(self, model_name):
        o_token = self.env['mnc.token.management'].search([
            ('model_name', '=', model_name),
            ('state', '=', True),
        ], limit=1)
        #
        return o_token.ora_atis_dsn
