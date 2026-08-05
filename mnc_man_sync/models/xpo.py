from odoo import api, fields, models, _, tools
from datetime import date, datetime
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class XPo(models.Model):
    _name = 'x.po'
    _description = 'XPO - Odoo Staging Table - prepared for ATIS - Oracle Staging'

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

        sql = "insert into XPO ( SOURCE_DATA, PO_NUMBER, PO_CREATION_DATE, PO_DESCRIPTION, PO_STATUS, ITEM_CODE, PO_LINE_NUM, PO_HEADER_ID, ITEM_ID, REQUESTOR_ID, INV_ORGANIZATION_ID, ORG_ID, ODOO_LOG_ID)      SELECT X.*, TO_NUMBER(TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')) as ODOO_LOG_ID FROM (      select distinct SOURCEDATA as SOURCE_DATA, PO# AS PO_NUMBER, PO_DATE AS PO_CREATION_DATE, PO_DESCRIPTION, PO_STATUS, RECEIVE_ITEM_CODE AS ITEM_CODE, po_line AS PO_LINE_NUM, po_header_id AS PO_HEADER_ID, po_item_id AS ITEM_ID, requestor_id AS REQUESTOR_ID, inv_org_id AS INV_ORGANIZATION_ID, ORG_ID AS ORG_ID from r12_po_receives where sourcedata = 'O14'      minus      select SOURCE_DATA, PO_NUMBER, PO_CREATION_DATE, PO_DESCRIPTION, PO_STATUS, ITEM_CODE, PO_LINE_NUM, PO_HEADER_ID, ITEM_ID, REQUESTOR_ID, INV_ORGANIZATION_ID, ORG_ID from xpo) X"
        cur.execute(sql)

        cur.close()
        con.commit()
        con.close()
