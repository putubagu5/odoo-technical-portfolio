from odoo import api, fields, models, _, tools
from datetime import date, datetime
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class XItem(models.Model):
    _name = 'x.item'
    _description = 'xitem - Odoo Staging Table - prepared for ATIS - Oracle Staging'

    source_data = fields.Char(string="Source Data")
    itemcode = fields.Char(string="Item Code")
    description = fields.Char(string="Description")
    inventory_item_id = fields.Integer(string="Inventory Item ID")
    inv_organization_id = fields.Integer(string="Inventory Organization ID")
    org_id = fields.Integer(string="Organization ID")
    #
    sync_log_id = fields.Many2one('mnc.sync.logger', String="Sync Logger", required=True)
    curr_steps = fields.Integer(string="Current Steps")
    total_steps = fields.Integer(string="Total Steps")

    def create_odoo_stg(self, loc_id):
        _logger.info('posisi di : create_in_odoo_stg')
        _logger.info(loc_id)

        sl_ids = self.env['product.product'].search([
            ('id', '=', loc_id),
        ])

        msl_id = self.env['mnc.sync.logger'].create({
            'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'model_name': self._name,
            'step01_activity': 'Create Row Data in Odoo Staging',
            'step01_desc': 'Create Row Data in Odoo Staging',
            'step01_source': 'odoo',
            'step01_target': 'odoo_stg',
            'step01_start_time': datetime.now(),
            'step01_end_time': False,
            'step01_caller': self._name + '.create_odoo_stg',
            'step01_count': 0,
            'curr_steps': 1,
            'total_steps': 2,
        })

        fetch_cnt = 0
        vals = {}
        for sl in sl_ids:
            sourcedata = 'O14'
            # _logger.info('hai bos 3')
            # _logger.info(sl.product_tmpl_id.id)
            # _logger.info(sl.product_tmpl_id.company_id.id)

            stock_loc_ids = self.env['stock.location'].search([
                ('active', '=', True),
                ('usage', '=', 'internal'),
                ('barcode', '!=', False),
                ('company_id', '=', 1),
            ], limit=1)

            inv_organization_id = org_id = False
            for stock_loc in stock_loc_ids:
                inv_organization_id = stock_loc.id
                org_id = stock_loc.company_id.org_id

            vals = {
                'source_data': sourcedata,
                'itemcode': sl.product_tmpl_id.default_code,
                'description': sl.product_tmpl_id.name,
                'inventory_item_id': sl.id,
                'inv_organization_id': inv_organization_id,
                'org_id': org_id,
                'sync_log_id': msl_id.id
            }

            fetch_cnt += 1

            self.env['x.item'].sudo().create(vals)

        #

        msl_ids = self.env['mnc.sync.logger'].search([("id", "=", msl_id.id)])
        for msl_data in msl_ids:
            msl_data.write({'step01_end_time': datetime.now(),
                            'step01_count': fetch_cnt,
                            })

        return msl_id

    def create_push_to_atis(self, sync_log_id):
        _logger.info('posisi di create_push_to_atis')
        _logger.info(sync_log_id)

        log_ids = self.env['mnc.sync.logger'].search([
            ('id', '=', sync_log_id),
        ])

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
                'step02_caller': self._name + '.create_push_to_atis',
                'step02_count': 0,
                'curr_steps': 2,
                #
            })

            line_ids = self.env['x.item'].search([
                ('sync_log_id', '=', log_id.id),
            ])

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
                line.curr_steps = 2

                send_cnt += 1
                sql = "insert into XITEM ( SOURCE_DATA, ITEMCODE, DESCRIPTION, INVENTORY_ITEM_ID, INV_ORGANIZATION_ID, ORG_ID, ODOO_LOG_ID) values ( :source_data, :itemcode, :description, :inv_item_id, :inv_org_id, :org_id, :odoo_log_id)"

                cur.execute(sql, {'source_data': line.source_data, 'itemcode': line.itemcode,
                                  'description': line.description, 'inv_item_id': line.inventory_item_id,
                                  'inv_org_id': line.inv_organization_id, 'org_id': line.org_id,
                                  'odoo_log_id': sync_log_id})

            cur.close()
            con.commit()
            con.close()

            log_id.write({'step02_end_time': datetime.now(),
                          'step02_count': send_cnt,
                          })

    def write_odoo_stg(self, loc_id):
        _logger.info('posisi di : write_odoo_stg')
        _logger.info(loc_id)

        sl_ids = self.env['product.product'].search([
            ('id', '=', loc_id),
        ])

        msl_id = self.env['mnc.sync.logger'].create({
            'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'model_name': self._name,
            'step01_activity': 'Write Row Data in Odoo Staging',
            'step01_desc': 'Write Row Data in Odoo Staging',
            'step01_source': 'odoo',
            'step01_target': 'odoo_stg',
            'step01_start_time': datetime.now(),
            'step01_end_time': False,
            'step01_caller': self._name + '.write_odoo_stg',
            'step01_count': 0,
            'curr_steps': 1,
            'total_steps': 2,
        })

        fetch_cnt = 0
        vals = {}
        for sl in sl_ids:

            sourcedata = 'O14'
            # _logger.info('hai bos 2')
            # _logger.info(sl.product_tmpl_id.id)
            # _logger.info(sl.product_tmpl_id.company_id.id)

            stock_loc_ids = self.env['stock.location'].search([
                ('active', '=', True),
                ('usage', '=', 'internal'),
                ('barcode', '!=', False),
                ('company_id', '=', 1),
            ], limit=1)

            inv_organization_id = org_id = False
            for stock_loc in stock_loc_ids:
                inv_organization_id = stock_loc.id
                org_id = stock_loc.company_id.org_id

            vals = {
                'source_data': sourcedata,
                'itemcode': sl.product_tmpl_id.default_code,
                'description': sl.product_tmpl_id.name,
                'inventory_item_id': sl.id,
                'inv_organization_id': inv_organization_id,
                'org_id': org_id,
                'sync_log_id': msl_id.id
            }

            fetch_cnt += 1

            xloc_ids = self.env['x.item'].sudo().search([("inventory_item_id", "=", sl.id)])
            for xloc_data in xloc_ids:
                xloc_data.write(vals)

        #

        msl_ids = self.env['mnc.sync.logger'].search([("id", "=", msl_id.id)])
        for msl_data in msl_ids:
            msl_data.write({'step01_end_time': datetime.now(),
                            'step01_count': fetch_cnt,
                            })

        return msl_id

    def write_push_to_atis(self, sync_log_id):
        _logger.info('posisi di write_push_to_atis')
        _logger.info(sync_log_id)

        log_ids = self.env['mnc.sync.logger'].search([
            ('id', '=', sync_log_id),
        ])

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
                'step02_caller': self._name + '.write_push_to_atis',
                'step02_count': 0,
                'curr_steps': 2,
                #
            })

            line_ids = self.env['x.item'].search([
                ('sync_log_id', '=', log_id.id),
            ])

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
                line.curr_steps = 2

                send_cnt += 1
                sql = "update XITEM set SOURCE_DATA = :source_data, ITEMCODE = :itemcode, DESCRIPTION = :description, INV_ORGANIZATION_ID = :inv_org_id, ORG_ID = :org_id, ODOO_LOG_ID = :odoo_log_id where INVENTORY_ITEM_ID = :inv_item_id"

                cur.execute(sql, {'source_data': line.source_data, 'itemcode': line.itemcode,
                                  'description': line.description, 'inv_org_id': line.inv_organization_id,
                                  'org_id': line.org_id, 'odoo_log_id': sync_log_id,
                                  'inv_item_id': line.inventory_item_id})

            cur.close()
            con.commit()
            con.close()

            log_id.write({'step02_end_time': datetime.now(),
                          'step02_count': send_cnt,
                          })

    def count_data_from_atis(self, sync_log_id):

        # a = ambil total baris data terkini dari atis
        # b = ambil total baris data terkini dari odoo
        # c = a - odoo = jumlah data yang selisih .
        # jika tidak ada selisih maka data match .

        _logger.info('posisi di count_data_from_atis')
        _logger.info(sync_log_id)

        log_ids = self.env['mnc.sync.logger'].search([
            ('id', '=', sync_log_id),
        ])

        _logger.info(log_ids)

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
                ora_atis_dsn = "arjuna.mncgroup.com:1523/rcti"
                _logger.info('default ora_atis_pass default')

            _logger.info('get data from param - done')
            # _logger.info(ora_atis_user)
            # _logger.info(ora_atis_pass)
            # _logger.info(ora_atis_dsn)

            con = cx_Oracle.connect(user=ora_atis_user, password=ora_atis_pass, dsn=ora_atis_dsn)
            # con = cx_Oracle.connect(user="GEN21_FIN_INTERFACE", password="test1ng", dsn="localhost:1521/xe")
            cur = con.cursor()

            sql = "select count(1) as total_baris from XITEM where odoo_log_id = :odoo_log_id and source_data = 'O14'"

            cur.execute(sql, {'odoo_log_id': sync_log_id})

            for result in cur:
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

    def send_all_odoo_stg(self):
        _logger.info('posisi di : send_all_odoo_stg')

        sl_ids = self.env['product.product'].search([])

        msl_id = self.env['mnc.sync.logger'].create({
            'name': self._name + '_' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'model_name': self._name,
            'step01_activity': 'Create Row Data in Odoo Staging',
            'step01_desc': 'Create Row Data in Odoo Staging',
            'step01_source': 'odoo',
            'step01_target': 'odoo_stg',
            'step01_start_time': datetime.now(),
            'step01_end_time': False,
            'step01_caller': self._name + '.create_odoo_stg',
            'step01_count': 0,
            'curr_steps': 1,
            'total_steps': 2,
        })

        fetch_cnt = 0
        vals = {}
        for sl in sl_ids:
            sourcedata = 'O14'

            # _logger.info('hai bos')
            # _logger.info(sl.product_tmpl_id.id)
            # _logger.info(sl.product_tmpl_id.company_id.id)

            stock_loc_ids = self.env['stock.location'].search([
                ('active', '=', True),
                ('usage', '=', 'internal'),
                ('barcode', '!=', False),
                ('company_id', '=', 1),
            ], limit=1)

            inv_organization_id = org_id = False
            for stock_loc in stock_loc_ids:
                inv_organization_id = stock_loc.id
                org_id = stock_loc.company_id.org_id

            vals = {
                'source_data': sourcedata,
                'itemcode': sl.product_tmpl_id.default_code,
                'description': sl.product_tmpl_id.name,
                'inventory_item_id': sl.id,
                'inv_organization_id': inv_organization_id,
                'org_id': org_id,
                'sync_log_id': msl_id.id
            }

            fetch_cnt += 1

            self.env['x.item'].sudo().create(vals)

        #

        msl_ids = self.env['mnc.sync.logger'].search([("id", "=", msl_id.id)])
        for msl_data in msl_ids:
            msl_data.write({'step01_end_time': datetime.now(),
                            'step01_count': fetch_cnt,
                            })

        return msl_id

    def send_all_to_atis(self):
        _logger.info('posisi di send_all_to_atis')
        _logger.info('first time only - run this via odoo scheduler - ir.cron ')
        sync_log_id = self.sudo().send_all_odoo_stg()
        self.sudo().create_push_to_atis(sync_log_id.id)
        self.sudo().count_data_from_atis(sync_log_id.id)
