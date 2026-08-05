from datetime import date
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetProgress(models.Model):
    _name = 'asset.progress'
    _description = 'Asset Progress'

    name = fields.Char('Name', copy=False)
    date = fields.Date('Date', default=date.today())
    asset_cost_progress_id = fields.Many2one('cip.configuration', 'CIP',
                                             ondelete='restrict')
    qty = fields.Float('Qty')
    model_id = fields.Many2one('account.asset', 'Asset Category')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    date_acquisition = fields.Date('Acquisition Date', default=date.today())
    journal_id = fields.Many2one('account.journal', 'Journal', check_company=True)
    account_id = fields.Many2one('account.account', 'Account')
    line_ids = fields.One2many('asset.progress.line', 'progress_id', 'Details')
    amount_total = fields.Float('Total', compute='_compute_total', store=True)
    account_src_id = fields.Many2one('account.account', 'Credit Account')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], 'State', default='draft')

    # @api.model
    # def default_get(self, fields):
    #     """ inherit function to add result as default lines """
    #     res = super(AssetProgress, self).default_get(fields)

    #     # find all invoice line -> invoice -> purchase -> picking -> stock move
    #     # filter: posted invoice, asset_cost_progress_id exists,
    #     # created_asset_ids is null
    #     lines = []
    #     pickings = []
    #     accounts = []

    #     company = self.company_id.id or self.env.user.company_id.id
    #     domain = [
    #         ('move_id.company_id', '=', company),
    #         ('move_id.state', '=', 'posted'),
    #         ('asset_cost_progress_id', '!=', False),
    #         ('created_asset_ids', '=', False),
    #         # ('product_id.asset_model_ids', '!=', False),
    #         ('purchase_line_id', '!=', False),
    #         ('purchase_line_id.move_ids', '!=', False),
    #     ]

    #     # get account.move.line, traceback to account.move, purchase.order
    #     # stock.picking
    #     move_lines = self.env['account.move.line'].sudo().search(domain)
    #     for ln in move_lines:
    #         picking = False
    #         move = ln.purchase_line_id.move_ids
    #         if move:
    #             picking = move[0].picking_id.id
    #             pickings.append(picking)
    #         data = {
    #             'product_id': ln.product_id.id,
    #             'move_line_id': ln.id,
    #             'move_id': ln.move_id.id,
    #             'picking_id': picking,
    #             'asset_cost_progress_id': ln.asset_cost_progress_id.id,
    #             'qty': ln.quantity,
    #             'price_unit': ln.price_unit,
    #             'price_subtotal': ln.price_total,
    #         }
    #         lines.append((0, 0, data))

    #     if pickings:
    #         for pc in pickings:
    #             picking = self.env['stock.picking'].sudo().browse(pc)
    #             move = picking.move_lines
    #             receipt = move.account_move_ids.filtered(
    #                 lambda x: not x.reversed_entry_id).line_ids.filtered(lambda x: x.debit)
    #             if receipt[:1]:
    #                 accounts.append(receipt[:1].account_id.id)

    #     # in the end check if the accounts' length, if > 1 then raise error
    #     if not accounts:
    #         msg = ''
    #         if not accounts:
    #             msg = 'No account found!'
    #         return {
    #             'warning': {
    #                 'title': 'Warning',
    #                 'message': msg,
    #             }
    #         }

    #     # nothing's wrong, proceed. Regardless what happened, take the first
    #     res['account_src_id'] = accounts[0]
    #     res['line_ids'] = lines
    #     return res

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """ onchange function to set account_asset_id based on model_id """
        self.ensure_one()
        if self.model_id:
            self.account_id = self.model_id.account_asset_id

    @api.onchange('asset_cost_progress_id')
    def _onchange_asset_cost_progress(self):
        """ onchange function to add lines and return model domain """
        self.ensure_one()
        if self.asset_cost_progress_id:
            cip = self.asset_cost_progress_id
            self.model_id = cip.model_id
            return {
                'domain': {
                    'model_id': [('id', '=', cip.model_id.id)],
                },
            }

    @api.depends('line_ids')
    def _compute_total(self):
        """ compute function to get amount_total from line_ids """
        for rec in self:
            rec.amount_total = sum(x.price_subtotal for x in rec.line_ids)

    def button_done(self):
        """ function to generate asset and journal items """
        for rec in self:
            lines = [x for x in rec.line_ids if x.selected]
            amt = sum(x.price_subtotal for x in lines)
            vals = {
                'name': rec.name,
                'qty': rec.qty,
                'model_id': rec.model_id.id,
                'acquisition_date': rec.date_acquisition,
                'date_received': rec.date,
                'original_value': amt,
                'asset_type': 'purchase',
                'state': 'draft',
                'origin_ids': [(4, x.move_line_id.id) for x in lines],
            }
            new_asset = self.env['account.asset'].new(vals)
            new_asset._onchange_model_id()  # to assign journal and accounts
            vals = new_asset._convert_to_write(new_asset._cache)
            asset = self.env['account.asset'].create(vals)
            context = {
                'name': rec.name,
                'journal_id': rec.journal_id.id,
                'debit_account_id': rec.account_id.id,
                'credit_account_id': rec.account_src_id.id,
            }
            asset.with_context(context).action_move_create()
            rec.write({'state': 'done'})
        return True
