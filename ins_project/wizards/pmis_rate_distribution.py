from odoo import api, fields, models


class WizardPmisRateDistribution(models.TransientModel):
    _name = 'wizard.pmis.rate.distribution'
    _description = 'Rate Distribution'

    def button_distribute(self):
        """ function to distribute rate """
        active_ids = self._context.get('active_ids', [])
        budgets = self.env['pmis.budget'].browse(active_ids)
        if budgets:
            for line in budgets.budget_ids:
                line._process_distribution()
        return
