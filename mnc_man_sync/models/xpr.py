from odoo import api, fields, models, _, tools
from datetime import date, datetime
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class XPr(models.Model):
    _name = 'x.pr'
    _description = 'XPR - Odoo Staging Table - prepared for ATIS - Oracle Staging'

    def run_in_atis(self):
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

        sql = "insert into XPR (SOURCE_DATA, PR_NUMBER, PR_CREATION_DATE, PR_STATUS, DESCRIPTION, PR_LINE_NUM, PR_ITEM_CODE, LINE_CANCEL_FLAG, REQUISITION_HEADER_ID, INV_ORG_ID, REQUESTOR_ID, ORG_ID, ODOO_LOG_ID)      SELECT X.*, TO_NUMBER(TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')) as ODOO_LOG_ID FROM (      select distinct SOURCEDATA as source_data, PR# as PR_NUMBER, PR_DATE AS PR_CREATION_DATE, PR_STATUS, pr_description AS DESCRIPTION, PR_LINE_NUM, receive_item_code AS PR_ITEM_CODE, CASE WHEN pr_status ='cancel' then 'Y' else 'N' end as LINE_CANCEL_FLAG, requisition_header_id as REQUISITION_HEADER_ID, INV_ORG_ID, REQUESTOR_ID, ORG_ID from r12_po_receives WHERE pr# is not null and odoo_log_id is not null and sourcedata = 'O14'      minus      select SOURCE_DATA, PR_NUMBER, PR_CREATION_DATE, PR_STATUS, DESCRIPTION, PR_LINE_NUM, PR_ITEM_CODE, LINE_CANCEL_FLAG, REQUISITION_HEADER_ID, INV_ORG_ID, REQUESTOR_ID, ORG_ID from xpr) X"

        cur.execute(sql)

        cur.close()
        con.commit()
        con.close()
