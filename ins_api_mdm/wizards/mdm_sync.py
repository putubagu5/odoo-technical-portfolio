import logging
from odoo import api, fields, models


_logger = logging.getLogger()


class WizardMdmSync(models.TransientModel):
    _name = 'wizard.mdm.sync'
    _description = 'MDM Sync Wizard'

    def button_sync(self):
        """ function to trigger MDM sync """
        self.ensure_one()
        # get company from env
        company = self.env.company

        partner = self.env['res.partner']

        # call from partner: _get_token()
        token = partner._get_token()

        # trigger the sync
        if not token:
            _logger.info('No Token found, cannot connect to API')
            return

        partner._process_url(token, company.org_id)
        return True
