from odoo import api, fields, models, _, tools
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)


class r12_po_receives(models.Model):
    _name = 'r12.po.receives'
    _description = 'R12 PO Receives - Odoo Staging Table - prepared for ATIS - Oracle Staging'

    sourcedata = fields.Char(string="SOURCEDATA")
    receive_date = fields.Datetime(string="RECEIVE_DATE")
    po_date = fields.Datetime(string="PO_DATE")
    po_rate_date = fields.Datetime(string="PO_RATE_DATE")
    pr_date = fields.Datetime(string="PR_DATE")
    pr_rate_date = fields.Datetime(string="PR_RATE_DATE")
    po_header_id = fields.Integer(string="PO_HEADER_ID")
    po_line_id = fields.Integer(string="PO_LINE_ID")
    po_line = fields.Integer(string="PO_LINE")
    pr_amount_idr = fields.Float(string="PR_AMOUNT_IDR")
    buyer_id = fields.Integer(string="BUYER_ID")
    deliver_to_person_id = fields.Integer(string="DELIVER_TO_PERSON_ID")
    requestor_id = fields.Integer(string="REQUESTOR_ID")
    shipment_header_id = fields.Integer(string="SHIPMENT_HEADER_ID")
    vendor_id = fields.Integer(string="VENDOR_ID")
    vendor_site_id = fields.Integer(string="VENDOR_SITE_ID")
    line_num = fields.Integer(string="LINE_NUM")
    primary_quantity = fields.Float(string="PRIMARY_QUANTITY")
    qty_receive = fields.Float(string="QTY_RECEIVE")
    rr_qty = fields.Float(string="RR_QTY")
    inv_org_id = fields.Integer(string="INV_ORG_ID")
    org_id = fields.Integer(string="ORG_ID")
    receive_item_id = fields.Integer(string="RECEIVE_ITEM_ID")
    ship_to_location_id = fields.Integer(string="SHIP_TO_LOCATION_ID")
    employee_id_receiver = fields.Char(string="EMPLOYEE_ID_RECEIVER")
    deliver_to_location_id = fields.Integer(string="DELIVER_TO_LOCATION_ID")
    po_rate = fields.Float(string="PO_RATE")
    po_item_id = fields.Integer(string="PO_ITEM_ID")
    po_qty = fields.Float(string="PO_QTY")
    unit_price = fields.Float(string="UNIT_PRICE")
    po_amount_idr = fields.Float(string="PO_AMOUNT_IDR")
    requisition_header_id = fields.Integer(string="REQUISITION_HEADER_ID")
    requisition_line_id = fields.Integer(string="REQUISITION_LINE_ID")
    pr_line_num = fields.Integer(string="PR_LINE_NUM")
    pr_qty = fields.Float(string="PR_QTY")
    pr_unit_price = fields.Float(string="PR_UNIT_PRICE")
    pr_rates = fields.Float(string="PR_RATES")
    po_currency = fields.Char(string="PO_CURRENCY")
    pr_currency = fields.Char(string="PR_CURRENCY")
    po = fields.Char(string="PO#")
    pr = fields.Char(string="PR#")
    vendor_name = fields.Char(string="VENDOR_NAME")
    receive_item_name = fields.Char(string="RECEIVE_ITEM_NAME")
    receive_item_desc = fields.Char(string="RECEIVE_ITEM_DESC")
    ship_to_location_desc = fields.Char(string="SHIP_TO_LOCATION_DESC")
    receiver_name = fields.Char(string="RECEIVER_NAME")
    deliver_to_location_desc = fields.Char(string="DELIVER_TO_LOCATION_DESC")
    deliver_to_person = fields.Char(string="DELIVER_TO_PERSON")
    buyer_name = fields.Char(string="BUYER_NAME")
    po_description = fields.Char(string="PO_DESCRIPTION")
    po_item_description = fields.Char(string="PO_ITEM_DESCRIPTION")
    pr_description = fields.Char(string="PR_DESCRIPTION")
    requestor_name = fields.Char(string="REQUESTOR_NAME")
    destination_type_code = fields.Char(string="DESTINATION_TYPE_CODE")
    po_status = fields.Char(string="PO_STATUS")
    pr_status = fields.Char(string="PR_STATUS")
    po_uom = fields.Char(string="PO_UOM")
    rr_uom = fields.Char(string="RR_UOM")
    pr_uom = fields.Char(string="PR_UOM")
    receipt_num = fields.Char(string="RECEIPT_NUM")
    receive_item_code = fields.Char(string="RECEIVE_ITEM_CODE")
    rr_uom_desc = fields.Char(string="RR_UOM_DESC")
    po_uom_desc = fields.Char(string="PO_UOM_DESC")
    pr_uom_desc = fields.Char(string="PR_UOM_DESC")
    ship_to_location = fields.Char(string="SHIP_TO_LOCATION")
    deliver_to_location = fields.Char(string="DELIVER_TO_LOCATION")
    #
    sync_log_id = fields.Many2one('mnc.sync.logger', String="Sync Logger", required=True)
    curr_steps = fields.Integer(string="Current Steps")
    total_steps = fields.Integer(string="Total Steps")

    def get_ora_po_state(self, state):
        res = False

        if state == 'draft':
            res = 'INCOMPLETE'
        elif state == 'to approve':
            res = 'IN PROCESS'
        elif state == 'to approve':
            res = 'IN PROCESS'
        elif state == 'cancel':
            res = 'REJECTED'
        elif state == 'done':
            res = 'APPROVED'

        # purchase ini harusnya apa ya . ini masih SALAH
        elif state == 'purchase':
            res = 'APPROVED'

        return res

    def get_ora_pr_state(self, state):
        res = False

        if state == 'draft':
            res = 'INCOMPLETE'
        elif state == 'to_approve':
            res = 'IN PROCESS'
        elif state == 'returned':
            res = 'RETURNED'
        elif state == 'rejected':
            res = 'REJECTED'
        elif state == 'approved':
            res = 'APPROVED'

        return res

    def fill_odoo_staging_table(self):
        # _logger.info('posisi di : fill_odoo_staging_table x')
        # _logger.info(self._name)

        fetch_cnt = 0
        msl_id = self.env['mnc.sync.logger'].create({
            'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'model_name': self._name,
            'step01_activity': 'Fill Odoo Staging Table',
            'step01_desc': 'Fill Odoo Staging Table',
            'step01_source': 'odoo',
            'step01_target': 'odoo_stg',
            'step01_start_time': datetime.now(),
            'step01_end_time': False,
            'step01_caller': self._name + '.fill_odoo_staging_table',
            'step01_count': 0,
            'curr_steps': 1,
            'total_steps': 3,
        })

        # _logger.info('posisi di : fill_odoo_staging_table x')
        stock_pick_ids = self.env['stock.picking'].search([('state', '=', 'done')])

        # PO
        po_ids = self.env['purchase.order'].search([
            ('name', '=', 'P00006'),
        ])

        vals = {}
        for po in po_ids:
            # _logger.info('siap')
            # _logger.info(po.state)

            # init data
            sourcedata = 'O14'
            receive_date = False
            po_date = po.date_order
            po_rate_date = po.date_order
            pr_date = False
            pr_rate_date = False
            po_header_id = po.id
            po_line_id = False
            po_line = False
            pr_amount_idr = False
            buyer_id = po.buyer_id.id
            deliver_to_person_id = False
            requestor_id = False
            shipment_header_id = False
            vendor_id = False
            vendor_site_id = False
            line_num = False
            primary_quantity = False
            qty_receive = False
            rr_qty = False
            # inv_org_id = po.company_id.id
            inv_org_id = self.get_inv_org_id(po.company_id.id)
            org_id = po.company_id.org_id
            receive_item_id = False
            ship_to_location_id = False
            employee_id_receiver = False
            deliver_to_location_id = False
            po_rate = po.actual_rate
            po_item_id = False
            po_qty = False
            unit_price = False
            po_amount_idr = False
            requisition_header_id = False
            requisition_line_id = False
            pr_line_num = False
            pr_qty = False
            pr_unit_price = False
            pr_rates = False
            po_currency = po.currency_id.name
            pr_currency = False
            po_no = po.name
            pr_no = False
            vendor_name = False
            receive_item_name = False
            receive_item_desc = False
            ship_to_location_desc = False
            receiver_name = False
            deliver_to_location_desc = False
            deliver_to_person = False
            buyer_name = po.buyer_id.name
            po_description = po.po_description
            po_item_description = False
            pr_description = False
            requestor_name = False
            destination_type_code = False
            po_status = self.get_ora_po_state(po.state)
            pr_status = False
            po_uom = False
            rr_uom = False
            pr_uom = False
            receipt_num = False
            receive_item_code = False
            rr_uom_desc = False
            po_uom_desc = False
            pr_uom_desc = False
            ship_to_location = False
            deliver_to_location = False

            # _logger.info('po head 01')

            for sp in po.picking_ids:
                shipment_header_id = sp.id
                receipt_num = sp.name
                receive_date = sp.date_done
                vendor_id = sp.partner_id.id
                vendor_name = sp.partner_id.name
                ship_to_location_id = sp.location_dest_id.id
                ship_to_location = sp.location_dest_id.name
                ship_to_location_desc = sp.location_dest_id.complete_name
                deliver_to_location_id = sp.location_dest_id.id
                deliver_to_location = sp.location_dest_id.name
                deliver_to_location_desc = sp.location_dest_id.complete_name

                if sp.id:
                    destination_type_code = 'RECEIVING'
                else:
                    destination_type_code = ''

                # _logger.info('sp 01')

                for vs in sp.partner_id.site_ids:
                    # harusnya ambil baris teratas saja
                    vendor_site_id = vs.id

                    # _logger.info('vs 01')

            ###### P R #########

            # PR
            po_origin = []
            if po.origin:
                many_po_origin = po.origin.split(",")
                _logger.info("saya disini many_po_origin")
                _logger.info(many_po_origin)

                for x in many_po_origin:
                    _logger.info("masuk di x")
                    _logger.info(x)
                    po_origin.append(x)
                _logger.info("po_origin")
                _logger.info(po_origin)

            pr_ids = self.env['purchase.request'].search([
                ('name', 'in', po_origin),
            ])
            _logger.info("lagi di pr_ids tempat 1")
            _logger.info(pr_ids)

            for pr in pr_ids:
                employee_id_receiver = pr.requested_by.id
                receiver_name = pr.requested_by.name
                deliver_to_person_id = pr.requested_by.id
                deliver_to_person = pr.requested_by.name
                requisition_header_id = pr.id
                pr_no = pr.name
                pr_status = self.get_ora_pr_state(pr.state)
                pr_date = pr.date_start
                pr_description = pr.description
                requestor_id = pr.requested_by.id
                requestor_name = pr.requested_by.name
                # _logger.info(pr.requested_by)
                # _logger.info(pr.requested_by.name)
                # _logger.info(pr.id)
                # _logger.info(pr.name)

                # _logger.info('pr 01')

            ####### P R ########

            # PO Line

            for pol in po.order_line:
                primary_quantity = pol.product_qty
                qty_receive = pol.qty_received
                po_line_id = pol.id
                po_line = pol.line_number
                po_item_id = pol.product_id.id
                po_item_description = pol.name
                po_uom = pol.product_id.uom_id.name[0:15]
                po_uom_desc = pol.product_id.uom_id.name
                unit_price = pol.price_unit
                po_amount_idr = pol.price_subtotal

                # _logger.info(pol.product_qty)
                # _logger.info(pol.line_number)
                # _logger.info('sini')

                # PR Line
                if requisition_header_id:
                    prl_ids = self.env['purchase.request.line'].search([
                        ('request_id', '=', requisition_header_id),
                        ('line_number', '=', pol.line_number),
                    ])

                    # _logger.info(prl_ids)

                    # _logger.info('pr 01')

                    for prl in prl_ids:
                        requisition_line_id = prl.id
                        pr_line_num = prl.line_number
                        pr_qty = prl.product_qty
                        pr_uom = prl.product_id.uom_id.id
                        pr_uom_desc = prl.product_id.uom_id.name
                        pr_unit_price = prl.original_price
                        pr_currency = prl.select_currency_id.name
                        pr_rates = prl.actual_rate
                        pr_rate_date = prl.date_rate
                        pr_amount_idr = prl.estimated_cost

                        # _logger.info('prl 01')

                for sm in sp.move_lines:
                    if sm.purchase_line_number == pol.line_number:
                        line_num = sm.purchase_line_number
                        rr_qty = sm.quantity_done
                        rr_uom = sm.product_uom.name[0:15]
                        rr_uom_desc = sm.product_uom.name
                        receive_item_id = sm.product_id.id
                        receive_item_code = sm.product_id.code
                        receive_item_name = sm.product_id.product_tmpl_id.name
                        receive_item_desc = sm.description_picking

                        # _logger.info(sm.purchase_line_number)
                        # _logger.info('sm 01')

                # data diinsert ketika pol
                vals = {
                    'sourcedata': sourcedata,
                    'shipment_header_id': shipment_header_id,
                    'receipt_num': receipt_num,
                    'receive_date': receive_date,
                    'vendor_id': vendor_id,
                    'vendor_name': vendor_name,
                    'vendor_site_id': vendor_site_id,
                    'line_num': line_num,
                    'destination_type_code': destination_type_code,
                    'primary_quantity': primary_quantity,
                    'qty_receive': qty_receive,
                    'rr_qty': rr_qty,
                    'rr_uom': rr_uom,
                    'rr_uom_desc': rr_uom_desc,
                    'inv_org_id': inv_org_id,
                    'org_id': org_id,
                    'receive_item_id': receive_item_id,
                    'receive_item_code': receive_item_code,
                    'receive_item_name': receive_item_name,
                    'receive_item_desc': receive_item_desc,
                    'ship_to_location_id': ship_to_location_id,
                    'ship_to_location': ship_to_location,
                    'ship_to_location_desc': ship_to_location_desc,
                    'employee_id_receiver': employee_id_receiver,
                    'receiver_name': receiver_name,
                    'deliver_to_location_id': deliver_to_location_id,
                    'deliver_to_location': deliver_to_location,
                    'deliver_to_location_desc': deliver_to_location_desc,
                    'deliver_to_person_id': deliver_to_person_id,
                    'deliver_to_person': deliver_to_person,
                    'po_header_id': po_header_id,
                    # 'po': po,
                    'po': po_no,
                    'po_status': po_status,
                    'buyer_id': buyer_id or None,
                    'buyer_name': buyer_name or None,
                    'po_date': po_date,
                    'po_description': po_description,
                    'po_currency': po_currency,
                    'po_rate': po_rate,
                    'po_rate_date': po_rate_date,
                    'po_line_id': po_line_id,
                    'po_line': po_line,
                    'po_item_id': po_item_id,
                    'po_item_description': po_item_description,
                    'po_qty': po_qty,
                    'po_uom': po_uom,
                    'po_uom_desc': po_uom_desc,
                    'unit_price': unit_price,
                    'po_amount_idr': po_amount_idr,
                    'requisition_header_id': requisition_header_id,
                    # 'pr': pr,
                    'pr': pr_no,
                    'pr_status': pr_status,
                    'pr_date': pr_date,
                    'pr_description': pr_description,
                    'requestor_id': requestor_id,
                    'requestor_name': requestor_name,
                    'requisition_line_id': requisition_line_id,
                    'pr_line_num': pr_line_num,
                    'pr_qty': pr_qty,
                    'pr_uom': pr_uom,
                    'pr_uom_desc': pr_uom_desc,
                    'pr_unit_price': pr_unit_price,
                    'pr_currency': pr_currency,
                    'pr_rates': pr_rates,
                    'pr_rate_date': pr_rate_date,
                    'pr_amount_idr': pr_amount_idr,
                    'sync_log_id': msl_id.id
                }

                fetch_cnt += 1

                # _logger.info(vals)

                self.env['r12.po.receives'].create(vals)

        #

        msl_ids = self.env['mnc.sync.logger'].search([("id", "=", msl_id.id)])
        for msl_data in msl_ids:
            msl_data.write({'step01_end_time': datetime.now(),
                            'step01_count': fetch_cnt,
                            })

        # _logger.info('posisi di : fill_odoo_staging_table')

        return msl_id

    def push_data_to_atis(self, sync_log_id):
        # _logger.info('posisi di push_data_to_atis')
        # _logger.info(sync_log_id)

        log_ids = self.env['mnc.sync.logger'].search([
            ('id', '=', sync_log_id),
        ])

        # _logger.info(log_ids)

        for log_id in log_ids:
            log_id.write({
                'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
                'model_name': self._name,
                'step02_activity': 'Push Data to Atis',
                'step02_desc': 'Push Data from odoo staging to oracle staging ATIS',
                'step02_source': 'odoo_stg',
                'step02_target': 'ora_stg',
                'step02_start_time': datetime.now(),
                'step02_end_time': False,
                'step02_caller': self._name + '.push_data_to_atis',
                'step02_count': 0,
                'curr_steps': 2,
                #
            })

            # _logger.info('cek poin sync log id xxs')
            # _logger.info(sync_log_id)
            # _logger.info(log_id.id)

            line_ids = self.env['r12.po.receives'].search([
                ('sync_log_id', '=', log_id.id),
            ])

            # _logger.info('di push data to oracle staging atis')
            # _logger.info(line_ids)

            sent_cnt = send_cnt = 0

            import cx_Oracle
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="10.3.99.165:1521/xe")
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="localhost:1521/xe")
            # TODO: Buatkan Modul untuk menyimpan data user, password, dsn ini. Saat ini username dan password masih dalam kondisi Hard Code.

            ora_atis_user = self.env['mnc.token.management'].get_ora_atis_user('r12.po.receives')
            if not ora_atis_user:
                ora_atis_user = "atisappsr12dev"
                _logger.info('default ora_atis_pass default')

            ora_atis_pass = self.env['mnc.token.management'].get_ora_atis_pass('r12.po.receives')
            if not ora_atis_pass:
                ora_atis_pass = "atisappsr12dev"
                _logger.info('default ora_atis_pass default')

            ora_atis_dsn = self.env['mnc.token.management'].get_ora_atis_dsn('r12.po.receives')
            if not ora_atis_dsn:
                ora_atis_dsn = "arjuna.mncgroup.com:1523/rcti"
                _logger.info('default ora_atis_pass default')

            _logger.info('get data from param - done')
            # _logger.info(ora_atis_user)
            # _logger.info(ora_atis_pass)
            # _logger.info(ora_atis_dsn)

            con = cx_Oracle.connect(user=ora_atis_user, password=ora_atis_pass, dsn=ora_atis_dsn)
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="localhost:1521/xe")
            cur = con.cursor()

            for line in line_ids:
                # _logger.info('di line nya BDR 554')
                # _logger.info(line)

                # _logger.info(line.sourcedata or None)
                # _logger.info(line.receive_date or None)
                # _logger.info(line.po_date or None)
                # _logger.info(line.po_rate_date or None)
                # _logger.info(line.pr_date or None)
                # _logger.info(line.pr_rate_date or None)
                # _logger.info(line.po_header_id or None)
                # _logger.info(line.po_line_id or None)
                # _logger.info(line.po_line or None)
                # _logger.info(line.pr_amount_idr or None)
                # _logger.info(line.buyer_id or None)
                # _logger.info(line.deliver_to_person_id or None)
                # _logger.info(line.requestor_id or None)
                # _logger.info(line.shipment_header_id or None)
                # _logger.info(line.vendor_id or None)
                # _logger.info(line.vendor_site_id or None)
                # _logger.info(line.line_num or None)
                # _logger.info(line.primary_quantity or None)
                # _logger.info(line.qty_receive or None)
                # _logger.info(line.rr_qty or None)
                # _logger.info(line.inv_org_id or None)
                # _logger.info(line.org_id or None)
                # _logger.info(line.receive_item_id or None)
                # _logger.info(line.ship_to_location_id or None)
                # _logger.info(line.employee_id_receiver or None)
                # _logger.info(line.deliver_to_location_id or None)
                # _logger.info(line.po_rate or None)
                # _logger.info(line.po_item_id or None)
                # _logger.info(line.po_qty or None)
                # _logger.info(line.unit_price or None)
                # _logger.info(line.po_amount_idr or None)
                # _logger.info(line.requisition_header_id or None)
                # _logger.info(line.requisition_line_id or None)
                # _logger.info(line.pr_line_num or None)
                # _logger.info(line.pr_qty or None)
                # _logger.info(line.pr_unit_price or None)
                # _logger.info(line.pr_rates or None)
                # _logger.info(line.po_currency or None)
                # _logger.info(line.pr_currency or None)
                # _logger.info(line.po or None)
                # _logger.info(line.pr or None)
                # _logger.info(line.vendor_name or None)
                # _logger.info(line.receive_item_name or None)
                # _logger.info(line.receive_item_desc or None)
                # _logger.info(line.ship_to_location_desc or None)
                # _logger.info(line.receiver_name or None)
                # _logger.info(line.deliver_to_location_desc or None)
                # _logger.info(line.deliver_to_person or None)
                # _logger.info(line.buyer_name or None)
                # _logger.info(line.po_description or None)
                # _logger.info(line.po_item_description or None)
                # _logger.info(line.pr_description or None)
                # _logger.info(line.requestor_name or None)
                # _logger.info(line.destination_type_code or None)
                # _logger.info(line.po_status or None)
                # _logger.info(line.pr_status or None)
                # _logger.info(line.po_uom or None)
                # _logger.info(line.rr_uom or None)
                # _logger.info(line.pr_uom or None)
                # _logger.info(line.receipt_num or None)
                # _logger.info(line.receive_item_code or None)
                # _logger.info(line.rr_uom_desc or None)
                # _logger.info(line.po_uom_desc or None)
                # _logger.info(line.pr_uom_desc or None)
                # _logger.info(line.ship_to_location or None)
                # _logger.info(line.deliver_to_location or None)

                line.curr_steps = 2

                # line.state = 'send'
                send_cnt += 1

                sql = "insert into R12_PO_RECEIVES ( SOURCEDATA ,RECEIVE_DATE ,PO_DATE ,PO_RATE_DATE ,PR_DATE ,PR_RATE_DATE ,PO_HEADER_ID ,PO_LINE_ID ,PO_LINE ,PR_AMOUNT_IDR ,BUYER_ID ,DELIVER_TO_PERSON_ID ,REQUESTOR_ID ,SHIPMENT_HEADER_ID ,VENDOR_ID ,VENDOR_SITE_ID ,LINE_NUM ,PRIMARY_QUANTITY ,QTY_RECEIVE ,RR_QTY ,INV_ORG_ID ,ORG_ID ,RECEIVE_ITEM_ID ,SHIP_TO_LOCATION_ID ,EMPLOYEE_ID_RECEIVER ,DELIVER_TO_LOCATION_ID ,PO_RATE ,PO_ITEM_ID ,PO_QTY ,UNIT_PRICE ,PO_AMOUNT_IDR ,REQUISITION_HEADER_ID ,REQUISITION_LINE_ID ,PR_LINE_NUM ,PR_QTY ,PR_UNIT_PRICE ,PR_RATES ,PO_CURRENCY ,PR_CURRENCY ,PO# ,PR# ,VENDOR_NAME ,RECEIVE_ITEM_NAME ,RECEIVE_ITEM_DESC ,SHIP_TO_LOCATION_DESC ,RECEIVER_NAME ,DELIVER_TO_LOCATION_DESC ,DELIVER_TO_PERSON ,BUYER_NAME ,PO_DESCRIPTION ,PO_ITEM_DESCRIPTION ,PR_DESCRIPTION ,REQUESTOR_NAME ,DESTINATION_TYPE_CODE ,PO_STATUS ,PR_STATUS ,PO_UOM ,RR_UOM ,PR_UOM ,RECEIPT_NUM ,RECEIVE_ITEM_CODE ,RR_UOM_DESC ,PO_UOM_DESC ,PR_UOM_DESC ,SHIP_TO_LOCATION ,DELIVER_TO_LOCATION, ODOO_LOG_ID ) " \
                      "values ( :sourcedata ,:receive_date ,:po_date ,:po_rate_date ,:pr_date ,:pr_rate_date ,:po_header_id ,:po_line_id ,:po_line ,:pr_amount_idr ,:buyer_id ,:deliver_to_person_id ,:requestor_id ,:shipment_header_id ,:vendor_id ,:vendor_site_id ,:line_num ,:primary_quantity ,:qty_receive ,:rr_qty ,:inv_org_id ,:org_id ,:receive_item_id ,:ship_to_location_id ,:employee_id_receiver ,:deliver_to_location_id ,:po_rate ,:po_item_id ,:po_qty ,:unit_price ,:po_amount_idr ,:requisition_header_id ,:requisition_line_id ,:pr_line_num ,:pr_qty ,:pr_unit_price ,:pr_rates ,:po_currency ,:pr_currency ,:po ,:pr ,:vendor_name ,:receive_item_name ,:receive_item_desc ,:ship_to_location_desc ,:receiver_name ,:deliver_to_location_desc ,:deliver_to_person ,:buyer_name ,:po_description ,:po_item_description ,:pr_description ,:requestor_name ,:destination_type_code ,:po_status ,:pr_status ,:po_uom ,:rr_uom ,:pr_uom ,:receipt_num ,:receive_item_code ,:rr_uom_desc ,:po_uom_desc ,:pr_uom_desc ,:ship_to_location ,:deliver_to_location, :odoo_log_id)"
                # _logger.info('sql nih :')
                # _logger.info(sql)
                cur.execute(sql, {'sourcedata': line.sourcedata or None, 'receive_date': line.receive_date or None,
                                  'po_date': line.po_date or None, 'po_rate_date': line.po_rate_date or None,
                                  'pr_date': line.pr_date or None, 'pr_rate_date': line.pr_rate_date or None,
                                  'po_header_id': line.po_header_id or None, 'po_line_id': line.po_line_id,
                                  'po_line': line.po_line or 0, 'pr_amount_idr': line.pr_amount_idr or '0',
                                  'buyer_id': line.buyer_id or '0',
                                  'deliver_to_person_id': line.deliver_to_person_id or None,
                                  'requestor_id': line.requestor_id or None,
                                  'shipment_header_id': line.shipment_header_id or None,
                                  'vendor_id': line.vendor_id or None, 'vendor_site_id': line.vendor_site_id or None,
                                  'line_num': line.line_num or None, 'primary_quantity': line.primary_quantity or '0',
                                  'qty_receive': line.qty_receive or '0', 'rr_qty': line.rr_qty or None,
                                  'inv_org_id': line.inv_org_id or None, 'org_id': line.org_id or None,
                                  'receive_item_id': line.receive_item_id or None,
                                  'ship_to_location_id': line.ship_to_location_id or None,
                                  'employee_id_receiver': line.employee_id_receiver or None,
                                  'deliver_to_location_id': line.deliver_to_location_id or None,
                                  'po_rate': line.po_rate or None, 'po_item_id': line.po_item_id or None,
                                  'po_qty': line.po_qty or '0', 'unit_price': line.unit_price or '0',
                                  'po_amount_idr': line.po_amount_idr or '0',
                                  'requisition_header_id': line.requisition_header_id or None,
                                  'requisition_line_id': line.requisition_line_id or None,
                                  'pr_line_num': line.pr_line_num or None, 'pr_qty': line.pr_qty or '0',
                                  'pr_unit_price': line.pr_unit_price or '0', 'pr_rates': line.pr_rates or '0',
                                  'po_currency': line.po_currency or None, 'pr_currency': line.pr_currency or None,
                                  'po': line.po or None, 'pr': line.pr or None, 'vendor_name': line.vendor_name or None,
                                  'receive_item_name': line.receive_item_name or None,
                                  'receive_item_desc': line.receive_item_desc or None,
                                  'ship_to_location_desc': line.ship_to_location_desc or None,
                                  'receiver_name': line.receiver_name or None,
                                  'deliver_to_location_desc': line.deliver_to_location_desc or None,
                                  'deliver_to_person': line.deliver_to_person or None,
                                  'buyer_name': line.buyer_name or None, 'po_description': line.po_description or None,
                                  'po_item_description': line.po_item_description or None,
                                  'pr_description': line.pr_description or None,
                                  'requestor_name': line.requestor_name or None,
                                  'destination_type_code': line.destination_type_code or None,
                                  'po_status': line.po_status or None, 'pr_status': line.pr_status or None,
                                  'po_uom': line.po_uom or None, 'rr_uom': line.rr_uom or None,
                                  'pr_uom': line.pr_uom or None, 'receipt_num': line.receipt_num or '0',
                                  'receive_item_code': line.receive_item_code or None,
                                  'rr_uom_desc': line.rr_uom_desc or None, 'po_uom_desc': line.po_uom_desc or None,
                                  'pr_uom_desc': line.pr_uom_desc or None,
                                  'ship_to_location': line.ship_to_location or None,
                                  'deliver_to_location': line.deliver_to_location or None, 'odoo_log_id': sync_log_id})

                # line.state = 'sent'
                # sent_cnt += 1

            cur.close()
            con.commit()
            con.close()

            # dan setelah data sukses terkirim ke oracle staging
            # lakukan proses copy data dari
            # r12_po_receives ke xpo, xpo_receipt, xpr
            # 1. jalankan fungsi xpo.run_in_atis()
            # 2. jalankan fungsi xpo_receipt.run_in_atis()
            # 3. jalankan fungsi xpr.run_in_atis()
            # tempelkan disini.

            self.env['x.po'].run_in_atis()
            self.env['x.po.receipt'].run_in_atis()
            self.env['x.pr'].run_in_atis()

            # cur.execute('select * from dept where rownum < 10')
            # cur.execute('select * from dept ')
            # for result in cur:
            #     print(result)
            #     print('kolom 1 : ' + str(result[0]) + ', kolom 2 : ' + str(result[1]) + ', kolom 3 : ' + str(result[2]))

            log_id.write({'step02_end_time': datetime.now(),
                          'step02_count': send_cnt,
                          })

            print("insert Oracle - push_data_to_atis")

    def count_data_from_atis(self, sync_log_id):

        # a = ambil total baris data terkini dari atis
        # b = ambil total baris data terkini dari odoo
        # c = a - odoo = jumlah data yang selisih .
        # jika tidak ada selisih maka data match .

        # _logger.info('posisi di count_data_from_atis')
        # _logger.info(sync_log_id)

        log_ids = self.env['mnc.sync.logger'].search([
            ('id', '=', sync_log_id),
        ])

        # _logger.info(log_ids)

        for log_id in log_ids:
            log_id.write({
                'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
                'model_name': self._name,
                'step03_activity': 'Count Sent items in ATIS',
                'step03_desc': 'Count Sent items in ATIS',
                'step03_source': 'ora_stg',
                'step03_target': 'ora_stg',
                'step03_start_time': datetime.now(),
                'step03_end_time': False,
                'step03_caller': self._name + '.count_data_from_atis',
                'step03_count': 0,
                'curr_steps': 3,
                #
            })

            hasil = 0

            import cx_Oracle
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="10.3.99.165:1521/xe")
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="localhost:1521/xe")
            # TODO: Buatkan Modul untuk menyimpan data user, password, dsn ini. Saat ini username dan password masih dalam kondisi Hard Code.

            ora_atis_user = self.env['mnc.token.management'].get_ora_atis_user('r12.po.receives')
            if not ora_atis_user:
                ora_atis_user = "atisappsr12dev"
                _logger.info('default ora_atis_pass default')

            ora_atis_pass = self.env['mnc.token.management'].get_ora_atis_pass('r12.po.receives')
            if not ora_atis_pass:
                ora_atis_pass = "atisappsr12dev"
                _logger.info('default ora_atis_pass default')

            ora_atis_dsn = self.env['mnc.token.management'].get_ora_atis_dsn('r12.po.receives')
            if not ora_atis_dsn:
                # tambahkan code untuk pengecekan lebih lanjut, jika tidak dikonfigurasi .
                ora_atis_dsn = "arjuna.mncgroup.com:1523/rcti"
                _logger.info('default ora_atis_pass default')

            _logger.info('get data from param - done')
            # _logger.info(ora_atis_user)
            # _logger.info(ora_atis_pass)
            # _logger.info(ora_atis_dsn)

            con = cx_Oracle.connect(user=ora_atis_user, password=ora_atis_pass, dsn=ora_atis_dsn)
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="localhost:1521/xe")
            cur = con.cursor()

            cur.execute("select count(1) as total_baris from r12_po_receives where sourcedata = 'O14'")

            for result in cur:
                print('kolom 1 : ')
                print(result[0])
                hasil = result[0]

            cur.close()
            con.commit()
            con.close()

            log_id.write({
                'step03_end_time': datetime.now(),
                'step03_count': hasil,
                'diff_count': hasil - log_id.step02_count,
                #
            })

            # _logger.info('count_data_from_atis')

    def get_token(self):
        o_token = self.env['mnc.token.management'].get_token(self._name)
        #
        return o_token.token

    def get_inv_org_id(self, company_id):
        # sebelum tgl 10 nov 2022 .
        # mapping adalah inv_org_id = po.company_id.id

        stock_location_ids = self.env['stock.location'].search([
            ('active', '=', True),
            ('usage', '=', 'internal'),
            ('return_location', '=', False),
            ('barcode', '!=', False),
            ('company_id', '=', company_id),
        ], limit=1)

        res = False
        for sl in stock_location_ids:
            res = sl.id

        # select *
        # from stock_location where
        # active = True and usage = 'internal' and return_location is null and barcode is not null

        return res

    def send_all_odoo_stg(self):

        # _logger.info('posisi di : fill_odoo_staging_table yy')
        # _logger.info(self._name)

        fetch_cnt = 0
        msl_id = self.env['mnc.sync.logger'].create({
            'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'model_name': self._name,
            'step01_activity': 'Fill Odoo Staging Table',
            'step01_desc': 'Fill Odoo Staging Table',
            'step01_source': 'odoo',
            'step01_target': 'odoo_stg',
            'step01_start_time': datetime.now(),
            'step01_end_time': False,
            'step01_caller': self._name + '.fill_odoo_staging_table',
            'step01_count': 0,
            'curr_steps': 1,
            'total_steps': 3,
        })

        # _logger.info('posisi di : fill_odoo_staging_table yy')

        # stock.picking
        stock_pick_ids = self.env['stock.picking'].search([('state', '=', 'done'), ('name', 'ilike', '/IN/')])

        # _logger.info(stock_pick_ids)

        for record in stock_pick_ids:
            # _logger.info('record')
            # _logger.info(record)
            # po_numbers = fields.Char(string="PO Numbers", compute='_compute_po_numbers', store=True)

            purchase_order_number = False
            po_split = record.po_numbers.split(',')
            for po_list in po_split:
                purchase_order_number = po_list.strip()

                # for line in record.move_ids_without_package:
                # _logger.info('line')
                # _logger.info(line)
                if not purchase_order_number:
                    # line.purchase_order_number:
                    # _logger.info('gak punya po number di detail nya ')
                    pass
                else:
                    # _logger.info('not order number')
                    # _logger.info(line.purchase_order_number)
                    # _logger.info('okee 555')
                    # PO
                    po_ids = self.env['purchase.order'].search([
                        ('name', '=', purchase_order_number)
                    ])
                    # ('name', '=', line.purchase_order_number)
                    # _logger.info('okee 666')
                    ##_logger.info(po_ids)

                    vals = {}
                    for po in po_ids:
                        # _logger.info('siap poopkokpo')
                        # _logger.info(po.state)

                        # init data
                        sourcedata = 'O14'
                        receive_date = False
                        po_date = po.date_order
                        po_rate_date = po.date_order
                        pr_date = False
                        pr_rate_date = False
                        po_header_id = po.id
                        po_line_id = False
                        po_line = False
                        pr_amount_idr = False
                        buyer_id = po.buyer_id.id
                        deliver_to_person_id = False
                        requestor_id = False
                        shipment_header_id = False
                        vendor_id = False
                        vendor_site_id = False
                        line_num = False
                        primary_quantity = False
                        qty_receive = False
                        rr_qty = False
                        # inv_org_id = po.company_id.id
                        inv_org_id = self.get_inv_org_id(po.company_id.id)
                        org_id = po.company_id.org_id
                        receive_item_id = False
                        ship_to_location_id = False
                        employee_id_receiver = False
                        deliver_to_location_id = False
                        po_rate = po.actual_rate
                        po_item_id = False
                        po_qty = False
                        unit_price = False
                        po_amount_idr = False
                        requisition_header_id = False
                        requisition_line_id = False
                        pr_line_num = False
                        pr_qty = False
                        pr_unit_price = False
                        pr_rates = False
                        po_currency = po.currency_id.name
                        pr_currency = False
                        po_no = po.name
                        pr_no = False
                        vendor_name = False
                        receive_item_name = False
                        receive_item_desc = False
                        ship_to_location_desc = False
                        receiver_name = False
                        deliver_to_location_desc = False
                        deliver_to_person = False
                        buyer_name = po.buyer_id.name
                        po_description = po.po_description
                        po_item_description = False
                        pr_description = False
                        requestor_name = False
                        destination_type_code = False
                        po_status = self.get_ora_po_state(po.state)
                        pr_status = False
                        po_uom = False
                        rr_uom = False
                        pr_uom = False
                        receipt_num = False
                        receive_item_code = False
                        rr_uom_desc = False
                        po_uom_desc = False
                        pr_uom_desc = False
                        ship_to_location = False
                        deliver_to_location = False

                        # _logger.info('po head 01')

                        for sp in po.picking_ids:
                            shipment_header_id = sp.id
                            receipt_num = sp.name
                            receive_date = sp.date_done
                            vendor_id = sp.partner_id.id
                            vendor_name = sp.partner_id.name
                            ship_to_location_id = sp.location_dest_id.id
                            ship_to_location = sp.location_dest_id.name
                            ship_to_location_desc = sp.location_dest_id.complete_name
                            deliver_to_location_id = sp.location_dest_id.id
                            deliver_to_location = sp.location_dest_id.name
                            deliver_to_location_desc = sp.location_dest_id.complete_name

                            if sp.id:
                                destination_type_code = 'RECEIVING'
                            else:
                                destination_type_code = ''

                            # _logger.info('sp 01')

                            for vs in sp.partner_id.site_ids:
                                # harusnya ambil baris teratas saja
                                vendor_site_id = vs.id

                                # _logger.info('vs 01')

                        ###### P R #########

                        # PR
                        po_origin = []
                        if po.origin:
                            many_po_origin = po.origin.split(",")
                            _logger.info("saya disini many_po_origin")
                            _logger.info(many_po_origin)

                            for x in many_po_origin:
                                _logger.info("masuk di x")
                                _logger.info(x)
                                po_origin.append(x)
                            _logger.info("po_origin")
                            _logger.info(po_origin)

                        pr_ids = self.env['purchase.request'].search([
                            ('name', 'in', po_origin),
                        ])
                        _logger.info("lagi di pr_ids tempat 1")
                        _logger.info(pr_ids)

                        for pr in pr_ids:
                            employee_id_receiver = pr.requested_by.id
                            receiver_name = pr.requested_by.name
                            deliver_to_person_id = pr.requested_by.id
                            deliver_to_person = pr.requested_by.name
                            requisition_header_id = pr.id
                            pr_no = pr.name
                            pr_status = self.get_ora_pr_state(pr.state)
                            pr_date = pr.date_start
                            pr_description = pr.description
                            requestor_id = pr.requested_by.id
                            requestor_name = pr.requested_by.name
                            ##_logger.info(pr.requested_by)
                            ##_logger.info(pr.requested_by.name)
                            ##_logger.info(pr.id)
                            # _logger.info(pr.name)

                            # _logger.info('pr 01')

                        ####### P R ########

                        # PO Line

                        for pol in po.order_line:
                            primary_quantity = pol.product_qty
                            qty_receive = pol.qty_received
                            po_line_id = pol.id
                            po_line = pol.line_number
                            po_item_id = pol.product_id.id
                            po_item_description = pol.name
                            po_uom = pol.product_id.uom_id.name[0:15]
                            po_uom_desc = pol.product_id.uom_id.name
                            unit_price = pol.price_unit
                            po_amount_idr = pol.price_subtotal

                            # po_qty
                            po_qty = pol.product_qty

                            ##_logger.info(pol.product_qty)
                            ##_logger.info(pol.line_number)
                            # _logger.info('sini')

                            # PR Line
                            if requisition_header_id:
                                prl_ids = self.env['purchase.request.line'].search([
                                    ('request_id', '=', requisition_header_id),
                                    ('line_number', '=', pol.line_number),
                                ])

                                ##_logger.info(prl_ids)

                                # _logger.info('pr 01')

                                for prl in prl_ids:
                                    requisition_line_id = prl.id
                                    pr_line_num = prl.line_number
                                    pr_qty = prl.product_qty
                                    pr_uom = prl.product_id.uom_id.id
                                    pr_uom_desc = prl.product_id.uom_id.name
                                    pr_unit_price = prl.original_price
                                    pr_currency = prl.select_currency_id.name
                                    pr_rates = prl.actual_rate
                                    pr_rate_date = prl.date_rate
                                    pr_amount_idr = prl.estimated_cost

                                    # _logger.info('prl 01')

                            for sm in sp.move_lines:
                                if sm.purchase_line_number == pol.line_number:
                                    line_num = sm.purchase_line_number
                                    rr_qty = sm.quantity_done
                                    rr_uom = sm.product_uom.name[0:15]
                                    rr_uom_desc = sm.product_uom.name
                                    receive_item_id = sm.product_id.id
                                    receive_item_code = sm.product_id.code
                                    receive_item_name = sm.product_id.product_tmpl_id.name
                                    receive_item_desc = sm.description_picking

                                    # _logger.info(sm.purchase_line_number)
                                    # _logger.info('sm 01')

                            # data diinsert ketika pol
                            vals = {
                                'sourcedata': sourcedata,
                                'shipment_header_id': shipment_header_id,
                                'receipt_num': receipt_num,
                                'receive_date': receive_date,
                                'vendor_id': vendor_id,
                                'vendor_name': vendor_name,
                                'vendor_site_id': vendor_site_id,
                                'line_num': line_num,
                                'destination_type_code': destination_type_code,
                                'primary_quantity': primary_quantity,
                                'qty_receive': qty_receive,
                                'rr_qty': rr_qty,
                                'rr_uom': rr_uom,
                                'rr_uom_desc': rr_uom_desc,
                                'inv_org_id': inv_org_id,
                                'org_id': org_id,
                                'receive_item_id': receive_item_id,
                                'receive_item_code': receive_item_code,
                                'receive_item_name': receive_item_name,
                                'receive_item_desc': receive_item_desc,
                                'ship_to_location_id': ship_to_location_id,
                                'ship_to_location': ship_to_location,
                                'ship_to_location_desc': ship_to_location_desc,
                                'employee_id_receiver': employee_id_receiver,
                                'receiver_name': receiver_name,
                                'deliver_to_location_id': deliver_to_location_id,
                                'deliver_to_location': deliver_to_location,
                                'deliver_to_location_desc': deliver_to_location_desc,
                                'deliver_to_person_id': deliver_to_person_id,
                                'deliver_to_person': deliver_to_person,
                                'po_header_id': po_header_id,
                                # 'po': po,
                                'po': po_no,
                                'po_status': po_status,
                                'buyer_id': buyer_id,
                                'buyer_name': buyer_name,
                                'po_date': po_date,
                                'po_description': po_description,
                                'po_currency': po_currency,
                                'po_rate': po_rate,
                                'po_rate_date': po_rate_date,
                                'po_line_id': po_line_id,
                                'po_line': po_line,
                                'po_item_id': po_item_id,
                                'po_item_description': po_item_description,
                                'po_qty': po_qty,
                                'po_uom': po_uom,
                                'po_uom_desc': po_uom_desc,
                                'unit_price': unit_price,
                                'po_amount_idr': po_amount_idr,
                                'requisition_header_id': requisition_header_id,
                                # 'pr': pr,
                                'pr': pr_no,
                                'pr_status': pr_status,
                                'pr_date': pr_date,
                                'pr_description': pr_description,
                                'requestor_id': requestor_id,
                                'requestor_name': requestor_name,
                                'requisition_line_id': requisition_line_id,
                                'pr_line_num': pr_line_num,
                                'pr_qty': pr_qty,
                                'pr_uom': pr_uom,
                                'pr_uom_desc': pr_uom_desc,
                                'pr_unit_price': pr_unit_price,
                                'pr_currency': pr_currency,
                                'pr_rates': pr_rates,
                                'pr_rate_date': pr_rate_date,
                                'pr_amount_idr': pr_amount_idr,
                                'sync_log_id': msl_id.id
                            }

                            # fetch_cnt +=1

                            ##_logger.info(vals)

                            # dia search dulu ke r12.po.receives
                            # cek po_header_id, po_line_id, po_line,
                            # pastikan tidak sama .
                            # kalau benar2x belum ada datanya .
                            # baru create r12 po receives

                            no_dup_dt = self.env['r12.po.receives'].search([
                                ('po', '=', po_no),
                                ('pr', '=', pr_no),
                                ('po_header_id', '=', po_header_id),
                                ('po_line_id', '=', po_line_id),
                                ('receipt_num', '=', receipt_num),
                            ])

                            # kalau tidak ganda ya masukkan datanya
                            if not no_dup_dt:
                                self.env['r12.po.receives'].create(vals)
                                fetch_cnt += 1

                    #

                    msl_ids = self.env['mnc.sync.logger'].search([("id", "=", msl_id.id)])
                    for msl_data in msl_ids:
                        msl_data.write({'step01_end_time': datetime.now(),
                                        'step01_count': fetch_cnt,
                                        })

                    # _logger.info('posisi di : fill_odoo_staging_table okokoko')

        return msl_id

    def send_one_odoo_stg(self, picking_id):

        # _logger.info('posisi di : fill_odoo_staging_table yy')
        # _logger.info(self._name)

        fetch_cnt = 0
        msl_id = self.env['mnc.sync.logger'].create({
            'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'model_name': self._name,
            'step01_activity': 'Fill Odoo Staging Table',
            'step01_desc': 'Fill Odoo Staging Table',
            'step01_source': 'odoo',
            'step01_target': 'odoo_stg',
            'step01_start_time': datetime.now(),
            'step01_end_time': False,
            'step01_caller': self._name + '.fill_odoo_staging_table',
            'step01_count': 0,
            'curr_steps': 1,
            'total_steps': 3,
        })

        # _logger.info('posisi di : fill_odoo_staging_table yy')

        # stock.picking
        # stock_pick_ids = self.env['stock.picking'].search([('state', '=', 'done'),('name', 'ilike', '/IN/')])
        _logger.info('picking_id : ')
        _logger.info(picking_id)
        stock_pick_ids = self.env['stock.picking'].search([('id', '=', picking_id)])

        # _logger.info(stock_pick_ids)

        for record in stock_pick_ids:
            # _logger.info('record')
            # _logger.info(record)
            # po_numbers = fields.Char(string="PO Numbers", compute='_compute_po_numbers', store=True)

            purchase_order_number = False
            po_split = record.po_numbers.split(',')
            for po_list in po_split:
                purchase_order_number = po_list.strip()

                # for line in record.move_ids_without_package:
                # _logger.info('line')
                # _logger.info(line)
                if not purchase_order_number:
                    # line.purchase_order_number:
                    # _logger.info('gak punya po number di detail nya ')
                    pass
                else:
                    # _logger.info('not order number')
                    # _logger.info(line.purchase_order_number)
                    # _logger.info('okee 555')
                    # PO
                    po_ids = self.env['purchase.order'].search([
                        ('name', '=', purchase_order_number)
                    ])
                    # ('name', '=', line.purchase_order_number)
                    # _logger.info('okee 666')
                    ##_logger.info(po_ids)

                    vals = {}
                    for po in po_ids:
                        # _logger.info('siap poopkokpo')
                        # _logger.info(po.state)

                        # init data
                        sourcedata = 'O14'
                        receive_date = False
                        po_date = po.date_order
                        po_rate_date = po.date_order
                        pr_date = False
                        pr_rate_date = False
                        po_header_id = po.id
                        po_line_id = False
                        po_line = False
                        pr_amount_idr = False
                        buyer_id = po.buyer_id.id
                        deliver_to_person_id = False
                        requestor_id = False
                        shipment_header_id = False
                        vendor_id = False
                        vendor_site_id = False
                        line_num = False
                        primary_quantity = False
                        qty_receive = False
                        rr_qty = False
                        # inv_org_id = po.company_id.id
                        inv_org_id = self.get_inv_org_id(po.company_id.id)
                        org_id = po.company_id.org_id
                        receive_item_id = False
                        ship_to_location_id = False
                        employee_id_receiver = False
                        deliver_to_location_id = False
                        po_rate = po.actual_rate
                        po_item_id = False
                        po_qty = False
                        unit_price = False
                        po_amount_idr = False
                        requisition_header_id = False
                        requisition_line_id = False
                        pr_line_num = False
                        pr_qty = False
                        pr_unit_price = False
                        pr_rates = False
                        po_currency = po.currency_id.name
                        pr_currency = False
                        po_no = po.name
                        pr_no = False
                        vendor_name = False
                        receive_item_name = False
                        receive_item_desc = False
                        ship_to_location_desc = False
                        receiver_name = False
                        deliver_to_location_desc = False
                        deliver_to_person = False
                        buyer_name = po.buyer_id.name
                        po_description = po.po_description
                        po_item_description = False
                        pr_description = False
                        requestor_name = False
                        destination_type_code = False
                        po_status = self.get_ora_po_state(po.state)
                        pr_status = False
                        po_uom = False
                        rr_uom = False
                        pr_uom = False
                        receipt_num = False
                        receive_item_code = False
                        rr_uom_desc = False
                        po_uom_desc = False
                        pr_uom_desc = False
                        ship_to_location = False
                        deliver_to_location = False

                        # _logger.info('po head 01')

                        for sp in po.picking_ids:
                            shipment_header_id = sp.id
                            receipt_num = sp.name
                            receive_date = sp.date_done
                            vendor_id = sp.partner_id.id
                            vendor_name = sp.partner_id.name
                            ship_to_location_id = sp.location_dest_id.id
                            ship_to_location = sp.location_dest_id.name
                            ship_to_location_desc = sp.location_dest_id.complete_name
                            deliver_to_location_id = sp.location_dest_id.id
                            deliver_to_location = sp.location_dest_id.name
                            deliver_to_location_desc = sp.location_dest_id.complete_name

                            if sp.id:
                                destination_type_code = 'RECEIVING'
                            else:
                                destination_type_code = ''

                            # _logger.info('sp 01')

                            for vs in sp.partner_id.site_ids:
                                # harusnya ambil baris teratas saja
                                vendor_site_id = vs.id

                                # _logger.info('vs 01')

                        ###### P R #########

                        # PR
                        pr_ids = self.env['purchase.request'].search([
                            ('name', '=', po.origin),
                        ])

                        for pr in pr_ids:
                            employee_id_receiver = pr.requested_by.id
                            receiver_name = pr.requested_by.name
                            deliver_to_person_id = pr.requested_by.id
                            deliver_to_person = pr.requested_by.name
                            requisition_header_id = pr.id
                            pr_no = pr.name
                            pr_status = self.get_ora_pr_state(pr.state)
                            pr_date = pr.date_start
                            pr_description = pr.description
                            requestor_id = pr.requested_by.id
                            requestor_name = pr.requested_by.name
                            ##_logger.info(pr.requested_by)
                            ##_logger.info(pr.requested_by.name)
                            ##_logger.info(pr.id)
                            # _logger.info(pr.name)

                            # _logger.info('pr 01')

                        ####### P R ########

                        # PO Line

                        for pol in po.order_line:
                            primary_quantity = pol.product_qty
                            qty_receive = pol.qty_received
                            po_line_id = pol.id
                            po_line = pol.line_number
                            po_item_id = pol.product_id.id
                            po_item_description = pol.name
                            po_uom = pol.product_id.uom_id.name[0:15]
                            po_uom_desc = pol.product_id.uom_id.name
                            unit_price = pol.price_unit
                            po_amount_idr = pol.price_subtotal

                            ##_logger.info(pol.product_qty)
                            ##_logger.info(pol.line_number)
                            # _logger.info('sini')

                            # PR Line
                            if requisition_header_id:
                                prl_ids = self.env['purchase.request.line'].search([
                                    ('request_id', '=', requisition_header_id),
                                    ('line_number', '=', pol.line_number),
                                ])

                                ##_logger.info(prl_ids)

                                # _logger.info('pr 01')

                                for prl in prl_ids:
                                    requisition_line_id = prl.id
                                    pr_line_num = prl.line_number
                                    pr_qty = prl.product_qty
                                    pr_uom = prl.product_id.uom_id.id
                                    pr_uom_desc = prl.product_id.uom_id.name
                                    pr_unit_price = prl.original_price
                                    pr_currency = prl.select_currency_id.name
                                    pr_rates = prl.actual_rate
                                    pr_rate_date = prl.date_rate
                                    pr_amount_idr = prl.estimated_cost

                                    # _logger.info('prl 01')

                            for sm in sp.move_lines:
                                if sm.purchase_line_number == pol.line_number:
                                    line_num = sm.purchase_line_number
                                    rr_qty = sm.quantity_done
                                    rr_uom = sm.product_uom.name[0:15]
                                    rr_uom_desc = sm.product_uom.name
                                    receive_item_id = sm.product_id.id
                                    receive_item_code = sm.product_id.code
                                    receive_item_name = sm.product_id.product_tmpl_id.name
                                    receive_item_desc = sm.description_picking

                                    # _logger.info(sm.purchase_line_number)
                                    # _logger.info('sm 01')

                            # data diinsert ketika pol
                            vals = {
                                'sourcedata': sourcedata,
                                'shipment_header_id': shipment_header_id,
                                'receipt_num': receipt_num,
                                'receive_date': receive_date,
                                'vendor_id': vendor_id,
                                'vendor_name': vendor_name,
                                'vendor_site_id': vendor_site_id,
                                'line_num': line_num,
                                'destination_type_code': destination_type_code,
                                'primary_quantity': primary_quantity,
                                'qty_receive': qty_receive,
                                'rr_qty': rr_qty,
                                'rr_uom': rr_uom,
                                'rr_uom_desc': rr_uom_desc,
                                'inv_org_id': inv_org_id,
                                'org_id': org_id,
                                'receive_item_id': receive_item_id,
                                'receive_item_code': receive_item_code,
                                'receive_item_name': receive_item_name,
                                'receive_item_desc': receive_item_desc,
                                'ship_to_location_id': ship_to_location_id,
                                'ship_to_location': ship_to_location,
                                'ship_to_location_desc': ship_to_location_desc,
                                'employee_id_receiver': employee_id_receiver,
                                'receiver_name': receiver_name,
                                'deliver_to_location_id': deliver_to_location_id,
                                'deliver_to_location': deliver_to_location,
                                'deliver_to_location_desc': deliver_to_location_desc,
                                'deliver_to_person_id': deliver_to_person_id,
                                'deliver_to_person': deliver_to_person,
                                'po_header_id': po_header_id,
                                # 'po': po,
                                'po': po_no,
                                'po_status': po_status,
                                'buyer_id': buyer_id,
                                'buyer_name': buyer_name,
                                'po_date': po_date,
                                'po_description': po_description,
                                'po_currency': po_currency,
                                'po_rate': po_rate,
                                'po_rate_date': po_rate_date,
                                'po_line_id': po_line_id,
                                'po_line': po_line,
                                'po_item_id': po_item_id,
                                'po_item_description': po_item_description,
                                'po_qty': po_qty,
                                'po_uom': po_uom,
                                'po_uom_desc': po_uom_desc,
                                'unit_price': unit_price,
                                'po_amount_idr': po_amount_idr,
                                'requisition_header_id': requisition_header_id,
                                # 'pr': pr,
                                'pr': pr_no,
                                'pr_status': pr_status,
                                'pr_date': pr_date,
                                'pr_description': pr_description,
                                'requestor_id': requestor_id,
                                'requestor_name': requestor_name,
                                'requisition_line_id': requisition_line_id,
                                'pr_line_num': pr_line_num,
                                'pr_qty': pr_qty,
                                'pr_uom': pr_uom,
                                'pr_uom_desc': pr_uom_desc,
                                'pr_unit_price': pr_unit_price,
                                'pr_currency': pr_currency,
                                'pr_rates': pr_rates,
                                'pr_rate_date': pr_rate_date,
                                'pr_amount_idr': pr_amount_idr,
                                'sync_log_id': msl_id.id
                            }

                            # fetch_cnt +=1

                            ##_logger.info(vals)

                            # dia search dulu ke r12.po.receives
                            # cek po_header_id, po_line_id, po_line,
                            # pastikan tidak sama .
                            # kalau benar2x belum ada datanya .
                            # baru create r12 po receives

                            no_dup_dt = self.env['r12.po.receives'].search([
                                ('po', '=', po_no),
                                ('pr', '=', pr_no),
                                ('po_header_id', '=', po_header_id),
                                ('po_line_id', '=', po_line_id),
                                ('receipt_num', '=', receipt_num),
                            ])

                            # kalau tidak ganda ya masukkan datanya
                            if not no_dup_dt:
                                self.env['r12.po.receives'].create(vals)
                                fetch_cnt += 1

                    #

                    msl_ids = self.env['mnc.sync.logger'].search([("id", "=", msl_id.id)])
                    for msl_data in msl_ids:
                        msl_data.write({'step01_end_time': datetime.now(),
                                        'step01_count': fetch_cnt,
                                        })

                    # _logger.info('posisi di : fill_odoo_staging_table okokoko')

        return msl_id

    def send_all_to_atis(self):
        # _logger.info('posisi di send_all_to_atis')
        # _logger.info('first time only - run this via odoo scheduler - ir.cron ')
        sync_log_id = self.sudo().send_all_odoo_stg()
        self.sudo().push_data_to_atis(sync_log_id.id)
        self.sudo().count_data_from_atis(sync_log_id.id)

    def send_one_to_atis(self, picking_id):
        # _logger.info('posisi di send_all_to_atis')
        # _logger.info('first time only - run this via odoo scheduler - ir.cron ')
        sync_log_id = self.sudo().send_one_odoo_stg(picking_id)
        self.sudo().push_data_to_atis(sync_log_id.id)
        self.sudo().count_data_from_atis(sync_log_id.id)
