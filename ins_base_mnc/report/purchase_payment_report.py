from odoo import api, fields, models, tools


class PurchasePaymentReport(models.Model):
    _name = 'purchase.payment.report'
    _description = 'Purchase to Payment Report'
    _auto = False

    # purchase request related fields
    purchase_request_no = fields.Char('Purchase Request No.')
    purchase_request_description = fields.Text('Purchase Request Description')
    date_purchase_request_create = fields.Date('Purchase Request Create Date')
    product_id = fields.Many2one('product.product', 'Product')
    product_ref = fields.Char('Product Description')
    purchase_request_currency_id = fields.Many2one('res.currency',
                                                   'Purchase Request Currency')
    qty_purchase_request = fields.Float('Qty. Purchase Request')
    price = fields.Float('Unit Price (PR)')  # from original price
    rate = fields.Float('Rate')
    amount = fields.Float('Amount (PR)')  # qty * price
    user_id = fields.Many2one('res.users', 'Requested By')
    purchase_request_state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To be approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done'),
    ], 'Purchase Request State')
    analytic_account = fields.Char('Analytic Account')
    department = fields.Char('Department')
    date_pr_line_needed = fields.Date('Needed Date')
    manual_rate = fields.Float('Manual Currency Rate')
    pr_company_id = fields.Many2one('res.company', 'Company')

    # purchase order related fields
    purchase_order_no = fields.Char('Purchase Order No.')
    date_purchase_create = fields.Date('Purchase Create Date')
    purchase_description = fields.Text('Purchase Description')
    purchase_state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], 'Purchase Order State')
    purchase_currency_id = fields.Many2one('res.currency', 'Purchase Currency')
    purchase_uom_id = fields.Many2one('uom.uom', 'Purchase UoM')
    price_purchase = fields.Float('Unit Price (PO)')
    qty_purchase = fields.Float('Qty. Purchase')
    amount_purchase = fields.Float('Amount (PO)')
    purchase_representative = fields.Many2one('res.users', 'Purchase Representative')
    # purchase_account_id = fields.Many2one('account.account', 'Purchase Account')
    buyer_id = fields.Many2one('res.buyer', 'Buyer')
    purchase_partner_id = fields.Many2one('res.partner', 'Vendor')

    # picking related fields
    picking_no = fields.Char('Receipt Number')
    date_picking = fields.Date('Receipt Date')
    qty_picking = fields.Float('Qty. Receipt')
    picking_user_id = fields.Many2one('res.users', 'Created By')
    qty_delivered = fields.Float('Qty. Delivered')
    location_delivered = fields.Many2one('stock.location', 'Location Delivered')

    # invoice related fields
    invoice_no = fields.Char('Invoice No.')
    date_invoice = fields.Date('Invoice Date')
    qty_invoice = fields.Float('Qty. Invoice')

    # payment related fields
    payment_no = fields.Char('Payment No.')
    date_payment = fields.Date('Payment Date')
    payment_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], 'Payment State')
    is_matched = fields.Boolean('Is Matched With a Bank Statement')
    journal_id = fields.Many2one('account.journal', 'Bank Account')
    check_id = fields.Many2one('res.check.line', 'Check No')
    inv_ref = fields.Char('Reference No')

    def init(self):
        """ function to generate view """
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = """
            CREATE OR REPLACE VIEW %s AS (%s)
        """ % (self._table, self._query())
        self.env.cr.execute(sql)

    def _query(self):
        """ query constructor """
        return 'SELECT %s FROM %s GROUP BY %s' % (
            self._select(), self._from(), self._group_by())

    def _select(self):
        """ select query """
        sql = """
            DISTINCT
            row_number() OVER(ORDER BY aml.id) AS id,
            pr.name AS purchase_request_no,
            prl.name AS purchase_request_description,
            pr.date_start::timestamp::date AS date_purchase_request_create,
            pp.id AS product_id,
            pp.default_code AS product_ref,
            pr_cur.id AS purchase_request_currency_id,
            SUM(prl.product_qty) AS qty_purchase_request,
            SUM(prl.original_price) AS price,
            prl.actual_rate AS rate,
            SUM(prl.product_qty) * SUM(prl.original_price) AS amount,
            requestor.id AS user_id,
            pr.state AS purchase_request_state,
            prl_aaa.code AS analytic_account,
            prl_aaa.name AS department,
            prl.date_needed::timestamp::date AS date_pr_line_needed,
            prl.manual_currency_rate AS manual_rate,
            pr_company.id AS pr_company_id,
            po.name AS purchase_order_no,
            po.date_order AS date_purchase_create,
            po.po_description AS purchase_description,
            po.state AS purchase_state,
            po_cur.id AS purchase_currency_id,
            uom.id AS purchase_uom_id,
            SUM(pol.price_unit) AS price_purchase,
            SUM(pol.product_uom_qty) AS qty_purchase,
            SUM(pol.product_uom_qty) * SUM(pol.price_unit) AS amount_purchase,
            po_rep.id AS purchase_representative,
            buyer.id AS buyer_id,
            po_partner.id AS purchase_partner_id,
            sp.name AS picking_no,
            sp.date_done::timestamp::date AS date_picking,
            SUM(sm.product_uom_qty) AS qty_picking,
            SUM(sm.quantity_done) AS qty_delivered,
            sp_deliver_loc.id AS location_delivered,
            sp.user_id AS picking_user_id,
            am.payment_reference AS invoice_no,
            am.date AS date_invoice,
            SUM(aml.quantity) AS qty_invoice,
            pmt.multi_payment_reference AS payment_no,
            pmove.date AS date_payment,
            pmove.state AS payment_state,
            pmt.is_matched AS is_matched,
            jrnl.id AS journal_id,
            chckl.id AS check_id,
            pmt.inv_ref AS inv_ref
        """
        return sql

    def _from(self):
        """ from query """
        sql = """
            purchase_request_line prl
            LEFT JOIN purchase_request pr ON pr.id = prl.request_id
            LEFT JOIN purchase_request_purchase_order_line_rel prel
                ON prel.purchase_request_line_id = prl.id
            LEFT JOIN res_currency pr_cur ON pr_cur.id = prl.select_currency_id
            LEFT JOIN res_company pr_company ON pr_company.id = pr.company_id
            LEFT JOIN account_analytic_account prl_aaa ON prl_aaa.id = prl.analytic_account_id
            LEFT JOIN res_users requestor ON requestor.id = pr.requested_by
            LEFT JOIN purchase_order_line pol ON pol.id = prel.purchase_order_line_id
            LEFT JOIN purchase_order po ON po.id = pol.order_id
            LEFT JOIN res_users po_rep ON po_rep.id = po.user_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN res_currency po_cur ON po_cur.id = po.currency_id
            LEFT JOIN uom_uom uom ON uom.id = pol.product_uom
            LEFT JOIN res_partner po_partner ON po_partner.id = po.partner_id
            LEFT JOIN res_buyer buyer ON buyer.id = po.buyer_id
            LEFT JOIN purchase_order_stock_picking_rel popl ON popl.purchase_order_id = po.id
            LEFT JOIN stock_picking sp ON sp.id = popl.stock_picking_id
            LEFT JOIN stock_move sm ON sm.picking_id = sp.id
            LEFT JOIN stock_location sp_deliver_loc ON sp_deliver_loc.id = sp.location_dest_id
            LEFT JOIN res_users sp_user ON sp_user.id = COALESCE(sp.user_id, sp.create_uid)
            LEFT JOIN account_move_purchase_order_rel ampl ON ampl.purchase_order_id = po.id
            LEFT JOIN account_move_line aml ON aml.purchase_line_id = pol.id
                AND aml.purchase_line_id = sm.purchase_line_id AND aml.product_id = pp.id
                AND aml.stock_move_id = sm.id
            LEFT JOIN account_move am ON am.id = aml.move_id AND am.id = ampl.account_move_id
            LEFT JOIN account_move_line pml ON pml.move_id = am.id
                AND pml.full_reconcile_id IS NOT NULL
            lEFT JOIN account_move_line payment
                ON payment.full_reconcile_id = pml.full_reconcile_id AND payment.debit > 0
            LEFT JOIN account_move pmove ON pmove.id = payment.move_id
            LEFT JOIN account_payment pmt ON pmt.move_id = pmove.id
            LEFT JOIN account_journal jrnl ON jrnl.id = pmt.journal_id
            LEFT JOIN res_check_line chckl ON chckl.id = pmt.check_id
            LEFT JOIN miscellaneous_miscellaneous mm ON mm.applied_customer_move_id = am.id
            WHERE aml.exclude_from_invoice_tab IS FALSE
        """
        return sql

    def _group_by(self):
        """ group by query """
        sql = """
            pr.name,
            prl.name,
            pr.date_start,
            pp.id,
            pp.default_code,
            pr_cur.id,
            prl.actual_rate,
            requestor.id,
            pr.state,
            prl_aaa.code,
            prl_aaa.name,
            prl.date_needed,
            prl.manual_currency_rate,
            pr_company.id,
            po.name,
            po.date_order,
            po.po_description,
            pol.name,
            po.state,
            po_rep.id,
            po_cur.id,
            uom.id,
            buyer.id,
            po_partner.id,
            sp.name,
            sp.date_done,
            sp_deliver_loc.id,
            sp.user_id,
            am.payment_reference,
            am.date,
            pmt.multi_payment_reference,
            pmove.date,
            pmove.state,
            pmt.is_matched,
            jrnl.id,
            chckl.id,
            pmt.inv_ref,
            prl.id,
            aml.id
        """
        return sql
