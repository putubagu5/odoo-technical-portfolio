from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WizardMassCipGenerate(models.TransientModel):
    _name = 'wizard.mass.cip.generate'
    _description = 'Mass CIP Generate'

    model_id = fields.Many2one('account.asset', 'Asset Model')
    company_id = fields.Many2one('res.company', 'Company',
                                 related='cip_id.company_id')
    journal_id = fields.Many2one('account.journal', 'Journal')
    type = fields.Selection([
        ('merge', 'Merge'),
        ('split', 'Split'),
    ], 'Transaction Type')
    name = fields.Char('Name')
    date_acquisition = fields.Date('Acquisition Date')
    cip_id = fields.Many2one('cip.configuration','CIP')
    amount_total = fields.Float('Total', default=0.0)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')
    line_ids = fields.One2many('wizard.mass.cip.detail', 'generate_id',
                               'Details')
    is_post_cip = fields.Boolean('Is Post Cip', default=False)
    
    # @api.onchange('cip_id')
    # def onchange_cip_id(self):
    #     lines = []

    #     domain = [
    #         ('move_id.company_id', '=', self.env.company.id),
    #         ('move_id.state', '=', 'posted'),
    #         ('asset_cost_progress_id', '!=', False),
    #         ('created_asset_ids', '=', False),
    #         ('product_id.type', '=', 'consu'),
    #         ('product_id.is_cost_progress', '=', True),
    #         ('purchase_line_id', '!=', False),
    #         ('purchase_line_id.move_ids', '!=', False),
    #     ]
    #     if self.type == 'split':
    #         domain += [('quantity', '>', 1)]

    #     # get account.move.line, traceback to account.move, purchase.order
    #     # stock.picking
    #     move_lines = self.env['account.move.line'].sudo().search(domain)
    #     if self.cip_id:
    #         for ln in move_lines:
    #             if ln.product_id.cip_id:
    #                 if ln.product_id.cip_id.id == self.cip_id.id:
    #                     picking = False
    #                     move = ln.purchase_line_id.move_ids
    #                     if move:
    #                         picking = move[0].picking_id.id
    #                     data = {
    #                         'selected': True,
    #                         'product_id': ln.product_id.id,
    #                         'purchase_id': ln.purchase_line_id.order_id.id,
    #                         'picking_id': picking,
    #                         'invoice_id': ln.move_id.id,
    #                         'invoice_line_id': ln.id,
    #                         'qty': ln.quantity,
    #                         'price_unit': ln.price_unit,
    #                         'amount': ln.price_total,
    #                         'purchase_line_number': ln.purchase_line_number,
    #                     }
    #                     lines.append((0, 0, data))
    #     else:
    #         for ln in move_lines:
    #             picking = False
    #             move = ln.purchase_line_id.move_ids
    #             if move:
    #                 picking = move[0].picking_id.id
    #             data = {
    #                 'selected': True,
    #                 'product_id': ln.product_id.id,
    #                 'purchase_id': ln.purchase_line_id.order_id.id,
    #                 'picking_id': picking,
    #                 'invoice_id': ln.move_id.id,
    #                 'invoice_line_id': ln.id,
    #                 'qty': ln.quantity,
    #                 'price_unit': ln.price_unit,
    #                 'amount': ln.price_total,
    #                 'purchase_line_number': ln.purchase_line_number,
    #             }
    #             lines.append((0, 0, data))
        
    #     if self.cip_id:
    #         self.line_ids = False
    #         self.line_ids = lines
    #     else:
    #         self.line_ids = False
    #         self.line_ids = lines

    def _get_default_lines(self, is_cip_post_journal = False):
        lines = []

        domain = [
            ('move_id.company_id', '=', self.env.company.id),
            ('move_id.state', '=', 'posted'),
            ('asset_cost_progress_id', '!=', False),
            ('created_asset_ids', '=', False),
            ('product_id.type', '=', 'consu'),
            ('product_id.is_cost_progress', '=', True),
            ('purchase_line_id', '!=', False),
            ('purchase_line_id.move_ids', '!=', False),
            ('is_cip_post_journal', '=', is_cip_post_journal),
        ]
        if self.type == 'split':
            domain += [('quantity', '>', 1)]

        # get account.move.line, traceback to account.move, purchase.order
        # stock.picking
        move_lines = self.env['account.move.line'].sudo().search(domain)
        for ln in move_lines:
            picking = False
            move = ln.purchase_line_id.move_ids
            if move:
                picking = move[0].picking_id.id
            data = {
                'selected': True,
                'product_id': ln.product_id.id,
                'purchase_id': ln.purchase_line_id.order_id.id,
                'picking_id': picking,
                'invoice_id': ln.move_id.id,
                'invoice_line_id': ln.id,
                'qty': ln.quantity,
                'price_unit': ln.price_unit,
                'amount': ln.price_total,
                'purchase_line_number': ln.purchase_line_number,
            }
            lines.append((0, 0, data))
        return lines

    @api.model
    def default_get(self, fields):
        """ inherit function to set line_ids """
        res = super(WizardMassCipGenerate, self).default_get(fields)

        lines = []

        domain = [
            ('move_id.company_id', '=', self.env.company.id),
            ('move_id.state', '=', 'posted'),
            ('asset_cost_progress_id', '!=', False),
            ('created_asset_ids', '=', False),
            ('product_id.type', '=', 'consu'),
            ('product_id.is_cost_progress', '=', True),
            ('purchase_line_id', '!=', False),
            ('purchase_line_id.move_ids', '!=', False),
            ('is_cip_post_journal', '=', False),
        ]
        if self.type == 'split':
            domain += [('quantity', '>', 1)]

        # get account.move.line, traceback to account.move, purchase.order
        # stock.picking
        move_lines = self.env['account.move.line'].sudo().search(domain)
        for ln in move_lines:
            picking = False
            move = ln.purchase_line_id.move_ids
            if move:
                picking = move[0].picking_id.id
            data = {
                'selected': True,
                'product_id': ln.product_id.id,
                'purchase_id': ln.purchase_line_id.order_id.id,
                'picking_id': picking,
                'invoice_id': ln.move_id.id,
                'invoice_line_id': ln.id,
                'qty': ln.quantity,
                'price_unit': ln.price_unit,
                'amount': ln.price_total,
                'purchase_line_number': ln.purchase_line_number,
            }
            lines.append((0, 0, data))

        res['line_ids'] = lines

        # get account.journal default
        journal_id = self.env['account.journal'].search([('type','=','general')],limit=1)
        res['journal_id'] = journal_id.id

        return res

    def button_generate(self):
        # self._check_lines()  # check first
        account_move = self.env['account.move']
        line_ids = []
        cost = 0
        details = self.line_ids.filtered(lambda x: x.selected)
        for detail in details.mapped('invoice_line_id').filtered(lambda x: x.debit > 0):
            cost += detail.debit
            line_ids.append((0,0, {
                'account_id': detail.product_id.property_account_expense_id.id,
                'name': detail.name,
                'analytic_account_id': detail.analytic_account_id.id,
                'credit': detail.debit,
                'debit': 0,
            }))
            detail.write({'is_cip_post_journal': True})
        line_ids.append((0,0, {
            'account_id': self.cip_id.account_id.id,
            'name': '',
            'analytic_account_id': self.analytic_account_id.id,
            'credit': 0,
            'debit': cost,
            }))
        account_move = account_move.create({
                                    # 'partner_id':partner_ids[0].id,
                                    'journal_id':self.journal_id.id,
                                    'user_id':self._uid,
                                    # 'move_type':'out_invoice',
                                    'invoice_date' : self.date_acquisition,
                                    'line_ids': line_ids
                                    })
        return True

    def button_generate_cip(self):
        progress = self.env['asset.progress']
        line_ids = []
        details = self.line_ids.filtered(lambda x: x.selected)
        for detail in details:
            line_ids.append((0, 0, {
                'move_id': detail.invoice_id.id,
                'move_line_id': detail.invoice_line_id.id,
                'picking_id': detail.picking_id.id,
                'product_id': detail.product_id.id,
                'asset_cost_progress_id': self.cip_id.id,
                'qty': detail.qty,
                'price_unit': detail.price_unit,
                'price_subtotal': detail.qty * detail.price_unit,
            }))
        vals = {
            'name': self.name,
            'date': self.date_acquisition,
            'asset_cost_progress_id': self.cip_id.id,
            'qty': self.amount_total,
            'model_id': self.model_id.id,
            'date_acquisition': self.date_acquisition,
            'journal_id': self.journal_id.id,
            'account_src_id': self.cip_id.account_id.id,
            'account_id': self.model_id.account_asset_id.id,
            'state': 'draft',
            'line_ids': line_ids
        }
        progress.create(vals)
        return True
    
    @api.onchange('cip_id')
    def _onchange_cip_id(self):
        for rec in self:
            if not rec.line_ids:
                rec.line_ids = False
                if rec.is_post_cip:
                    rec.line_ids = self._get_default_lines(True)
                    if rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.model_id == rec.model_id))
                    if rec.cip_id and not rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.cip_id == rec.cip_id)
                    if not rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.model_id == rec.model_id)
                else:
                    rec.line_ids = self._get_default_lines()
                    if rec.cip_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.cip_id == rec.cip_id)
            else:
                rec.line_ids = False
                if rec.is_post_cip:
                    rec.line_ids = self._get_default_lines(True)
                    if rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.model_id == rec.model_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                    if rec.cip_id and not rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                    if not rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.model_id == rec.model_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                else:
                    rec.line_ids = self._get_default_lines()
                    if rec.cip_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and  (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
    
    @api.onchange('is_post_cip')
    def _onchange_is_post_cip(self):
        for rec in self:
            if not rec.line_ids:
                rec.line_ids = False
                if rec.is_post_cip:
                    rec.line_ids = self._get_default_lines(True)
                    if rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.model_id == rec.model_id))
                    if rec.cip_id and not rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.cip_id == rec.cip_id)
                    if not rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.model_id == rec.model_id)
                else:
                    rec.line_ids = self._get_default_lines()
                    if rec.cip_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.cip_id == rec.cip_id)
            else:
                rec.line_ids = False
                if rec.is_post_cip:
                    rec.line_ids = self._get_default_lines(True)
                    if rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.model_id == rec.model_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                    if rec.cip_id and not rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                    if not rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.model_id == rec.model_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                else:
                    rec.line_ids = self._get_default_lines()
                    if rec.cip_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and  (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
    
    @api.onchange('model_id')
    def _onchange_model_id(self):
        for rec in self:
            if not rec.line_ids:
                rec.line_ids = False
                if rec.is_post_cip:
                    rec.line_ids = self._get_default_lines(True)
                    if rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.model_id == rec.model_id))
                    if rec.cip_id and not rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.cip_id == rec.cip_id)
                    if not rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.model_id == rec.model_id)
                else:
                    rec.line_ids = self._get_default_lines()
                    if rec.cip_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: line.cip_id == rec.cip_id)
            else:
                rec.line_ids = False
                if rec.is_post_cip:
                    rec.line_ids = self._get_default_lines(True)
                    if rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.model_id == rec.model_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                    if rec.cip_id and not rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                    if not rec.cip_id and rec.model_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.model_id == rec.model_id) and (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
                else:
                    rec.line_ids = self._get_default_lines()
                    if rec.cip_id:
                        rec.line_ids = rec.line_ids.filtered(lambda line: (line.cip_id == rec.cip_id) and  (line.invoice_line_id.is_cip_post_journal == rec.is_post_cip))
    
    @api.onchange('is_post_cip')
    def _onchange_is_post_cip(self):
        for rec in self:
            if rec.is_post_cip:
                rec.model_id = False
                rec.company_id = False
                rec.cip_id = False
                rec.line_ids = False
                rec.line_ids = self._get_default_lines(True)
            else:
                rec.model_id = False
                rec.company_id = False
                rec.cip_id = False
                rec.line_ids = False
                rec.line_ids = self._get_default_lines()
