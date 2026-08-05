from odoo import api, fields, models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def _get_test_email_addresses(self):
        email_from, email_to = super(IrMailServer, self)._get_test_email_addresses()
        email_to = 'odooerp03.prod@mncgroup.com'  # bypass the noreply
        return email_from, email_to
