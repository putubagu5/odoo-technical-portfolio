from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    name = fields.Char(default='/')
    company_id = fields.Many2one('res.company', 'Company',
                                 related='asset_id.company_id')
    model_id = fields.Many2one('account.asset', related='asset_id.model_id')
    is_added = fields.Boolean('Is Added', default=False)
    journal_id = fields.Many2one('account.journal', 'Journal')
    amount_residual = fields.Float('Current Value')
    amount_total = fields.Float('Amount Total')
    line_ids = fields.One2many('asset.modify.line', 'modify_id', 'Details')

    @api.model
    def create(self, vals):
        """ inherit function to assign method_number """
        if 'asset_id' in vals:
            asset = self.env['account.asset'].browse(vals['asset_id'])
            vals['method_number'] = asset.total_duration_disposal or vals.get('method_number', 1)
        res = super(AssetModify, self).create(vals)
        return res

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        """ onchange function to calculate amount total from lines """
        self.amount_total = sum(x.amount for x in self.line_ids.filtered(
            lambda x: x.selected))

    @api.onchange('amount_total', 'amount_residual')
    def _onchange_amount_total_residual(self):
        """ onchange function to get value_residual """
        self.value_residual = self.amount_total + self.amount_residual

    def _get_sql(self):
        """ helper function to get sql """
        sql_dict = {
            'company': self.company_id.id or self.env.company.id,
        }
        sql = """
            SELECT DISTINCT FALSE AS selected,
            pp.id AS product_id,
            sp.id AS picking_id,
            am.id AS invoice_id,
            aml.id AS invoice_line_id,
            aml.price_total AS amount
            FROM account_move_line aml
            JOIN product_product pp ON pp.id = aml.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_move_purchase_order_rel ampl ON ampl.account_move_id = am.id
            JOIN purchase_order po ON po.id = ampl.purchase_order_id
            JOIN purchase_order_stock_picking_rel popl ON po.id = popl.purchase_order_id
            JOIN stock_picking sp ON sp.id = popl.stock_picking_id
            JOIN stock_move sm ON sm.picking_id = sp.id
                AND sm.purchase_line_id = aml.purchase_line_id
            JOIN purchase_order_line pol ON pol.order_id = po.id
                AND pol.id = aml.purchase_line_id
            JOIN account_asset_product_template_rel aapl
                ON aapl.product_template_id = pt.id
            JOIN account_asset asset ON asset.id = aapl.account_asset_id
            LEFT JOIN generate_asset_move_rel gen ON gen.move_line_id = aml.id
            WHERE am.state = 'posted' AND pt.type = 'consu'
            AND gen.move_line_id IS NULL
            AND am.company_id = %(company)s AND po.company_id = %(company)s
            AND sp.company_id = %(company)s AND asset.company_id = %(company)s
        """ % (sql_dict)
        return sql

    def _get_modify_lines(self):
        """ helper function to get line records """
        lines = [(2, x.id) for x in self.line_ids]
        sql = self._get_sql()
        self.env.cr.execute(sql)
        result = self.env.cr.dictfetchall()
        for res in result:
            lines.append((0, 0, res))
        return lines

    def button_add(self):
        """ function to add lines and set reason """
        self.name = 'Add to Asset'
        self.is_added = True
        self.line_ids = self._get_modify_lines()
        self.amount_residual = self.asset_id.value_residual
        ctx = self.env.context.copy()
        return {
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asset.modify',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def modify(self):
        """ inherit function to add reverse journal """
        if self.is_added:
            if not any([x.selected for x in self.line_ids]) or not self.line_ids:
                raise ValidationError('Please select at least 1 line')

            # this process will not create another asset, but will create journal
            # which also will connect the selected lines to the origin_ids of the
            # selected asset

            lines = self.line_ids.filtered(lambda x: x.selected)

            # get the amount of selected lines
            amount = sum(x.amount for x in lines)

            # then update the original_value and origin_ids of the asset
            self.asset_id.write({
                'origin_ids': [(4, x.invoice_line_id.id) for x in lines],
            })

            # get the old picking if any
            old_picking = self.asset_id.picking_id

            # set new picking taken from the line, used to create journal first
            product = lines[0].product_id
            picking = lines[0].picking_id
            self.asset_id.picking_id = picking.id

            # using the existing asset, create another journal
            context = {
                'journal_id': self.journal_id.id,
                'product_id': product,
                'amount': amount,
            }
            self.asset_id.with_context(context).action_move_create()

            # then remember to reset the picking
            self.asset_id.picking_id = old_picking.id if old_picking else False

        # always call the parent function
        return super(AssetModify, self).modify()
