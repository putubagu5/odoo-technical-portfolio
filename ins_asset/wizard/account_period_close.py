from odoo import api, fields, models


class WizardAccountPeriodClose(models.TransientModel):
    _inherit = 'account.period.close'

    def data_save(self):
        """ inherit function to check on asset """
        active_ids = self._context.get('active_ids', [])
        period_ids = self.env['account.period'].browse(active_ids)
        # TODO
        return super(WizardAccountPeriodClose, self).data_save()
