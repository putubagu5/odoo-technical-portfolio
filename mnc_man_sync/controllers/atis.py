# -*- coding: utf-8 -*-

import json
import werkzeug
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.web import Home
from odoo.exceptions import UserError, ValidationError, AccessError, MissingError, AccessDenied
from odoo import api, fields, models, _, tools

import logging

_logger = logging.getLogger(__name__)


class ManSyncAtis(Home):

    @http.route('/push_data_to_atis_ora/<string:token>/', type='http', auth='public', website=False, sitemap=False)
    def push_data_to_atis_ora(self, token, **kwargs):
        print('TOKEN : ' + token)
        # ke menu update apps
        # http://localhost:8062/web#action=35&model=ir.module.module&view_type=kanban&cids=&menu_id=5
        # how to test
        # http://localhost:8062/push_data_to_atis_ora/BZBSUSHKVSKJZSC2356234560937657098KSBLDEKBSLKEBTLKHSJ9AE14431CCE24BF53F5F13A486549006506D
        # http://localhost:8062/push_data_to_atis_ora/tKbU433AIAvXFGsbARWKnuNac18Oga9oNl9gmcmmY4WA1b9697PdxU1Bh6zs7NuCprtBqeILJ5CPOmmJ6Wbv4VhA3

        # if token == 'BZBSUSHKVSKJZSC2356234560937657098KSBLDEKBSLKEBTLKHSJ9AE14431CCE24BF53F5F13A486549006506D':
        # return request.env.cr.dbname

        # get token from mnc token management -> model r12.po.receives
        # get token from Database
        print(request.env['mnc.token.management'].get_token('r12.po.receives'))

        if request.env['mnc.token.management'].get_token('r12.po.receives') == token:
            # ini dijalankan per request . dari sisi oracle .
            request.env['r12.po.receives'].send_all_to_atis()
            # sync_log_id = request.env['r12.po.receives'].fill_odoo_staging_table()
            # request.env['r12.po.receives'].push_data_to_atis(sync_log_id.id)
            # request.env['r12.po.receives'].count_data_from_atis(sync_log_id.id)

        return 'OK'
