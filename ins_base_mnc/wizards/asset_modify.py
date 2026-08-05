from odoo import api, fields, models


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    def _get_sql(self):
        """ helper function to get sql """
        sql_dict = {'company': self.company_id.id or self.env.company.id}
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
                AND sm.id = aml.stock_move_id
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
