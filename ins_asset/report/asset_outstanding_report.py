from odoo import api, fields, models, tools


class AssetOutstandingReport(models.Model):
    _name = 'asset.outstanding.report'
    _description = 'Asset Outstanding Report'
    _auto = False

    move_line_id = fields.Many2one('account.move.line', 'Invoice Line')
    move_id = fields.Many2one('account.move', 'Invoice No',
                              related='move_line_id.move_id')
    company_id = fields.Many2one('res.company', 'Company')
    partner_id = fields.Many2one('res.partner', 'Vendor',
                                 related='move_id.partner_id')
    date_invoice = fields.Date('Invoice Date', related='move_id.invoice_date')
    description = fields.Char('Description', related='move_line_id.name')
    picking_id = fields.Many2one('stock.picking', 'Picking No')
    product_id = fields.Many2one('product.product', 'Product',
                                 related='move_line_id.product_id')
    asset_cost_progress_id = fields.Many2one(
        'cip.configuration', 'CIP',
        related='move_line_id.asset_cost_progress_id')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        related='move_line_id.analytic_account_id')
    qty = fields.Float('Qty')
    amount = fields.Float('Amount')

    def init(self):
        """ function to generate view """
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = """
            CREATE OR REPLACE VIEW %s AS (%s)
        """ % (self._table, self._query())
        self.env.cr.execute(sql)

    def _query(self):
        """ query constructor """
        return 'SELECT %s FROM %s ' % (self._select(), self._from())

    def _select(self):
        """ select query """
        # Vendor, Invoice (Bill) Number, Bill Date, CIP in move line,
        # Picking Number, Product from move line, Description, Qty, Subtotal
        # rules: get invoice line that has not become asset, and invoice line
        # that has CIP OR has product with Asset model filled
        sql = """
            DISTINCT
            aml.id AS id,
            aml.id AS move_line_id,
            aml.company_id AS company_id,
            FIRST_VALUE(sp.id) OVER (
                PARTITION BY aml.id
                ORDER BY sp.id
                RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS picking_id,
            aml.quantity AS qty,
            aml.price_subtotal AS amount
        """
        return sql

    def _from(self):
        """ from query """
        sql = """
            account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            JOIN stock_move sm ON sm.purchase_line_id = aml.purchase_line_id
            JOIN stock_picking sp ON sp.id = sm.picking_id
            WHERE
            (
                (
                    am.state = 'posted' AND (
                        aml.id NOT IN (
                            SELECT move_line_id
                            FROM generate_asset_move_rel
                            WHERE move_line_id IS NOT NULL
                        )
                    ) AND aml.purchase_line_id IS NOT NULL
                ) AND (
                    aml.purchase_line_id IN (
                        SELECT pol.id
                        FROM purchase_order_line pol
                        WHERE (
                            pol.id IN (
                                SELECT purchase_line_id
                                FROM stock_move
                                WHERE purchase_line_id IS NOT NULL
                            )
                        )
                    )
                )
            ) AND (
                (
                    aml.product_id IN (
                        SELECT pp.id FROM product_product pp
                        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                        WHERE pt.id IN (
                            SELECT product_template_id
                            FROM account_asset_product_template_rel
                            WHERE product_template_id IS NOT NULL
                        )
                    )
                ) OR aml.asset_cost_progress_id IS NOT NULL
            )
        """
        return sql
