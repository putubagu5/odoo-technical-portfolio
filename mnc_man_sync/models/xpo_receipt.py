from odoo import api, fields, models, _, tools
from datetime import date, datetime
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class XPoReceipt(models.Model):
    _name = 'x.po.receipt'
    _description = 'X-PO-Receipt - Odoo Staging Table - prepared for ATIS - Oracle Staging'


    def run_in_atis(self):
        pass
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

        sql = "insert into xpo_receipt (SOURCE_DATA, RECEIPT_NUMBER, CREATION_DATE, CREATED_BY_USER_ID, CREATED_BY_USER_NAME, LINE_NUM, ITEM_ID, SHIPMENT_HEADER_ID, INV_ORGANIZATION_ID, ORG_ID, ODOO_LOG_ID)      SELECT X.*, TO_NUMBER(TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')) as ODOO_LOG_ID FROM (      SELECT DISTINCT SOURCEDATA AS SOURCE_DATA, receipt_num as RECEIPT_NUMBER, po_date as CREATION_DATE, requestor_id as CREATED_BY_USER_ID, requestor_name as CREATED_BY_USER_NAME, line_num AS LINE_NUM, po_item_id AS ITEM_ID, shipment_header_id AS SHIPMENT_HEADER_ID, inv_org_id AS INV_ORGANIZATION_ID, ORG_ID AS ORG_ID from r12_po_receives where sourcedata = 'O14'      minus      select SOURCE_DATA, RECEIPT_NUMBER, CREATION_DATE, CREATED_BY_USER_ID, CREATED_BY_USER_NAME, LINE_NUM, ITEM_ID, SHIPMENT_HEADER_ID, INV_ORGANIZATION_ID, ORG_ID from xpo_receipt) X"
        cur.execute(sql)

        cur.close()
        con.commit()
        con.close()
