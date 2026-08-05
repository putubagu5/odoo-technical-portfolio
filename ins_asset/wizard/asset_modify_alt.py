from odoo import api, fields, models, _
from odoo.exceptions import Warning


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    asset_category_id = fields.Many2one(
        'account.asset', string='Asset Category')

    def modify(self):
        # """ inherit function to add asset category """
        # if self.need_date is False:
        #     raise Warning('Please change depreciable amount or not depreciable amount.')
        # else:

        if self.asset_category_id:
            # create journal entres when changes asset category without modify residual value
            print('masuk sini buat create journal')
            print('AAAAAAAAAAAAAAAAAAAAA')
            move = self.env['account.move'].create({
                'journal_id': self.asset_category_id.journal_id.id,
                'date': fields.Date.today(),
                'line_ids': [
                    (0, 0, {
                        'account_id': self.asset_category_id.account_asset_id.id,
                        'debit': self.asset_id.original_value,
                        'credit': 0,
                        'name': _('Value new original value for: %(asset)s', asset=self.asset_id.name),
                    }),
                    (0, 0, {
                        'account_id': self.asset_category_id.account_depreciation_id.id,
                        'debit': 0,
                        'credit': self.asset_id.amount_depreciated,
                        'name': _('Value new depreciation value for: %(asset)s', asset=self.asset_id.name),
                    }),
                    (0, 0, {
                        'account_id': self.asset_id.account_depreciation_id.id,
                        'debit': self.asset_id.amount_depreciated,
                        'credit': 0,
                        'name': _('Value old depreciatation value for: %(asset)s', asset=self.asset_id.name),
                    }),
                    (0, 0, {
                        'account_id': self.asset_id.account_asset_id.id,
                        'debit': 0,
                        'credit': self.asset_id.original_value,
                        'name': _('Value old original value for: %(asset)s', asset=self.asset_id.name),
                    }),
                ],
            })
            move._post()

            # end modify create journal
            # update the asset category of the asset
            self.asset_id.write({
                'model_id': self.asset_category_id.id,
                'account_asset_id': self.asset_category_id.account_asset_id.id,
                'account_depreciation_id': self.asset_category_id.account_depreciation_id.id,
                'account_depreciation_expense_id': self.asset_category_id.account_depreciation_expense_id.id,
                'journal_id': self.asset_category_id.journal_id.id,
                'account_analytic_id': self.asset_category_id.account_analytic_id.id,
                'analytic_tag_ids': [(6, 0, self.asset_category_id.analytic_tag_ids.ids)],
            })
        self.asset_id.method_number = self.method_number
        self.asset_id.compute_depreciation_list()
        # always call the parent function
        return super(AssetModify, self).modify()
