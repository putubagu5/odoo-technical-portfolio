from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    default_all_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Default All Account')
    purchase_type = fields.Selection([
        ('purchase', "Purchase"), ('prepayment', "Prepayment"), ('settlement', "Settlement")
    ], string="Purchase Type", default='purchase')
    suspense_payment_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Suspense Payment Account')
    is_applied_invoice = fields.Boolean(check_company=True, copy=False, ondelete='restrict', default=False,
                                        string='Is Applied Invoice Journal')
    is_applied_customer = fields.Boolean(check_company=True, copy=False, ondelete='restrict', default=False,
                                         string='Is Applied Customer Journal')
    is_applied_prepayment = fields.Boolean(check_company=True, copy=False, ondelete='restrict', default=False,
                                         string='Is Applied Prepayment Journal')
    exclude_cf_report = fields.Boolean(check_company=True, copy=False, ondelete='restrict', default=False,
                                         string='Exclude CF Report')

    @api.depends('type')
    def _compute_default_account_type(self):
        # Override default method to accomodate Prepayment and Settlement
        # that use cash/bank account but the type equal to purchase
        default_account_id_types = {
            'bank': 'account.data_account_type_liquidity',
            'cash': 'account.data_account_type_liquidity',
            'prepayment': 'account.data_account_type_prepayments',
            'sale': 'account.data_account_type_revenue',
            'purchase': 'account.data_account_type_expenses'
        }

        for journal in self:
            if journal.type in default_account_id_types:
                if journal.type == 'purchase' and journal.purchase_type in ['prepayment', 'settlement']:
                    journal.default_account_type = self.env.ref(default_account_id_types['prepayment']).id
                else:
                    journal.default_account_type = self.env.ref(default_account_id_types[journal.type]).id
            else:
                journal.default_account_type = False
