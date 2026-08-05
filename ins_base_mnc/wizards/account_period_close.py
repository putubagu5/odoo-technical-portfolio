from odoo import models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class WizardAccountPeriodClose(models.TransientModel):
    _inherit = 'account.period.close'

    def data_save(self):
        """ override function to check on asset moves """
        # NOTE this is a glue function to connect ins_asset and fiscal_year_sync_app
        account_move_obj = self.env['account.move']
        mode = 'done'
        active_ids = self._context.get('active_ids')
        period_ids = self.env['account.period'].browse(active_ids)
        for record in self:
            if record.sure:
                for period_id in period_ids:
                    # find all journals with period and state is draft
                    domain = [
                        ('asset_id', '=', False),
                        ('period_id', '=', period_id.id),
                        ('move_type', '=', 'entry'),
                        ('state', '=', 'draft'),
                        ('company_id', '=', self.env.company.id)
                    ]
                    account_move_ids = account_move_obj.search(domain)
                    if account_move_ids:
                        raise UserError(_('In order to close a period, you must first post related journal entries.'))
                    self._cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, period_id.id))
                    self._cr.execute('update account_period set state=%s where id=%s', (mode, period_id.id))

        # check payment period
        for period in period_ids:
            payment_domain = [
                ('date_start', '=', period.date_start),
                ('date_end', '=', period.date_stop),
                ('payment_period_id.company_id.id', '=', period.company_id.id)
            ]
            receipt_domain = [
                ('date_start', '=', period.date_start),
                ('date_end', '=', period.date_stop),
                ('receipt_period_id.company_id.id', '=', period.company_id.id)
            ]
            asset_domain = [
                ('date_start', '=', period.date_start),
                ('date_end', '=', period.date_stop),
                ('period_id.company_id.id', '=', period.company_id.id)
            ]

            invoice_domain = [
                ('date_start', '=', period.date_start),
                ('date_end', '=', period.date_stop),
                ('invoice_period_id.company_id.id', '=', period.company_id.id),
                ('invoice_period_id.move_type', '=', 'out_invoice')
            ] 

            bill_domain = [
                ('date_start', '=', period.date_start),
                ('date_end', '=', period.date_stop),
                ('invoice_period_id.company_id.id', '=', period.company_id.id),
                ('invoice_period_id.move_type', '=', 'in_invoice')
            ] 

            payment_periods = self.env['payment.period.line'].search(payment_domain)
            if payment_periods and any([x.state != 'close' for x in payment_periods]):
                raise ValidationError('Unable to close period because Payment Period has not been closed')

            receipt_periods = self.env['receipt.period.line'].search(receipt_domain)
            if receipt_periods and any([x.state != 'close' for x in receipt_periods]):
                raise ValidationError('Unable to close period because Receipt Period has not been closed')
            
            asset_periods = self.env['asset.period.line'].search(asset_domain)
            if asset_periods and any([x.state != 'close' for x in asset_periods]):
                raise ValidationError('Unable to close period because Asset Period has not been closed')
            
            invoice_periods = self.env['invoicing.period.line'].search(invoice_domain)
            if invoice_periods and any([x.state != 'close' for x in invoice_periods]):
                raise ValidationError('Unable to close period because Invoice Period has not been closed')
            
            bill_periods = self.env['invoicing.period.line'].search(bill_domain)
            if bill_periods and any([x.state != 'close' for x in bill_periods]):
                raise ValidationError('Unable to close period because Bill Period has not been closed')
            

        return {'type': 'ir.actions.act_window_close'}
