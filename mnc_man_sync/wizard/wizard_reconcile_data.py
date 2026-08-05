from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, time, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import xlsxwriter
import calendar
import collections

import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WizardMmnReconcileData(models.TransientModel):
    _name = 'wizard.mnc.reconcile.data'

    @api.model
    def get_year_selection(self):
        years = []
        show_year = 0
        next_year = datetime.today().year + 2
        while show_year < 10:
            years.append(next_year)
            next_year -= 1
            show_year += 1
        return [(str(year), str(year)) for year in years]

    @api.model
    def get_this_year(self):
        return str(datetime.today().year)

    # @api.model
    # def _get_default_company_id(self):
    #     return self.env.user.company_id.id

    month = fields.Selection([
        ('01', 'Januari'), ('02', 'Februari'),
        ('03', 'Maret'), ('04', 'April'),
        ('05', 'Mei'), ('06', 'Juni'),
        ('07', 'Juli'), ('08', 'Agustus'),
        ('09', 'September'), ('10', 'Oktober'),
        ('11', 'November'), ('12', 'Desember')], string="Month")
    year = fields.Selection(selection="get_year_selection", default=get_this_year, string="Year")

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)

    def action_reconcile(self):
        post_data = self.post_data(self.company_id.id, self.month, self.year)
        # if post_data:
        get_data = self.get_data(self.company_id.id, self.month, self.year)

    def post_data(self, company, month, year):
        pass
        import cx_Oracle
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

        con = cx_Oracle.connect(user=ora_atis_user, password=ora_atis_pass, dsn=ora_atis_dsn)
        cur = con.cursor()

        date_from = datetime.strptime('%s-%s-%s' % (str(year), str(month), str(1)), '%Y-%m-%d')
        date_end = date_from + relativedelta(months=1)

        asset_ids = self.env['account.asset'].search(
            [('state', '=', 'open'), ('company_id', '=', company),
             ('first_depreciation_date', '>=', date_from.strftime('%Y-%m-%d')),
             ('first_depreciation_date', '<=', date_end.strftime('%Y-%m-%d'))])

        for asset_list in asset_ids:
            sql = "MERGE INTO    asset_rcv_line_barcode_parents trg " \
                  "USING   ( " \
                  "                select " \
                  "                  arlb.header_id, arlb.line_id, arlb.barcode_parent_id, arlb.asset_id" \
                  "                from asset_rcv_line_barcode_parents arlb " \
                  "                inner join asset_receive_distributions ard " \
                  "                  on arlb.header_id = ard.header_id and arlb.line_id = ard.line_id " \
                  "                where " \
                  "                    ard.PO_NUMBER = :PO_NUMBER " \
                  "                and ard.PO_LINE_NUMBER = :PO_LINE_NUMBER " \
                  "        ) src " \
                  "ON      ( " \
                  "                                trg.header_id         = src.header_id " \
                  "                            and trg.line_id           = src.line_id " \
                  "                            and trg.barcode_parent_id = src.barcode_parent_id " \
                  ") " \
                  "WHEN MATCHED THEN UPDATE " \
                  "    SET " \
                  "trg.ASSET_ID = :ASSET_ID," \
                  "trg.ASSET_NUMBER = :ASSET_NUMBER," \
                  "trg.MAJOR_CATEGORY = :MAJOR_CATEGORY," \
                  "trg.MINOR_CATEGORY = :MINOR_CATEGORY," \
                  "trg.ASSET_DESCRIPTION = :ASSET_DESCRIPTION," \
                  "trg.BOOK_TYPE_CODE = substr(:BOOK_TYPE_CODE, 1, 30)," \
                  "trg.ASSET_DATE_PLACED_IN_SERVICE = :ASSET_DATE_PLACED_IN_SERVICE," \
                  "trg.INVOICE_NUMBER = :INVOICE_NUMBER," \
                  "trg.INVOICE_LINE_NUM = :INVOICE_LINE_NUM," \
                  "trg.PAYMENT_NUMBER = :PAYMENT_NUMBER," \
                  "trg.INVOICE_ID = :INVOICE_ID," \
                  "trg.ASSET_QTY = :ASSET_QTY "

            _logger.info(asset_list.source_line_ids)
            _logger.info(asset_list.source_line_ids[0].invoice_name if asset_list.source_line_ids else '')
            move_ids = self.env['account.move'].search(
                [('name', '=', asset_list.source_line_ids[0].invoice_name if asset_list.source_line_ids else ''),
                 ('move_type', '=', 'in_invoice')], limit=1)

            _logger.info(move_ids)
            invoice_id = move_ids.id if move_ids else None
            _logger.info(invoice_id)
            _logger.info(move_ids.payment_id if move_ids else '')
            payment_number = None

            paynuminv_ids = self.env['account.payment.invoice'].search([('move_id', '=', invoice_id)], limit=1)
            _logger.info(paynuminv_ids)
            if paynuminv_ids:
                _logger.info('ok zone')
                _logger.info(paynuminv_ids.payment_id)
                _logger.info(paynuminv_ids.payment_id.name)
                payment_number = paynuminv_ids.payment_id.name

            cur.execute(sql, {'ASSET_ID': asset_list.id or None,
                              'ASSET_NUMBER': asset_list.asset_no or None,
                              'MAJOR_CATEGORY': asset_list.model_id.segment_id.name or None,
                              'MINOR_CATEGORY': asset_list.model_id.name or None,
                              'ASSET_DESCRIPTION': asset_list.name or None,
                              'BOOK_TYPE_CODE': asset_list.company_id.name or None,
                              'ASSET_DATE_PLACED_IN_SERVICE': asset_list.first_depreciation_date or None,
                              'INVOICE_NUMBER': asset_list.source_line_ids[
                                  0].invoice_name if asset_list.source_line_ids else None,
                              'INVOICE_ID': invoice_id,
                              'PAYMENT_NUMBER': payment_number,
                              'INVOICE_LINE_NUM': asset_list.source_line_ids[
                                  0].invoice_line_number if asset_list.source_line_ids else None,
                              'ASSET_QTY': asset_list.origin_ids[0].quantity if asset_list.origin_ids else None,
                              'PO_NUMBER': asset_list.source_line_ids[
                                  0].purchase_name if asset_list.source_line_ids else None,
                              'PO_LINE_NUMBER': asset_list.source_line_ids[
                                  0].purchase_line_number if asset_list.source_line_ids else None,
                              })

        cur.close()
        con.commit()
        con.close()

    def get_sql_oracle(self, po_number, po_line_number):
        pass
        import cx_Oracle
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

        con = cx_Oracle.connect(user=ora_atis_user, password=ora_atis_pass, dsn=ora_atis_dsn)
        cur = con.cursor()
        sql = "SELECT " \
              "child_barcode," \
              "component_barcode," \
              "barcode_label," \
              "serial_number," \
              "tag_number," \
              "goods_brand," \
              "goods_brand_model," \
              "spesification_details," \
              "condition," \
              "remarks," \
              "item_code," \
              "item_name," \
              "item_description," \
              "po_number," \
              "po_date," \
              "vendor_name," \
              "po_line_number," \
              "po_qty," \
              "pr_number," \
              "pr_date," \
              "pr_line_number," \
              "pr_qty," \
              "doc_number," \
              "doc_date," \
              "line_num," \
              "structure_long_name " \
              " from v_barcode_info where po_number = " + chr(39) + str(po_number) + chr(
            39) + " and po_line_number = " + chr(39) + str(po_line_number) + chr(39) + " and rownum = 1"

        _logger.info("halo 27apr2023 = 44444")
        _logger.info(po_number)
        _logger.info(po_line_number)
        _logger.info(sql)
        # cur.execute(sql, {'PO_NUMBERX': po_number or None,
        #                  'PO_LINE_NUMBERX': po_line_number or None})
        cur.execute(sql)

        if cur:
            for result in cur:
                _logger.info("hasil ada disini ")
                _logger.info(cur)
                res = {
                    "child_barcode": result[0] or '',
                    "barcode_label": result[1] or '',
                    "component_barcode": result[2] or '',
                    "serial_number": result[3] or '',
                    "tag_number": result[4] or '',
                    "goods_brand": result[5] or '',
                    "goods_brand_model": result[6] or '',
                    "spesification_details": result[7] or '',
                    "condition": result[8] or '',
                    "remarks": result[9] or '',
                    "item_code": result[10] or '',
                    "item_name": result[11] or '',
                    "item_description": result[12] or '',
                    "po_number": result[13] or '',
                    "po_date": result[14] or '',
                    "vendor_name": result[15] or '',
                    "po_line_number": result[16] or '',
                    "po_qty": result[17] or '',
                    "pr_number": result[18] or '',
                    "pr_date": result[19] or '',
                    "pr_line_number": result[20] or '',
                    "pr_qty": result[21] or '',
                    "doc_number": result[22] or '',
                    "doc_date": result[23] or '',
                    "line_num": result[24] or '',
                    "structure_long_name": result[25] or ''
                }
                _logger.info(res)

                # con.commit()
                cur.close()
                con.commit()
                con.close()
                if result:
                    return res
                else:
                    return False

        else:

            cur.close()
            con.commit()
            con.close()
            return False

        # con.close()

    def get_data(self, company, month, year):
        date_from = datetime.strptime('%s-%s-%s' % (str(year), str(month), str(1)), '%Y-%m-%d')
        date_end = date_from + relativedelta(months=1)

        asset_ids = self.env['account.asset'].search(
            [('state', '=', 'open'), ('company_id', '=', company),
             ('first_depreciation_date', '>=', date_from.strftime('%Y-%m-%d')),
             ('first_depreciation_date', '<=', date_end.strftime('%Y-%m-%d'))])

        delete_data = self.env['x.asset'].search([('book_type_code', '=', company), ("month", "=", month),
                                                  ("year", "=", year)])
        delete_data.unlink()
        # if delete_data:
        for asset_list in asset_ids:
            _logger.info('ASSET LIST')
            _logger.info(asset_list)
            source_line = self.env['asset.source.line'].search([
                ('asset_id', '=', asset_list.id),
                ('product_id', '!=', False)
            ], limit=1)

            invoice_name = source_line.invoice_name if source_line else None
            invoice_line_number = source_line.invoice_line_number if source_line else None
            product_id = source_line.product_id if source_line else None
            uom_id = product_id.uom_id if product_id else None
            item_code = product_id.default_code if product_id else None
            item_name = product_id.name if product_id else None

            # ...

            po_number = asset_list.source_line_ids[0].purchase_name if asset_list.source_line_ids else None
            po_line_number = asset_list.source_line_ids[
                0].purchase_line_number if asset_list.source_line_ids else None
            atis = self.get_sql_oracle(po_number, po_line_number)
            if atis:
                self.env['x.asset'].create({
                    'book_type_code': asset_list.company_id.name or None,
                    'asset_number': asset_list.asset_no or None,
                    'unit_qty': 0 or None,
                    'asset_description': asset_list.name or None,
                    'major_category': asset_list.segment_id.name or None,
                    'minor_category': asset_list.model_id.name or None,
                    'date_in_service': asset_list.first_depreciation_date or None,
                    'prorate_convention': 0 or None,
                    'prorate_date': asset_list.first_depreciation_date or None,
                    'life_in_months': asset_list.method_number or None,
                    'life_year': asset_list.method_number / 12 or None,
                    'remaining_life_year': 0 or None,
                    'remaining_life_months': 0 or None,
                    'fixed_asset_cost': asset_list.original_value or None,
                    'accumulated_depreciation_cost': asset_list.amount_depreciated or None,
                    'net_book_value': asset_list.book_value or None,
                    'child_barcode': atis['child_barcode'] or None,
                    'component_barcode': atis['component_barcode'] or None,
                    'component_barcode_label': atis['barcode_label'] or None,
                    'serial_number': atis['serial_number'] or None,
                    'tag_number': atis['tag_number'] or None,
                    'goods_brand': atis['goods_brand'] or None,
                    'brand_model': atis['goods_brand_model'] or None,
                    'specification': atis['spesification_details'] or None,
                    'condition': atis['condition'] or None,
                    'remarks': atis['remarks'] or None,
                    'invoice_number': invoice_name if invoice_name else None,
                    'invoice_line_number': invoice_line_number if invoice_line_number else None,
                    'item_code': item_code or None,
                    'item_name': item_name or None,
                    'item_description': atis['item_description'] or None,
                    'po_number': atis['po_number'] or None,
                    'po_date': atis['po_date'] or None,
                    'po_vendor_name': atis['vendor_name'] or None,
                    'po_line_number': atis['po_line_number'] or None,
                    'po_qty': atis['po_qty'] or None,
                    'po_uom': uom_id.name if uom_id else None,
                    'po_uom_description': "" or None,
                    'pr_number': atis['pr_number'] or None,
                    'pr_date': atis['pr_date'] or None,
                    'pr_line_number': atis['pr_line_number'] or None,
                    'pr_qty': atis['pr_qty'] or None,
                    'pr_uom': uom_id.name if uom_id else None,
                    'pr_uom_description': "" or None,
                    'atis_doc_number': atis['doc_number'] or None,
                    'atis_doc_date': atis['doc_date'] or None,
                    'atis_line_number': atis['line_num'] or None,
                    'department_owner': atis['structure_long_name'] or None,
                    'month': self.month,
                    'year': self.year
                })

    # def get_data_schedule_month(self):
    #     curent_year = datetime.datetime.now().strftime("%Y")
    #     curent_month = datetime.datetime.now().strftime("%m")
    #     date_from = datetime.strptime('%s-%s-%s' % (str(curent_year), str(curent_month), str(1)), '%Y-%m-%d')
    #     date_end = date_from - relativedelta(months=1)
    #
    #     asset_ids = self.env['account.asset'].search(
    #         [('state', '=', 'done'), ('first_depreciation_date', '>=', date_end.strftime('%Y-%m-%d')),
    #          ('first_depreciation_date', '<=', date_from.strftime('%Y-%m-%d'))])
    #
    #     for asset_list in asset_ids:
    #         po_number = asset_list.source_line_ids[0].purchase_name if asset_list.source_line_ids else None
    #         po_line_number = asset_list.source_line_ids[0].purchase_line_number if asset_list.source_line_ids else None
    #         delete_data = self.env['x.asset'].search(
    #             [("po_number", "=", po_number), ("po_line_number", "=", po_line_number)])
    #         if delete_data:
    #             atis = self.get_sql_oracle(po_number, po_line_number)
    #             self.env['x.asset'].create({
    #                 'book_type_code': asset_list.company_id.name or None,
    #                 'asset_number': asset_list.asset_no or None,
    #                 'unit_qty': 0 or None,
    #                 'asset_description': asset_list.name or None,
    #                 'major_category': asset_list.segment_id or None,
    #                 'minor_category': asset_list.model_id or None,
    #                 'date_in_service': asset_list.first_depreciation_date or None,
    #                 'prorate_convention': 0 or None,
    #                 'prorate_date': asset_list.first_depreciation_date or None,
    #                 'life_in_months': asset_list.method_number or None,
    #                 'life_year': asset_list.method_number / 12 or None,
    #                 'remaining_life_year': 0 or None,
    #                 'remaining_life_months': 0 or None,
    #                 'fixed_asset_cost': asset_list.original_value or None,
    #                 'accumulated_depreciation_cost': asset_list.amount_depreciated or None,
    #                 'net_book_value': asset_list.book_value or None,
    #                 'child_barcode': atis.child_barcode or None,
    #                 'component_barcode': atis.component_barcode or None,
    #                 'component_barcode_label': atis.barcode_label or None,
    #                 'serial_number': atis.serial_number or None,
    #                 'tag_number': atis.tag_number or None,
    #                 'goods_brand': atis.goods_brand or None,
    #                 'brand_model': atis.goods_brand_model or None,
    #                 'specification': atis.spesification_details or None,
    #                 'condition': atis.condition or None,
    #                 'remarks': atis.remarks or None,
    #                 'payment_voucher': "" or None,
    #                 'invoice_number': "" or None,
    #                 'invoice_line_number': "" or None,
    #                 'remarks': atis.remarks or None,
    #                 'item_code': atis.item_code or None,
    #                 'item_name': atis.item_name or None,
    #                 'item_description': atis.item_description or None,
    #                 'po_number': atis.po_number or None,
    #                 'po_date': atis.po_date or None,
    #                 'po_vendor_name': atis.vendor_name or None,
    #                 'po_line_number': atis.po_line_number or None,
    #                 'po_qty': atis.po_qty or None,
    #                 'po_uom': "" or None,
    #                 'po_uom_description': "" or None,
    #                 'pr_number': atis.pr_number or None,
    #                 'pr_date': atis.pr_date or None,
    #                 'pr_line_number': atis.pr_line_number or None,
    #                 'pr_qty': atis.pr_qty or None,
    #                 'pr_uom': "" or None,
    #                 'pr_uom_description': "" or None,
    #                 'atis_doc_number': atis.doc_number or None,
    #                 'atis_doc_date': atis.doc_date or None,
    #                 'atis_line_number': atis.line_num or None,
    #                 'department_owner': atis.structure_long_name or None,
    #                 'month': self.month,
    #                 'year': self.year
    #             })

    # def get_data_old(self):
    #     pass
    #     import cx_Oracle
    #     # TODO: Buatkan Modul untuk menyimpan data user, password, dsn ini. Saat ini username dan password masih dalam kondisi Hard Code.
    #
    #     ora_atis_user = self.env['mnc.token.management'].get_ora_atis_user('r12.po.receives')
    #     if not ora_atis_user:
    #         ora_atis_user = "atisappsr12dev"
    #         _logger.info('default ora_atis_pass default')
    #
    #     ora_atis_pass = self.env['mnc.token.management'].get_ora_atis_pass('r12.po.receives')
    #     if not ora_atis_pass:
    #         ora_atis_pass = "atisappsr12dev"
    #         _logger.info('default ora_atis_pass default')
    #
    #     ora_atis_dsn = self.env['mnc.token.management'].get_ora_atis_dsn('r12.po.receives')
    #     if not ora_atis_dsn:
    #         ora_atis_dsn = "arjuna.mncgroup.com:1523/rcti"
    #         _logger.info('default ora_atis_pass default')
    #
    #     _logger.info('get data from param - done')
    #
    #     con = cx_Oracle.connect(user=ora_atis_user, password=ora_atis_pass, dsn=ora_atis_dsn)
    #     cur = con.cursor()
    #
    #     delete_data = self.env['x.asset'].search([("month", "=", self.month), ("year", "=", self.year)])
    #     if delete_data:
    #         sql = "SELECT " \
    #               "ASSET_ID," \
    #               "ASSET_NUMBER," \
    #               "MAJOR_CATEGORY," \
    #               "MINOR_CATEGORY," \
    #               "ASSET_DESCRIPTION," \
    #               "BOOK_TYPE_CODE," \
    #               "ASSET_DATE_PLACED_IN_SERVICE," \
    #               "INVOICE_NUMBER," \
    #               "INVOICE_ID," \
    #               "PAYMENT_NUMBER," \
    #               "INVOICE_LINE_NUM," \
    #               "ASSET_QTY" \
    #               " from asset_rcv_line_barcode_parents"
    #         cur.execute(sql)
    #         for result in cur:
    #             asset_id = result[0]
    #             asset_number = result[1]
    #             major_category = result[2]
    #             minor_category = result[3]
    #             asset_description = result[4]
    #             book_type_code = result[5]
    #             asset_date_placed_in_service = result[6]
    #             invoice_number = result[7]
    #             invoice_id = result[8]
    #             payment_number = result[9]
    #             invoice_line_num = result[10]
    #             asset_qty = result[11]
    #
    #             self.env['x.asset'].create({
    #                 'asset_id': asset_id or None,
    #                 'asset_number': asset_number or None,
    #                 'major_category': major_category or None,
    #                 'minor_category': minor_category or None,
    #                 'asset_description': asset_description or None,
    #                 'book_type_code': book_type_code or None,
    #                 'asset_date_placed_in_service': asset_date_placed_in_service or None,
    #                 'invoice_number': invoice_number or None,
    #                 'invoice_id': invoice_id or None,
    #                 'payment_number': payment_number or None,
    #                 'invoice_line_num': invoice_line_num or None,
    #                 'asset_qty': asset_qty or None,
    #                 'month': self.month,
    #                 'year': self.year
    #             })
    #
    #     cur.close()
    #     con.commit()
    #     con.close()
