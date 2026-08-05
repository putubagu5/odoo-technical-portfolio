from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class WizardSellAsset(models.TransientModel):
    _name = 'wizard.sell.asset'
    _description = 'Sell Assets'

    action = fields.Selection([
        ('sell', 'Sell'),
        ('dispose', 'Dispose'),
    ], 'Assets to', default='sell')
    asset_ids = fields.Many2many('account.asset', string='Selected Assets')
    invoice_id = fields.Many2one(
        'account.move', 'Invoice',
        domain=[('move_type', 'in', ('out_invoice',)), ('state', '=', 'posted')])
    invoice_name = fields.Char('Invoice Number', related="invoice_id.name")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    gain_account_id = fields.Many2one('account.account', related='company_id.gain_account_id', help="Account used to write the journal item in case of gain", readonly=False)
    loss_account_id = fields.Many2one('account.account', related='company_id.loss_account_id', help="Account used to write the journal item in case of loss", readonly=False)
    gain_or_loss = fields.Selection([('gain', 'Gain'), ('loss', 'Loss'), ('no', 'No')], compute='_compute_gain_or_loss', help="Technical field to know is there was a gain or a loss in the selling of the asset")

    @api.depends('asset_ids', 'invoice_id')
    def _compute_gain_or_loss(self):
        for record in self:
            line = len(record.invoice_id.invoice_line_ids) == 1 and record.invoice_id.invoice_line_ids or self.env['account.move.line']
            residual = 0
            for asset in self.asset_ids:
                residual += asset.value_residual
            if residual < abs(line.balance):
                record.gain_or_loss = 'gain'
            elif residual > abs(line.balance):
                record.gain_or_loss = 'loss'
            else:
                record.gain_or_loss = 'no'

    def do_sell(self):
        """ function to sell selected assets """

        self.ensure_one()
        invoice_lines = self.invoice_id.invoice_line_ids
        if self.action == 'dispose':
            invoice_lines = self.env['account.move.line']
        # for asset in self.asset_ids:
        #     asset.set_to_close(invoice_line_id=invoice_lines,
        #                        date=self.invoice_id.invoice_date)

        invoice_line_id = invoice_lines
        disposal_date = self.invoice_id.invoice_date or fields.Date.today()
        journal_id = False
        for rec in self.asset_ids:
            if rec:
                journal_id = rec.journal_id.id
            if rec.state == 'draft':
                raise UserError(
                    _("You cannot sell asset with draft status, please confirm the asseet firstly"))

        # new raw query to create sell journal asset
        invoice_id = self.invoice_id.id or 0
        company_id = self.invoice_id.company_id.id or self.env.company.id
        prec = self.invoice_id.company_id.currency_id.decimal_places
        asset_no = [str(x.asset_no) for x in self.asset_ids]
        list_asset_no = '(%s)' % ', '.join(asset_no)
        asset_id = [str(x.id) for x in self.asset_ids]
        list_asset = '(%s)' % ', '.join(asset_id)
        print(list_asset, 'isi list_asset',invoice_id, company_id)
        sql = """             
                SELECT  aa.account_asset_id as account, sum(aa.original_value) as amount,
                        aa.company_id, aa.currency_id,aa.account_analytic_id 
                FROM  account_asset aa 
                WHERE aa.state = 'open'
                  AND aa.id in %s --id asset
                GROUP BY aa.account_asset_id, aa.company_id, aa.currency_id,aa.account_analytic_id 
                UNION --get accumulated depreciation account			
                SELECT  aa.account_depreciation_id,  
                        sum(aadl.amount) * -1 as depreciation_amount,
                        aa.company_id, aa.currency_id,aa.account_analytic_id 
                FROM account_asset aa 
                JOIN (SELECT aadl.asset_id,sum(aadl.amount) as amount
                      FROM account_asset_depreciation_line aadl 
                      WHERE aadl.move_posted_check = true
                      GROUP BY aadl.asset_id) aadl
                  ON aa.id = aadl.asset_id
                WHERE aa.state = 'open'
                  AND aa.id in %s --id asset
                GROUP BY aa.account_depreciation_id, aa.company_id, aa.currency_id, aa.account_analytic_id 
                UNION --get expense depreciation account
                SELECT case WHEN (sum(aa.original_value) - coalesce(sum(aadl.amount),0) - 
                                coalesce ((select sum(aml.price_unit)
                                FROM account_move am 
                                JOIN account_move_line aml 
                                  ON am.id = aml.move_id 
                                 AND am.company_id = aml.company_id 
                                WHERE exclude_from_invoice_tab = false 
                                  AND am.id = %s -- id invoice
                                group by aml.account_id, am.invoice_date),0)
                                ) < 0
                             THEN (SELECT gain_account_id FROM res_company WHERE id = %s)
                             WHEN (sum(aa.original_value) - coalesce(sum(aadl.amount),0) - 
                                coalesce ((select sum(aml.price_unit)
                                from account_move am 
                                join account_move_line aml 
                                ON am.id = aml.move_id 
                                and am.company_id = aml.company_id 
                                where exclude_from_invoice_tab = false 
                                and am.id = %s -- id invoice
                                group by aml.account_id, am.invoice_date),0)
                                ) > 0
                             THEN (SELECT loss_account_id FROM res_company WHERE id = %s)
                             ELSE null
                             END as gain_or_loss,
                        (sum(aa.original_value) - coalesce(sum(aadl.amount),0) - 
                                coalesce ((SELECT sum(aml.price_unit)
                                FROM account_move am 
                                JOIN account_move_line aml 
                                  ON am.id = aml.move_id 
                                 AND am.company_id = aml.company_id 
                                WHERE exclude_from_invoice_tab = false 
                                  AND am.id = %s -- id invoice
                                group by aml.account_id, am.invoice_date),0)
                        ) * -1 as rev_amount, aa.company_id, aa.currency_id,null::integer as account_analytic_id 
                FROM account_asset aa 
                LEFT JOIN (SELECT aadl.asset_id,sum(aadl.amount) as amount
                      FROM account_asset_depreciation_line aadl 
                      WHERE aadl.move_posted_check = true
                      GROUP BY aadl.asset_id) aadl
                  ON aa.id = aadl.asset_id
                WHERE aa.state = 'open'
                  AND aa.id in %s --id asset
                GROUP BY aa.company_id, aa.currency_id
                UNION -- get invoice account
                SELECT aml.account_id, sum(aml.price_unit) * -1,
                       am.company_id, am.currency_id,aml.analytic_account_id 
                FROM account_move am 
                JOIN account_move_line aml 
                  ON am.id = aml.move_id 
                 AND am.company_id = aml.company_id 
                WHERE exclude_from_invoice_tab = false 
                  AND am.id = %s --id_invoice
                GROUP BY aml.account_id, am.company_id, am.currency_id, aml.analytic_account_id 
            """ % (
            list_asset, list_asset, invoice_id, company_id, invoice_id, company_id, invoice_id, list_asset,
            invoice_id)
        self.env.cr.execute(sql)
        line_sell_asset = self.env.cr.dictfetchall()
        line_datas = []
        for x in line_sell_asset:
            datas = []
            for y in x:
                datas.append(x[y])
            line_datas.append(tuple(datas))

        def get_line(account, amount, company_id, currency_id, account_analytic_id):
            return (0, 0, {
                'name': 'sale asset',
                'account_id': account,
                'debit': 0.0 if float_compare(float(amount), 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(float(amount), 0.0, precision_digits=prec) > 0 else 0.0,
                'analytic_account_id': account_analytic_id,
                'analytic_tag_ids': False,
                'company_id': company_id,
                'currency_id': currency_id,
                'amount_currency': 1,
            })

        self.env['account.move'].create({
            'ref': list_asset_no + ': ' + (_('Disposal') if not invoice_line_id else _('Sale')),
            'asset_remaining_value': 0,
            'asset_depreciated_value': 0,
            'date': disposal_date,
            'journal_id': journal_id,
            'line_ids': [get_line(account, amount, company_id, currency_id, account_analytic_id) for
                         account, amount, company_id, currency_id, account_analytic_id in line_datas if account],
        })

        # set to close asset
        print('load proses 1')
        for asset in self.asset_ids:
            if asset and asset.state == 'close':
                asset.message_post(body=_('Asset sold or disposed. Accounting entry awaiting for validation.'), )
            print('load proses 2')
            if invoice_line_id and asset.children_ids.filtered(
                    lambda a: a.state in ('draft', 'open') or a.value_residual > 0):
                raise UserError(
                    _("You cannot automate the journal entry for an asset that has a running gross increase. Please use 'Dispose' on the increase(s)."))
            full_asset = asset + asset.children_ids
            print('load proses 3 ini bikin lama', full_asset)
            full_asset.write({'state': 'close'})
            print('load proses 1.5')
            len_disposal = len(asset.depreciation_move_ids.filtered(lambda x: x.state == 'draft'))
            print('load proses 1.8 ini yang bikin lama kedua',len_disposal)
            asset.total_duration_disposal = len_disposal
            print('load proses 2.2')
            asset.invoice_id = invoice_line_id.move_id.id
