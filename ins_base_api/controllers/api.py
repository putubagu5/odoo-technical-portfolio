from odoo import http, tools, fields, api, _
from datetime import datetime, date
from odoo.http import request
import json
import logging
import functools
import datetime
import json
_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        vals = request.jsonrequest
        if 'auth' in vals:
            api_key = vals['auth']
            if api_key:
                request.uid = 1
                auth_api_key = request.env["res.api.key"]._retrieve_api_key(
                    api_key
                )

                try:
                    db_name = tools.config['api_db']
                except:
                    return {'status': 403, 'message': '`api_db` not found in your odoo configuration file.'}
                request.env.db = db_name  # force feed db_name

                if auth_api_key:
                    request._env = None
                    request.uid = auth_api_key.user_id.id
                    request.auth_api_key = api_key
                    request.auth_api_key_id = auth_api_key.id
                    return func(self, *args, **kwargs)
                return {'status': 401, 'message': "access denied", 'data': []}
            return {'status': 401, 'message': "access denied", 'data': []}
        else:
            return {'status': 401, 'message': "missing access token in request body", 'data': []}
    return wrap


class Api(http.Controller):

    def _convert_datetime_str(self, date_convert):
        date_val = date_convert.replace(" ", "")
        date_str = date_val[:10] + ' ' + date_val[10:18]
        return date_str

    def _get_key_invoice_ar(self):
        return [
            'org_id',
            'cust_type',
            'adv_source',
            'channel',
            'channel_name',
            'region',
            'region_name',
            'agen_code',
            'agen_name',
            'client_code',
            'client_name',
            'invoice_no',
            'invoice_date',
            'inv_yy',
            'po_no',
            'mo_no',
            'po_type',
            'ae_name',
            'prod_name',
            'pab_pbb',
            'generation_date',
            'rowid_inv',
            'total_spots',
            'total_gross',
            'agency_disc',
            'agency_comm',
            'total_net',
            'perc_tax',
            'total_tax',
            'update_user',
            'update_date',
            'attribute1',
            'cust_ref',
            'site',
            'send_flag',
            'senddate',
            'ccid',
            'gl_date',
            'region_line_code',
            'region_line_name',
            'period',
            'company_code',
            'wilayah'
        ]

    def _get_key_invoice_trading(self):
        return [
            'user_je_category_name',
            'user_je_source_name',
            'status',
            'accounted_cr',
            'accounted_dr',
            'accounting_date',
            'actual_flag',
            'attribute1',
            'attribute2',
            'attribute3',
            'attribute4',
            'attribute5',
            'attribute6',
            'attribute7',
            'attribute8',
            'created_by',
            'currency_code',
            'currency_conversion_date',
            'currency_conversion_rate',
            'date_created',
            'entered_cr',
            'entered_dr',
            'group_id',
            'ledger_id',
            'period_name',
            'rec_number',
            'reference1',
            'reference10',
            'reference2',
            'reference4',
            'reference5',
            'segment1',
            'segment2',
            'segment3',
            'segment4',
            'segment5',
            'segment6',
            'send_date',
            'send_flag',
            'send_flag_od',
            'update_date',
            'update_user',
            'user_currency_conversion_type'
        ]

    def _get_key_inventory_costs(self):
        return [
            'user_je_category_name',
            'user_je_source_name',
            'status',
            'accounted_cr',
            'accounted_dr',
            'accounting_date',
            'actual_flag',
            'attribute1',
            'attribute2',
            'attribute3',
            'attribute4',
            'attribute5',
            'attribute6',
            'attribute7',
            'attribute8',
            'created_by',
            'currency_code',
            'currency_conversion_date',
            'currency_conversion_rate',
            'date_created',
            'entered_cr',
            'entered_dr',
            'group_id',
            'ledger_id',
            'period_name',
            'rec_number',
            'reference1',
            'reference10',
            'reference2',
            'reference4',
            'reference5',
            'segment1',
            'segment2',
            'segment3',
            'segment4',
            'segment5',
            'segment6',
            'send_date',
            'send_flag',
            'send_flag_od',
            'update_date',
            'update_user',
            'user_currency_conversion_type'
        ]

    def _get_key_usage_costs(self):
        return [
            'user_je_category_name',
            'user_je_source_name',
            'status',
            'accounted_cr',
            'accounted_dr',
            'accounting_date',
            'actual_flag',
            'attribute1',
            'attribute2',
            'attribute3',
            'attribute4',
            'attribute5',
            'attribute6',
            'attribute7',
            'attribute8',
            'created_by',
            'currency_code',
            'currency_conversion_date',
            'currency_conversion_rate',
            'date_created',
            'entered_cr',
            'entered_dr',
            'group_id',
            'ledger_id',
            'period_name',
            'rec_number',
            'reference1',
            'reference10',
            'reference2',
            'reference4',
            'reference5',
            'segment1',
            'segment2',
            'segment3',
            'segment4',
            'segment5',
            'segment6',
            'send_date',
            'send_flag',
            'send_flag_od',
            'update_date',
            'update_user',
            'user_currency_conversion_type'
        ]

    def _get_key_program_costs(self):
        return [
            # 'transaction_id',
            # 'interface_source_code',
            # 'source_type_code',
            # 'requisition_type',
            # 'destination_type_code',
            'quantity',
            # 'uom_code',
            'unit_price',
            # 'currency_unit_price',
            # 'authorization_status',
            # 'group_code',
            # 'header_attribute_category',
            'header_attribute1',
            'header_attribute2',
            'header_attribute3',
            'header_attribute4',
            'header_attribute5',
            # 'header_attribute6',
            # 'deliver_to_location_id',
            # 'item_segment1',
            'item_description',
            # 'destination_organization_code',
            # 'destination_subinventory',
            # 'need_by_date',
            'gl_date',
            'org_id',
            # 'deliver_to_requestor_id',
            'preparer_id',
            'suggested_buyer_id',
            # 'suggested_vendor_id',
            # 'suggested_vendor_name',
            # 'charge_account_id',
            # 'variance_account_id',
            # 'budget_account_id',
            'currency_code',
            # 'rate',
            # 'rate_type',
            # 'charge_account_segment1',
            # 'charge_account_segment2',
            # 'charge_account_segment3',
            # 'charge_account_segment4',
            # 'charge_account_segment5',
            # 'charge_account_segment6',
            'last_update_date',
            'last_updated_by',
            'rate_date',
            # 'line_attribute15',
            # 'line_attribute_category'
        ]

    def check_keys(self, keys, vals):
        result = False
        for rec in keys:
            if rec in vals:
                result = True
            else:
                result = False
                break
        return result

    def check_keys_multiple(self, keys, vals):
        result = True
        for rec in keys:
            for val in vals:
                if rec in val:
                    result = True
                else:
                    result = False
                    return
        return result

    def api_response(self, message, data, status_code):
        res = {'status': status_code, 'message': message, 'data': data}
        return res

    @http.route(['/mnc_erp/getToken'], auth="none", type='json', csrf=False)
    def user_authenticate(self, **values):
        try:
            db_name = tools.config['api_db']
        except:
            return self.api_response("`api_db` not found in your odoo configuration file.", [], 401)
        username = request.jsonrequest.get('username','0')
        password = request.jsonrequest.get('password','0')
        testLogin = False
        try:
            testLogin = request.session.authenticate(db_name, username, password)
        except:
            return self.api_response("Forbidden Access", [], 401)
        if testLogin != False:
            getToken = request.env['res.api.key']._retrieve_api_by_username(username)
            return self.api_response("Client API", {'token': getToken}, 200)
        else:
            return self.api_response("Forbidden Access", [], 401)

    @validate_token
    @http.route('/mnc_erp/delToken', auth="none", type="json", methods=['POST'], csrf=False)
    def user_unauthenticate(self, **kw):
        res = request.env['res.api.key']._del_token_key(request.uid)
        if res:
            return self.api_response("Success Delete Token", [], 200)
        else:
            return self.api_response("Failed Delete Token", [], 401)

    @validate_token
    @http.route('/mnc_erp/customers', auth="none", type="json", methods=['POST'], csrf=False)
    def get_customers(self, **kw):
        vals = request.jsonrequest
        keys = ['name', 'org_id']
        # check if all keys are in vals
        if all(x in vals for x in keys):
            domain = [
                #('customer_rank', '!=', 0),
                #('active', '=', True),
                ('type', '=', 'customer')
            ]
            if vals['name'] != "":
                domain += [
                    ('alternatif_name', 'ilike', vals['name'])
                ]
            if vals['org_id'] != "":
                domain += [
                    ('company_id.org_id', '=', vals['org_id'])
                ]

            customers_rec = request.env['res.sites'].search(domain)
            customers = []
            for rec in customers_rec:
                # full_address = False
                # if rec.full_address:
                #     full_address = (rec.full_address[:146] + '..') if len(rec.full_address) > 150 else rec.full_address
                #if rec.partner_no:
                #    vendor_site = False
                #    if rec.site_ids:
                #        for site in rec.site_ids:
                #            if site.code:
                #                vendor_site = site.code
                #                break
                    values = {
                        'ORG_ID': rec.company_id.org_id,
                        'CUSTOMER_CODE': rec.site_number,
                        'CUSTOMER_SITE': rec.code,
                        'PARTY_NAME': rec.partner_id.partner_type_id.name,
                        'PHONETIC_NAME': rec.alternatif_name,
                        'BILL_ADDRESS1': rec.site_address,
                        'BILL_ADDRESS2': "",
                        'BILL_ADDRESS3': "",
                        'TAX_ID': rec.tax_npwp,
                        'TAX_ADDRESS1': rec.tax_address,
                        'TAX_ADDRESS2': "",
                        'TAX_ADDRESS3': "",
                        'SHIP_ADDRESS1': rec.delivery_address,
                        'SHIP_ADDRESS2': "",
                        'SHIP_ADDRESS3': ""
                    }
                    customers.append(values)
            return self.api_response("Success Get Customers", customers, 200)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/currencies', auth="none", type="json", methods=['POST'], csrf=False)
    def get_currencies(self, **kw):
        vals = request.jsonrequest
        keys = ['date_from', 'date_to']
        if self.check_keys(keys, vals):
            currencies_rec = request.env['res.currency'].search([])
            currencies = []
            for rec in currencies_rec:
                if rec.actual_rate_date:
                    date_from = datetime.datetime.strptime(vals['date_from'], "%Y-%m-%d").date()
                    date_to = datetime.datetime.strptime(vals['date_to'], "%Y-%m-%d").date()
                    if (rec.actual_rate_date >= date_from) and (rec.actual_rate_date <= date_to):
                        values = {
                            'CURRENCY_CODE': rec.name,
                            'CONVERSION_DATE': rec.actual_rate_date,
                            'CONVERSION_RATE': rec.actual_rate,
                        }
                        currencies.append(values)
            return self.api_response("Success Get Currencies", currencies, 200)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/invoice/ebilling', auth="none", type="json", methods=['POST'], csrf=False)
    def get_invoice_all(self, **kw):
        vals = request.jsonrequest
        keys = ['date_from', 'date_to', 'org_id']
        if self.check_keys(keys, vals):
            filter = [
                ('invoice_date', '>=', vals['date_from']),
                ('invoice_date', '<=', vals['date_to']),
                ('move_type', '=', 'out_invoice'),
                ('source_type_gen21', '=', 'iklan_bms')
            ]
            if vals['org_id'] != '':
                filter.append(('company_id.org_id', '=', vals['org_id']))

            account_move_rec = request.env['account.move'].search(filter)
            account_move = []
            for rec in account_move_rec:
                agen_code = False
                agen_name = False
                values = {
                    'ORG_ID': rec.company_id.org_id,
                    'CUST_TYPE': rec.customer_type_gen21,
                    'ADV_SOURCE': rec.advertiser_gen21,
                    'CHANNEL': rec.channel_code_gen21,
                    'CHANNEL_NAME': rec.channel_name_gen21,
                    'REGION': rec.code_region_gen21,
                    'REGION_NAME': rec.name_region_gen21,
                    'AGEN_CODE': agen_code,
                    'AGEN_NAME': agen_name,
                    'CLIENT_CODE': rec.partner_id.partner_no,
                    'CLIENT_NAME': rec.partner_id.name,
                    'INVOICE_NO': rec.payment_reference,
                    'INVOICE_DATE': rec.invoice_date,
                    'INV_YY': rec.invoice_date.strftime("%y%m") if rec.invoice_date else False,
                    'PO_NO': rec.po_numbers_gen21,
                    'MO_NO': rec.mo_numbers_gen21,
                    'PO_TYPE': rec.po_type_gen21,
                    'AE_NAME': rec.sales_person_gen21,
                    'PROD_NAME': rec.invoice_line_ids[0].name if len(rec.invoice_line_ids) > 0 else False,
                    'PAB_PBB': rec.pab_pbb_gen21,
                    'GENERATION_DATE': rec.create_date,
                    'ROWID_INV': rec.invoice_line_ids[0].purchase_line_number if len(rec.invoice_line_ids) > 0 else False,
                    'TOTAL_SPOTS': rec.invoice_line_ids[0].total_spots_gen21 if len(rec.invoice_line_ids) > 0 else False,
                    'TOTAL_GROSS': rec.invoice_line_ids[0].total_gross_gen21 if len(rec.invoice_line_ids) > 0 else False,
                    'AGENCY_DISC': rec.invoice_line_ids[0].agency_discount_gen21 if len(rec.invoice_line_ids) > 0 else False,
                    'AGENCY_COMM': rec.invoice_line_ids[0].agency_commision_gen21 if len(rec.invoice_line_ids) > 0 else False,
                    'TOTAL_NET': rec.amount_total,
                    'PERC_TAX': False,
                    'TOTAL_TAX': False,
                    'UPDATE_USER': rec.invoice_user_id.name,
                    'UPDATE_DATE': rec.write_date,
                    'ATTRIBUTE1': rec.status_transfer_oracle_gen21,
                    'CUST_REF': rec.customer_ref_gen21,
                    'SITE': rec.code_site_gen21,
                    'SEND_FLAG': rec.send_flag_gen21,
                    'SENDDATE': rec.send_date_gen21,
                    'CCID': rec.ccid_gen21,
                    'GL_DATE': rec.date,
                    'REGION_LINE_CODE': rec.code_region_line_gen21,
                    'REGION_LINE_NAME': rec.name_region_line_gen21,
                    'PERIOD': rec.period_id.name,
                    'COMPANY_CODE': rec.code_company_gen21,
                    'WILAYAH': rec.wilayah_gen21
                }

                if rec.amount_by_group:
                    percent_amount = 0
                    total_amount_tax = 0
                    for percent in rec.amount_by_group:
                        if percent[0] == 'Taxes':
                            percent_amount += percent[1]
                            total_amount_tax += percent[1]
                    if percent_amount != 0:
                        values['PERC_TAX'] = (percent_amount / rec.amount_untaxed) * 100
                    if total_amount_tax != 0:
                        values['TOTAL_TAX'] = total_amount_tax
                account_move.append(values)
            return self.api_response("Success Get Invoice All", account_move, 200)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/purchase/request', auth="none", type="json", methods=['POST'], csrf=False)
    def get_purchase_request_all(self, **kw):
        vals = request.jsonrequest
        keys = ['uniqkey', 'org_id']
        if self.check_keys(keys, vals):
            filter = []
            if vals['org_id'] != '':
                filter.append(('program_costs_id_gen21.company_id.org_id', '=', vals['org_id']))

            if vals['uniqkey'] != '':
                filter.append(('uniqkey', '=', vals['uniqkey']))

            purchase_request_line_rec = request.env['program.costs.line.gen21'].search(filter)
            purchase_request = []
            for rec in purchase_request_line_rec:
                values = {
                    'uniqkey': rec.uniqkey,
                    'status': rec.state,
                }
                purchase_request.append(values)
            return self.api_response("Success Get Purchase Request", purchase_request, 200)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/invoice/cndn', auth="none", type="json", methods=['POST'], csrf=False)
    def get_invoice_cndn(self, **kw):
        vals = request.jsonrequest
        keys = ['org_id', 'ar_type', 'source', 'trx_type', 'from_date', 'to_date']
        if self.check_keys(keys, vals):
            filter = [
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ]

            if vals['org_id'] != '':
                filter.append(('company_id.org_id', '=', vals['org_id']))

            if vals['ar_type'] != '':
                filter.append(('ar_receipt_type', '=', vals['ar_type'].lower()))

            if vals['trx_type'] != '':
                filter.append(('transaction_type_id.code_gen21', 'ilike', vals['trx_type']))

            if vals['source'] != '':
                filter.append(('source_type_gen21', '=', vals['source'].lower()))

            if vals['from_date'] != '':
                filter.append(('invoice_date', '>=', vals['from_date']))

            if vals['to_date'] != '':
                filter.append(('invoice_date', '<=', vals['to_date']))

            account_move_rec = request.env['account.move'].search(filter)
            account_move = []
            for rec in account_move_rec:
                if rec.move_type == 'out_invoice':
                    values = {
                        'ORG_ID': rec.company_id.org_id,
                        'AR_TYPE': rec.ar_receipt_type,
                        'SOURCE': rec.source_type_gen21,
                        'TRX_TYPE': rec.transaction_type_id.name,
                        'TRX_NUMBER': rec.payment_reference,
                        'MO_NUMBER': rec.mo_numbers_gen21,
                        'TRX_DATE': rec.invoice_date,
                        'AMOUNT': rec.amount_total,
                        'VREF_1': False,
                        'NUMREF_1': False,
                        'DATEREF_1': False,
                        'LINES': []
                    }
                    if len(rec.invoice_line_ids) > 0:
                        for line in rec.invoice_line_ids:
                            values['LINES'].append({
                                'ACCOUNT': line.account_id.code + ' ' + line.account_id.name,
                                'LABEL': line.name,
                                'TOTAL_SPOTS': line.total_spots_gen21,
                                'TOTAL_GROSS': line.total_gross_gen21,
                                'DISCOUNT_AGENCY': line.agency_discount_gen21,
                                'SUBTOTAL': line.price_unit,
                            })
                if rec.move_type == 'out_refund':
                    values = {
                        'ORG_ID': rec.company_id.org_id,
                        'AR_TYPE': rec.ar_receipt_type,
                        'SOURCE': rec.source_type_gen21,
                        'TRX_TYPE': rec.transaction_type_id.name,
                        'TRX_NUMBER': rec.payment_reference,
                        'MO_NUMBER': rec.mo_numbers_gen21,
                        'TRX_DATE': rec.invoice_date,
                        'AMOUNT': rec.amount_total,
                        'VREF_1': False,
                        'NUMREF_1': False,
                        'DATEREF_1': False,
                        'LINES': []
                    }
                    if len(rec.invoice_line_ids) > 0:
                        for line in rec.invoice_line_ids:
                            values['LINES'].append({
                                'ACCOUNT': line.account_id.code + ' ' + line.account_id.name,
                                'LABEL': line.name,
                                'TOTAL_SPOTS': line.total_spots_gen21,
                                'TOTAL_GROSS': line.total_gross_gen21,
                                'DISCOUNT_AGENCY': line.agency_discount_gen21,
                                'SUBTOTAL': line.price_unit,
                            })
                account_move.append(values)
            return self.api_response("Success Get Invoice CNDN", account_move, 200)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/invoice/ar', auth="none", type="json", methods=['POST'], csrf=False)
    def post_invoice_ar(self, **kw):
        vals = request.jsonrequest
        keys = self._get_key_invoice_ar()
        keys2 = ['name', 'invoices']
        if self.check_keys(keys2, vals):
            data_invoice = json.loads(vals['invoices'])
            if self.check_keys_multiple(keys, data_invoice):
                check_ar_posted = request.env['account.move.ar.gen21'].search([('name', '=', vals['name']), ('state', '=', 'posted')])
                if not check_ar_posted:
                    check_ar = request.env['account.move.ar.gen21'].search([('name', '=', vals['name']), ('state', '!=', 'posted')])
                    if check_ar:
                        check_ar.unlink()
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name':vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_invoice:
                            if not company_id:
                                data_company = request.env['res.company'].search([('org_id', '=', val['org_id'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_ar = request.env['account.move'].search([('company_id.org_id', '=', val_data['org_id']), ('name', '=', val_data['invoice_no'])])
                            if move_ar:
                                return self.api_response("Can't duplicated invoice ar, invoice no : " + val_data['invoice_no'], [], 500)
                            data_return['line_ids'].append({'org_id': val_data['org_id'], 'invoice_no': val_data['invoice_no']})
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        account_move_ar_gen21 = request.env['account.move.ar.gen21'].create(data)
                        if account_move_ar_gen21:
                            return self.api_response("Success Create Invoice Ar Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Invoice Ar Gen21", [], 500)
                    else:
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name': vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_invoice:
                            if not company_id:
                                data_company = request.env['res.company'].search([('org_id', '=', val['org_id'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_ar = request.env['account.move'].search([('company_id.org_id', '=', val_data['org_id']), ('name', '=', val_data['invoice_no'])])
                            if move_ar:
                                return self.api_response("Can't duplicated invoice ar, invoice no : " + val_data['invoice_no'], [], 500)
                            data_return['line_ids'].append({'org_id': val_data['org_id'], 'invoice_no': val_data['invoice_no']})
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        account_move_ar_gen21 = request.env['account.move.ar.gen21'].create(data)
                        if account_move_ar_gen21:
                            return self.api_response("Success Create Invoice Ar Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Invoice Ar Gen21", [], 500)
                else:
                    return self.api_response("Failed Create Invoice Ar Status Posted In Odoo, check name !", [], 500)
            else:
                return self.api_response("Check request body", [], 500)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/invoice/trading', auth="none", type="json", methods=['POST'], csrf=False)
    def post_invoice_trading(self, **kw):
        vals = request.jsonrequest
        keys = self._get_key_invoice_trading()
        keys2 = ['name', 'invoices']
        if self.check_keys(keys2, vals):
            data_invoice = json.loads(vals['invoices'])
            if self.check_keys_multiple(keys, data_invoice):
                check_trading_posted = request.env['account.move.trading.gen21'].search([('name', '=', vals['name']), ('state', '=', 'posted')])
                if not check_trading_posted:
                    check_trading = request.env['account.move.trading.gen21'].search([('name', '=', vals['name']), ('state', '!=', 'posted')])
                    if check_trading:
                        check_trading.unlink()
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name':vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_invoice:
                            if not company_id:
                                data_company = request.env['res.company'].search([('company_code', '=', val['segment1'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_trading = request.env['account.move'].search([('move_type', '=', 'entry'), ('name', '=', val_data['reference1'] + '-' + vals['name']), ('state', '!=', 'cancel')])
                            if move_trading:
                                return self.api_response("Can't duplicated invoice trading", [], 500)
                            val_return = {
                                'ledger_id': val_data['ledger_id'],
                                'reference1': val_data['reference1'],
                                'user_je_category_name': val_data['user_je_category_name'],
                                'period_name': val_data['period_name'],
                                'accounting_date': val_data['accounting_date'],
                                'attribute1': val_data['attribute1'],
                                'attribute2': val_data['attribute2'],
                                'attribute4': val_data['attribute4']
                            }
                            data_return['line_ids'].append(val_return)
                            if 'send_date' in val_data:
                                del val_data['send_date']
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        account_move_trading_gen21 = request.env['account.move.trading.gen21'].create(data)
                        if account_move_trading_gen21:
                            return self.api_response("Success Create Invoice Trading Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Invoice Trading Gen21", [], 500)
                    else:
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name': vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_invoice:
                            if not company_id:
                                data_company = request.env['res.company'].search([('company_code', '=', val['segment1'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_trading = request.env['account.move'].search([('move_type', '=', 'entry'), ('name', '=', val_data['reference1'] + '-' + vals['name']), ('state', '!=', 'cancel')])
                            if move_trading:
                                return self.api_response("Can't duplicated invoice trading", [], 500)
                            val_return = {
                                'ledger_id': val_data['ledger_id'],
                                'reference1': val_data['reference1'],
                                'user_je_category_name': val_data['user_je_category_name'],
                                'period_name': val_data['period_name'],
                                'accounting_date': val_data['accounting_date'],
                                'attribute1': val_data['attribute1'],
                                'attribute2': val_data['attribute2'],
                                'attribute4': val_data['attribute4']
                            }
                            data_return['line_ids'].append(val_return)
                            if 'send_date' in val_data:
                                del val_data['send_date']
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        account_move_trading_gen21 = request.env['account.move.trading.gen21'].create(data)
                        if account_move_trading_gen21:
                            return self.api_response("Success Create Invoice Trading Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Invoice Trading Gen21", [], 500)
                else:
                    return self.api_response("Failed Create Invoice trading Ttatus Posted In Odoo", [], 500)
            else:
                return self.api_response("Check request body", [], 500)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/inventory/costs', auth="none", type="json", methods=['POST'], csrf=False)
    def post_inventory_costs(self, **kw):
        vals = request.jsonrequest
        keys = self._get_key_inventory_costs()
        keys2 = ['name', 'data']
        if self.check_keys(keys2, vals):
            data_inventory = json.loads(vals['data'])
            if self.check_keys_multiple(keys, data_inventory):
                check_inventory_posted = request.env['inventory.costs.gen21'].search([('name', '=', vals['name']), ('state', '=', 'posted')])
                if not check_inventory_posted:
                    check_inventory = request.env['inventory.costs.gen21'].search([('name', '=', vals['name']), ('state', '!=', 'posted')])
                    if check_inventory:
                        check_inventory.unlink()
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name':vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_inventory:
                            if not company_id:
                                data_company = request.env['res.company'].search([('company_code', '=', val['segment1'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_inventory = request.env['account.move'].search([('move_type', '=', 'entry'), ('name', '=', val_data['reference1'] + '-' + vals['name']), ('state', '!=', 'cancel')])
                            if move_inventory:
                                return self.api_response("Can't duplicated inventory costs", [], 500)
                            val_return = {
                                'ledger_id': val_data['ledger_id'],
                                'user_je_category_name': val_data['user_je_category_name'],
                                'uniqkey': val_data['uniqkey'],
                            }
                            data_return['line_ids'].append(val_return)
                            if 'send_date' in val_data:
                                del val_data['send_date']
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        inventory_costs_gen21 = request.env['inventory.costs.gen21'].create(data)
                        if inventory_costs_gen21:
                            return self.api_response("Success Create Inventory Costs Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Inventory Costs Gen21", [], 500)
                    else:
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name': vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_inventory:
                            if not company_id:
                                data_company = request.env['res.company'].search([('company_code', '=', val['segment1'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_inventory = request.env['account.move'].search([('move_type', '=', 'entry'), ('name', '=', val_data['reference1'] + '-' + vals['name']), ('state', '!=', 'cancel')])
                            if move_inventory:
                                return self.api_response("Can't duplicated inventory costs", [], 500)
                            val_return = {
                                'ledger_id': val_data['ledger_id'],
                                'user_je_category_name': val_data['user_je_category_name'],
                                'uniqkey': val_data['uniqkey'],
                            }
                            data_return['line_ids'].append(val_return)
                            if 'send_date' in val_data:
                                del val_data['send_date']
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        inventory_costs_gen21 = request.env['inventory.costs.gen21'].create(data)
                        if inventory_costs_gen21:
                            return self.api_response("Success Create Inventory Costs Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Inventory Costs Gen21", [], 500)
                else:
                    return self.api_response("Failed Create Inventory Costs Status Posted In Odoo", [], 500)
            else:
                return self.api_response("Check request body", [], 500)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/usage/costs', auth="none", type="json", methods=['POST'], csrf=False)
    def post_usage_costs(self, **kw):
        vals = request.jsonrequest
        keys = self._get_key_usage_costs()
        keys2 = ['name', 'data']
        if self.check_keys(keys2, vals):
            data_usage = json.loads(vals['data'])
            if self.check_keys_multiple(keys, data_usage):
                check_usage_posted = request.env['usage.costs.gen21'].search([('name', '=', vals['name']), ('state', '=', 'posted')])
                if not check_usage_posted:
                    check_usage = request.env['usage.costs.gen21'].search([('name', '=', vals['name']), ('state', '!=', 'posted')])
                    if check_usage:
                        check_usage.unlink()
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name':vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_usage:
                            if not company_id:
                                data_company = request.env['res.company'].search([('company_code', '=', val['segment1'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_usage = request.env['account.move'].search([('move_type', '=', 'entry'), ('name', '=', val_data['reference1'] + '-' + vals['name']), ('state', '!=', 'cancel')])
                            if move_usage:
                                return self.api_response("Can't duplicated usage costs", [], 500)
                            val_return = {
                                'ledger_id': val_data['ledger_id'],
                                'user_je_category_name': val_data['user_je_category_name'],
                                'uniqkey': val_data['uniqkey'],
                            }
                            data_return['line_ids'].append(val_return)
                            if 'send_date' in val_data:
                                del val_data['send_date']
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        usage_costs_gen21 = request.env['usage.costs.gen21'].create(data)
                        if usage_costs_gen21:
                            return self.api_response("Success Create Usage Costs Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Usage Costs Gen21", [], 500)
                    else:
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name': vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_usage:
                            if not company_id:
                                data_company = request.env['res.company'].search([('company_code', '=', val['segment1'])])
                                if data_company:
                                    company_id = data_company
                            val_data = {k.lower(): v for k, v in val.items()}
                            move_usage = request.env['account.move'].search([('move_type', '=', 'entry'), ('name', '=', val_data['reference1'] + '-' + vals['name']), ('state', '!=', 'cancel')])
                            if move_usage:
                                return self.api_response("Can't duplicated usage costs", [], 500)
                            val_return = {
                                'ledger_id': val_data['ledger_id'],
                                'user_je_category_name': val_data['user_je_category_name'],
                                'uniqkey': val_data['uniqkey'],
                            }
                            data_return['line_ids'].append(val_return)
                            if 'send_date' in val_data:
                                del val_data['send_date']
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        usage_costs_gen21 = request.env['usage.costs.gen21'].create(data)
                        if usage_costs_gen21:
                            return self.api_response("Success Create Usage Costs Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Usage Costs Gen21", [], 500)
                else:
                    return self.api_response("Failed Create Usage Costs Status Posted In Odoo", [], 500)
            else:
                return self.api_response("Check request body", [], 500)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/program/costs', auth="none", type="json", methods=['POST'], csrf=False)
    def post_program_costs(self, **kw):
        vals = request.jsonrequest
        keys = self._get_key_program_costs()
        keys2 = ['name', 'data']
        if self.check_keys(keys2, vals):
            data_program = json.loads(vals['data'])
            if self.check_keys_multiple(keys, data_program):
                check_program_posted = request.env['program.costs.gen21'].search([('name', '=', vals['name']), ('state', '=', 'posted')])
                if not check_program_posted:
                    check_program = request.env['program.costs.gen21'].search([('name', '=', vals['name']), ('state', '!=', 'posted')])
                    if check_program:
                        is_change = check_program.is_change
                        check_program.unlink()
                        data = {
                            'name': vals['name'],
                            'is_change': is_change,
                            'line_ids': []
                        }
                        data_return = {
                            'name':vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_program:
                            val_data = {k.lower(): v for k, v in val.items()}
                            if not company_id:
                                data_company = request.env['res.company'].search([('org_id', '=', val_data['org_id'])])
                                if data_company:
                                    company_id = data_company
                            val_data['gl_date'] = self._convert_datetime_str(val_data['gl_date']) if val_data['gl_date'] else False
                            val_data['rate_date'] = self._convert_datetime_str(val_data['rate_date']) if val_data['rate_date'] else False
                            val_data['last_update_date'] = self._convert_datetime_str(val_data['last_update_date']) if val_data['last_update_date'] else False
                            # move_program = request.env['program.costs.line.gen21'].search([('header_attribute1', '=', val_data['header_attribute1']), ('gl_date', '=', val_data['gl_date']), ('state', '!=', 'posted')])
                            # if move_program:
                            #     return self.api_response("Can't duplicated program costs", [], 500)
                            val_return = {
                                'uniqkey': val_data['uniqkey'],
                            }
                            data_return['line_ids'].append(val_return)
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        program_costs_gen21 = request.env['program.costs.gen21'].create(data)
                        if program_costs_gen21:
                            return self.api_response("Success Create Program Costs Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Program Costs Gen21", [], 500)
                    else:
                        data = {
                            'name': vals['name'],
                            'line_ids': []
                        }
                        data_return = {
                            'name': vals['name'],
                            'line_ids':[]
                        }
                        company_id = False
                        for val in data_program:
                            val_data = {k.lower(): v for k, v in val.items()}
                            if not company_id:
                                data_company = request.env['res.company'].search([('org_id', '=', val_data['org_id'])])
                                if data_company:
                                    company_id = data_company
                            val_data['gl_date'] = self._convert_datetime_str(val_data['gl_date']) if val_data['gl_date'] else False
                            val_data['rate_date'] = self._convert_datetime_str(val_data['rate_date']) if val_data['rate_date'] else False
                            val_data['last_update_date'] = self._convert_datetime_str(val_data['last_update_date']) if val_data['last_update_date'] else False
                            # move_program = request.env['program.costs.line.gen21'].search([('header_attribute1', '=', val_data['header_attribute1']), ('gl_date', '=', val_data['gl_date']), ('state', '!=', 'posted')])
                            # if move_program:
                            #     return self.api_response("Can't duplicated program costs", [], 500)
                            val_return = {
                                'uniqkey': val_data['uniqkey'],
                            }
                            data_return['line_ids'].append(val_return)
                            data['line_ids'].append((0, 0, val_data))
                        if 'auth' in vals:
                            del vals['auth']
                        if company_id:
                            data['company_id'] = company_id.id
                        program_costs_gen21 = request.env['program.costs.gen21'].create(data)
                        if program_costs_gen21:
                            return self.api_response("Success Create Program Costs Gen21", json.dumps(data_return), 200)
                        else:
                            return self.api_response("Failed Create Program Costs Gen21", [], 500)
                else:
                    return self.api_response("Failed Create Program Costs Status Posted In Odoo", [], 500)
            else:
                return self.api_response("Check request body", [], 500)
        else:
            return self.api_response("Check request body", [], 500)

    @validate_token
    @http.route('/mnc_erp/atis', auth="none", type="json", methods=['POST'], csrf=False)
    def get_atis(self, **kw):
        body = request.jsonrequest
        data = []
        keys = ['po_number', 'rr_number', 'pr_number']
        if self.check_keys(keys, body):
            filter = []
            is_po = False
            is_pr = False
            if body['rr_number'] != '' and body['po_number'] == '' and body['pr_number'] == '':
                filter.append(('name', '=', body['rr_number']))
                filter.append(('state', '=', 'done'))
                filter.append(('picking_type_id.name', '=', 'Receipts'))
            elif body['rr_number'] != '' and body['po_number'] != '' and body['pr_number'] == '':
                filter.append(('name', '=', body['rr_number']))
                filter.append(('po_numbers', '=', body['po_number']))
                filter.append(('state', '=', 'done'))
                filter.append(('picking_type_id.name', '=', 'Receipts'))
            elif body['rr_number'] != '' and body['po_number'] == '' and body['pr_number'] != '':
                filter.append(('name', '=', body['rr_number']))
                filter.append(('pr_numbers', '=', body['pr_number']))
                filter.append(('state', '=', 'done'))
                filter.append(('picking_type_id.name', '=', 'Receipts'))
            elif body['rr_number'] != '' and body['po_number'] != '' and body['pr_number'] != '':
                filter.append(('name', '=', body['rr_number']))
                filter.append(('po_numbers', '=', body['po_number']))
                filter.append(('pr_numbers', '=', body['pr_number']))
                filter.append(('state', '=', 'done'))
                filter.append(('picking_type_id.name', '=', 'Receipts'))
            elif body['rr_number'] == '' and body['po_number'] != '' and body['pr_number'] == '':
                filter.append(('name', '=', body['po_number']))
                filter.append(('state', '=', 'purchase'))
                is_po = True
            elif body['rr_number'] == '' and body['po_number'] != '' and body['pr_number'] != '':
                filter.append(('name', '=', body['po_number']))
                filter.append(('pr_numbers', '=', body['pr_number']))
                filter.append(('state', '=', 'purchase'))
                is_po = True
            elif body['rr_number'] == '' and body['po_number'] == '' and body['pr_number'] != '':
                filter.append(('name', '=', body['pr_number']))
                filter.append(('state', 'in', ['approved', 'done']))
                is_pr = True
            if is_pr:
                purchase_request_rec = request.env['purchase.request'].search(filter)
                for rec in purchase_request_rec:
                    receipt_order = False
                    if rec.rr_numbers:
                        receipt_order = request.env['stock.picking'].search([('name', '=', rec.rr_numbers), ('state', '=', 'done'), ('picking_type_id.name', '=', 'Receipts')])

                    if receipt_order:
                        purchase_order = False
                        if rec.po_numbers:
                            purchase_order = request.env['purchase.order'].search([('name', '=', rec.po_numbers), ('state', '=', 'purchase')])

                        to_location_desc = False
                        requestor_emp_id = False
                        if receipt_order:
                            if receipt_order.location_dest_id:
                                to_location_desc = receipt_order.location_dest_id.location_id.name+'/'+receipt_order.location_dest_id.name
                            if receipt_order.requestor_comp:
                                requestor_emp = request.env['res.partner'].search([('name', '=', receipt_order.requestor_comp)], limit=1)
                                if requestor_emp:
                                    requestor_emp_id = requestor_emp.id
                        receive_date = False
                        if receipt_order:
                            if receipt_order.scheduled_date:
                                receive_date = receipt_order.scheduled_date.strftime("%-m/%-d/%Y %-I:%M")

                        VENDOR_SITE_ID = False
                        if len(receipt_order.partner_id.site_ids) != 0:
                            for vendor_site in receipt_order.partner_id.site_ids:
                                VENDOR_SITE_ID = vendor_site.id
                                break

                        po_date = False
                        po_status = False
                        if purchase_order:
                            if purchase_order.date_order:
                                po_date = purchase_order.date_order.strftime("%-m/%-d/%Y %-I:%M")
                            if purchase_order.state == 'purchase':
                                po_status = 'APPROVED'
                            else:
                                po_status = purchase_order.state.upper()
                        pr_date = False
                        if rec.date_start:
                            pr_date = rec.date_start.strftime("%-m/%-d/%Y %-I:%M")

                        vals = {
                            "SOURCEDATA":receipt_order.origin if receipt_order else False,
                            "SHIPMENT_HEADER_ID": receipt_order.id if receipt_order else False,
                            "RECEIPT_NUM": receipt_order.name if receipt_order else False,
                            "RECEIVE_DATE": receive_date,
                            "VENDOR_ID": receipt_order.partner_id.id if receipt_order.partner_id else False,
                            "VENDOR_NAME": receipt_order.partner_id.name if receipt_order else False,
                            "VENDOR_SITE_ID": VENDOR_SITE_ID,
                            "RR_LINE": [],
                            "RECEIVE_LINE": [],
                            "SHIP_TO_LOCATION_ID": receipt_order.location_dest_id.id if receipt_order else False,
                            "SHIP_TO_LOCATION": receipt_order.location_dest_id.name if receipt_order else False,
                            "SHIP_TO_LOCATION_DESC": to_location_desc if receipt_order else False,
                            "EMPLOYEE_ID_RECEIVER": requestor_emp_id if receipt_order else False,
                            "RECEIVER_NAME": receipt_order.requestor_comp if receipt_order else False,
                            "DELIVER_TO_LOCATION_ID": receipt_order.location_dest_id.id if receipt_order else False,
                            "DELIVER_TO_LOCATION": receipt_order.location_dest_id.name if receipt_order else False,
                            "DELIVER_TO_LOCATION_DESC": to_location_desc if receipt_order else False,
                            "DELIVER_TO_PERSON_ID": receipt_order.requestor_comp if receipt_order else False,
                            "DELIVER_TO_PERSON": requestor_emp_id if receipt_order else False,
                            "PO_HEADER_ID": purchase_order.id if purchase_order else False,
                            "PO": purchase_order.name if purchase_order else False,
                            "PO_STATUS": po_status,
                            "BUYER_ID": receipt_order.buyer_id.id if receipt_order else False,
                            "BUYER_NAME": receipt_order.buyer_id.name if receipt_order else False,
                            "PO_DATE":  po_date,
                            "PO_DESCRIPTION": purchase_order.po_description  if purchase_order else False,
                            "PO_CURRENCY": purchase_order.currency_id.name  if purchase_order else False,
                            "PO_RATE": purchase_order.actual_rate if purchase_order else False,
                            "PO_RATE_DATE": po_date,
                            "PO_LINE": [],
                            "REQUISITION_HEADER_ID": rec.id,
                            "PR": rec.name,
                            "PR_STATUS": rec.state.upper(),
                            "PR_DATE": rec.date_start,
                            "PR_DESCRIPTION": rec.description,
                            "REQUESTOR_ID": rec.requested_by.id,
                            "REQUESTOR_NAME": rec.requested_by.name,
                            "PR_LINE": []
                        }
                        if receipt_order:
                            if len(receipt_order.move_ids_without_package) != 0:
                                for line_receive in receipt_order.move_ids_without_package:
                                    data_vals = {
                                        "LINE_NUM": line_receive.line_number,
                                        "DESTINATION_TYPE_CODE": 'RECEIVING' if receipt_order.picking_type_id.name == 'Receipts' else receipt_order.picking_type_id.name.upper(),
                                        "PRIMARY_QUANTITY": line_receive.product_uom_qty,
                                        "QTY_RECEIVE": line_receive.quantity_done,
                                        "RR_QTY": line_receive.quantity_done,
                                        "RR_UOM": line_receive.product_uom.name,
                                        "RR_UOM_DESC": line_receive.product_uom.name,
                                    }
                                    vals["RR_LINE"].append(data_vals)
                                for line_receive in receipt_order.move_ids_without_package:
                                    data_vals = {
                                        "INV_ORG_ID": line_receive.id,
                                        "ORG_ID": line_receive.company_id.id,
                                        "RECEIVE_ITEM_ID": line_receive.product_id.id,
                                        "RECEIVE_ITEM_CODE": line_receive.product_id.default_code,
                                        "RECEIVE_ITEM_NAME": line_receive.product_id.name,
                                        "RECEIVE_ITEM_DESC": line_receive.description_picking
                                    }
                                    vals["RECEIVE_LINE"].append(data_vals)

                        if purchase_order:
                            if len(purchase_order.order_line) != 0:
                                for line in purchase_order.order_line:
                                    data_vals = {
                                        "PO_LINE_ID": line.id,
                                        "PO_LINE": line.line_number,
                                        "PO_ITEM_ID": line.product_id.id,
                                        "PO_ITEM_DESCRIPTION": line.name,
                                        "PO_QTY": line.product_qty,
                                        "PO_UOM": line.product_uom.name,
                                        "PO_UOM_DESC": line.product_uom.name,
                                        "UNIT_PRICE": line.price_unit,
                                        "PO_AMOUNT_IDR": line.price_subtotal,
                                    }
                                    vals["PO_LINE"].append(data_vals)

                        if len(rec.line_ids) != 0:
                            for line in rec.line_ids:
                                data_vals = {
                                    "REQUISITION_LINE_ID": line.id,
                                    "PR_LINE_NUM": line.line_number,
                                    "PR_QTY": line.product_qty,
                                    "PR_UOM": line.product_uom_id.name,
                                    "PR_UOM_DESC": line.name,
                                    "PR_UNIT_PRICE": line.original_price,
                                    "PR_CURRENCY": line.select_currency_id.name,
                                    "PR_RATES": line.actual_rate,
                                    "PR_RATE_DATE": line.date_rate,
                                    "PR_AMOUNT_IDR": line.estimated_cost,
                                }
                                vals["PR_LINE"].append(data_vals)
                        data.append(vals)
            elif is_po:
                purchase_order_rec = request.env['purchase.order'].search(filter)
                for rec in purchase_order_rec:
                    receipt_order = False
                    if rec.rr_numbers:
                        receipt_order = request.env['stock.picking'].search([('name', '=', rec.rr_numbers), ('state', '=', 'done'), ('picking_type_id.name', '=', 'Receipts')])
                    if receipt_order:
                        VENDOR_SITE_ID = False
                        if len(rec.partner_id.site_ids) != 0:
                            for vendor_site in rec.partner_id.site_ids:
                                VENDOR_SITE_ID = vendor_site.id
                                break
                        purchase_request = False
                        if rec.pr_numbers:
                            purchase_request = request.env['purchase.request'].search([('name', '=', rec.pr_numbers), ('state', 'in', ['approved', 'done'])])

                        to_location_desc = False
                        requestor_emp_id = False
                        if receipt_order:
                            if receipt_order.location_dest_id:
                                to_location_desc = receipt_order.location_dest_id.location_id.name+'/'+receipt_order.location_dest_id.name
                            if receipt_order.requestor_comp:
                                requestor_emp = request.env['res.partner'].search([('name', '=', receipt_order.requestor_comp)], limit=1)
                                if requestor_emp:
                                    requestor_emp_id = requestor_emp.id
                        receive_date = False
                        if receipt_order:
                            if receipt_order.scheduled_date:
                                receive_date = receipt_order.scheduled_date.strftime("%-m/%-d/%Y %-I:%M")

                        po_date = False
                        if rec.date_order:
                            po_date = rec.date_order.strftime("%-m/%-d/%Y %-I:%M")

                        po_status = False
                        if rec.state == 'purchase':
                            po_status = 'APPROVED'
                        else:
                            po_status = rec.state.upper()

                        pr_date = False
                        if purchase_request:
                            if purchase_request.date_start:
                                pr_date = purchase_request.date_start.strftime("%-m/%-d/%Y %-I:%M")

                        vals = {
                            "SOURCEDATA":receipt_order.origin if receipt_order else False,
                            "SHIPMENT_HEADER_ID": receipt_order.id if receipt_order else False,
                            "RECEIPT_NUM": receipt_order.name if receipt_order else False,
                            "RECEIVE_DATE": receipt_order.scheduled_date if receipt_order else False,
                            "VENDOR_ID": receipt_order.partner_id.id if receipt_order else False,
                            "VENDOR_NAME": receipt_order.partner_id.name if receipt_order else False,
                            "VENDOR_SITE_ID": VENDOR_SITE_ID,
                            "RR_LINE": [],
                            "RECEIVE_LINE": [],
                            "SHIP_TO_LOCATION_ID": receipt_order.location_dest_id.id if receipt_order else False,
                            "SHIP_TO_LOCATION": receipt_order.location_dest_id.name if receipt_order else False,
                            "SHIP_TO_LOCATION_DESC": to_location_desc if receipt_order else False,
                            "EMPLOYEE_ID_RECEIVER": requestor_emp_id if receipt_order else False,
                            "RECEIVER_NAME": receipt_order.requestor_comp if receipt_order else False,
                            "DELIVER_TO_LOCATION_ID": receipt_order.location_dest_id.id if receipt_order else False,
                            "DELIVER_TO_LOCATION": receipt_order.location_dest_id.name if receipt_order else False,
                            "DELIVER_TO_LOCATION_DESC": to_location_desc if receipt_order else False,
                            "DELIVER_TO_PERSON_ID": receipt_order.requestor_comp if receipt_order else False,
                            "DELIVER_TO_PERSON": requestor_emp_id if receipt_order else False,
                            "PO_HEADER_ID": rec.id,
                            "PO": rec.name,
                            "PO_STATUS": po_status,
                            "BUYER_ID": rec.buyer_id.id if receipt_order else False,
                            "BUYER_NAME": receipt_order.buyer_id.name if receipt_order else False,
                            "PO_DATE":  po_date,
                            "PO_DESCRIPTION": rec.po_description,
                            "PO_CURRENCY": rec.currency_id.name,
                            "PO_RATE": rec.actual_rate,
                            "PO_RATE_DATE": po_date,
                            "PO_LINE": [],
                            "REQUISITION_HEADER_ID": purchase_request.id if purchase_request else False,
                            "PR": purchase_request.name if purchase_request else False,
                            "PR_STATUS": purchase_request.state.upper() if purchase_request else False,
                            "PR_DATE": pr_date,
                            "PR_DESCRIPTION": purchase_request.description if purchase_request else False,
                            "REQUESTOR_ID": purchase_request.requested_by.id if purchase_request else False,
                            "REQUESTOR_NAME": purchase_request.requested_by.name if purchase_request else False,
                            "PR_LINE": []
                        }
                        if receipt_order:
                            if len(receipt_order.move_ids_without_package) != 0:
                                for line_receive in receipt_order.move_ids_without_package:
                                    data_vals = {
                                        "LINE_NUM": line_receive.line_number,
                                        "DESTINATION_TYPE_CODE": 'RECEIVING' if receipt_order.picking_type_id.name == 'Receipts' else receipt_order.picking_type_id.name.upper(),
                                        "PRIMARY_QUANTITY": line_receive.product_uom_qty,
                                        "QTY_RECEIVE": line_receive.quantity_done,
                                        "RR_QTY": line_receive.quantity_done,
                                        "RR_UOM": line_receive.product_uom.name,
                                        "RR_UOM_DESC": line_receive.product_uom.name,
                                    }
                                    vals["RR_LINE"].append(data_vals)
                                for line_receive in receipt_order.move_ids_without_package:
                                    data_vals = {
                                        "INV_ORG_ID": line_receive.id,
                                        "ORG_ID": line_receive.company_id.id,
                                        "RECEIVE_ITEM_ID": line_receive.product_id.id,
                                        "RECEIVE_ITEM_CODE": line_receive.product_id.default_code,
                                        "RECEIVE_ITEM_NAME": line_receive.product_id.name,
                                        "RECEIVE_ITEM_DESC": line_receive.description_picking
                                    }
                                    vals["RECEIVE_LINE"].append(data_vals)

                        if len(rec.order_line) != 0:
                            for line in rec.order_line:
                                data_vals = {
                                    "PO_LINE_ID": line.id,
                                    "PO_LINE": line.line_number,
                                    "PO_ITEM_ID": line.product_id.id,
                                    "PO_ITEM_DESCRIPTION": line.name,
                                    "PO_QTY": line.product_qty,
                                    "PO_UOM": line.product_uom.name,
                                    "PO_UOM_DESC": line.product_uom.name,
                                    "UNIT_PRICE": line.price_unit,
                                    "PO_AMOUNT_IDR": line.price_subtotal,
                                }
                                vals["PO_LINE"].append(data_vals)

                        if purchase_request:
                            if len(purchase_request.line_ids) != 0:
                                for line in purchase_request.line_ids:
                                    data_vals = {
                                        "REQUISITION_LINE_ID": line.id,
                                        "PR_LINE_NUM": line.line_number,
                                        "PR_QTY": line.product_qty,
                                        "PR_UOM": line.product_uom_id.name,
                                        "PR_UOM_DESC": line.name,
                                        "PR_UNIT_PRICE": line.original_price,
                                        "PR_CURRENCY": line.select_currency_id.name,
                                        "PR_RATES": line.actual_rate,
                                        "PR_RATE_DATE": line.date_rate,
                                        "PR_AMOUNT_IDR": line.estimated_cost,
                                    }
                                    vals["PR_LINE"].append(data_vals)
                        data.append(vals)
            else:
                stock_picking_rec = request.env['stock.picking'].search(filter)
                for rec in stock_picking_rec:
                    VENDOR_SITE_ID = False
                    if len(rec.partner_id.site_ids) != 0:
                        for vendor_site in rec.partner_id.site_ids:
                            VENDOR_SITE_ID = vendor_site.id
                            break
                    purchase_request = False
                    if rec.pr_numbers:
                        purchase_request = request.env['purchase.request'].search([('name', '=', rec.pr_numbers), ('state', 'in', ['approved', 'done'])])
                    purchase_order = False
                    if rec.po_numbers:
                        purchase_order = request.env['purchase.order'].search([('name', '=', rec.po_numbers), ('state', '=', 'purchase')])
                    to_location_desc = False
                    if rec.location_dest_id:
                        to_location_desc = rec.location_dest_id.location_id.name+'/'+rec.location_dest_id.name
                    requestor_emp_id = False
                    if rec.requestor_comp:
                        requestor_emp = request.env['res.partner'].search([('name', '=', rec.requestor_comp)], limit=1)
                        if requestor_emp:
                            requestor_emp_id = requestor_emp.id
                    receive_date = False
                    if rec.scheduled_date:
                        receive_date = rec.scheduled_date.strftime("%-m/%-d/%Y %-I:%M")

                    po_date = False
                    po_status = False
                    if purchase_order:
                        if purchase_order.date_order:
                            po_date = purchase_order.date_order.strftime("%-m/%-d/%Y %-I:%M")
                        if purchase_order.state == 'purchase':
                            po_status = 'APPROVED'
                        else:
                            po_status = purchase_order.state.upper()

                    pr_date = False
                    if purchase_request:
                        if purchase_request.date_start:
                            pr_date = purchase_request.date_start.strftime("%-m/%-d/%Y %-I:%M")

                    vals = {
                        "SOURCEDATA":rec.origin,
                        "SHIPMENT_HEADER_ID": rec.id,
                        "RECEIPT_NUM": rec.name,
                        "RECEIVE_DATE": rec.scheduled_date,
                        "VENDOR_ID": rec.partner_id.id,
                        "VENDOR_NAME": rec.partner_id.name,
                        "VENDOR_SITE_ID": VENDOR_SITE_ID,
                        "RR_LINE": [],
                        "RECEIVE_LINE": [],
                        "SHIP_TO_LOCATION_ID": rec.location_dest_id.id,
                        "SHIP_TO_LOCATION": rec.location_dest_id.name,
                        "SHIP_TO_LOCATION_DESC": to_location_desc,
                        "EMPLOYEE_ID_RECEIVER": requestor_emp_id,
                        "RECEIVER_NAME": rec.requestor_comp,
                        "DELIVER_TO_LOCATION_ID": rec.location_dest_id.id,
                        "DELIVER_TO_LOCATION": rec.location_dest_id.name,
                        "DELIVER_TO_LOCATION_DESC": to_location_desc,
                        "DELIVER_TO_PERSON_ID": rec.requestor_comp,
                        "DELIVER_TO_PERSON": requestor_emp_id,
                        "PO_HEADER_ID": purchase_order.id if purchase_order else False,
                        "PO": purchase_order.name if purchase_order else False,
                        "PO_STATUS": po_status,
                        "BUYER_ID": rec.buyer_id.id,
                        "BUYER_NAME": rec.buyer_id.name,
                        "PO_DATE":  po_date,
                        "PO_DESCRIPTION": purchase_order.po_description if purchase_order else False,
                        "PO_CURRENCY": purchase_order.currency_id.name if purchase_order else False,
                        "PO_RATE": purchase_order.actual_rate if purchase_order else False,
                        "PO_RATE_DATE": po_date,
                        "PO_LINE": [],
                        "REQUISITION_HEADER_ID": purchase_request.id if purchase_request else False,
                        "PR": purchase_request.name if purchase_request else False,
                        "PR_STATUS": purchase_request.state.upper() if purchase_request else False,
                        "PR_DATE": pr_date,
                        "PR_DESCRIPTION": purchase_request.description if purchase_request else False,
                        "REQUESTOR_ID": purchase_request.requested_by.id if purchase_request else False,
                        "REQUESTOR_NAME": purchase_request.requested_by.name if purchase_request else False,
                        "PR_LINE": []
                    }
                    if len(rec.move_ids_without_package) != 0:
                        for line_receive in rec.move_ids_without_package:
                            data_vals = {
                                "LINE_NUM": line_receive.line_number,
                                "DESTINATION_TYPE_CODE": 'RECEIVING' if rec.picking_type_id.name == 'Receipts' else rec.picking_type_id.name.upper(),
                                "PRIMARY_QUANTITY": line_receive.product_uom_qty,
                                "QTY_RECEIVE": line_receive.quantity_done,
                                "RR_QTY": line_receive.quantity_done,
                                "RR_UOM": line_receive.product_uom.name,
                                "RR_UOM_DESC": line_receive.product_uom.name,
                            }
                            vals["RR_LINE"].append(data_vals)
                        for line_receive in rec.move_ids_without_package:
                            data_vals = {
                                "INV_ORG_ID": line_receive.id,
                                "ORG_ID": line_receive.company_id.id,
                                "RECEIVE_ITEM_ID": line_receive.product_id.id,
                                "RECEIVE_ITEM_CODE": line_receive.product_id.default_code,
                                "RECEIVE_ITEM_NAME": line_receive.product_id.name,
                                "RECEIVE_ITEM_DESC": line_receive.description_picking
                            }
                            vals["RECEIVE_LINE"].append(data_vals)

                    if purchase_order:
                        if len(purchase_order.order_line) != 0:
                            for line in purchase_order.order_line:
                                data_vals = {
                                    "PO_LINE_ID": line.id,
                                    "PO_LINE": line.line_number,
                                    "PO_ITEM_ID": line.product_id.id,
                                    "PO_ITEM_DESCRIPTION": line.name,
                                    "PO_QTY": line.product_qty,
                                    "PO_UOM": line.product_uom.name,
                                    "PO_UOM_DESC": line.product_uom.name,
                                    "UNIT_PRICE": line.price_unit,
                                    "PO_AMOUNT_IDR": line.price_subtotal,
                                }
                                vals["PO_LINE"].append(data_vals)

                    if purchase_request:
                        if len(purchase_request.line_ids) != 0:
                            for line in purchase_request.line_ids:
                                data_vals = {
                                    "REQUISITION_LINE_ID": line.id,
                                    "PR_LINE_NUM": line.line_number,
                                    "PR_QTY": line.product_qty,
                                    "PR_UOM": line.product_uom_id.name,
                                    "PR_UOM_DESC": line.name,
                                    "PR_UNIT_PRICE": line.original_price,
                                    "PR_CURRENCY": line.select_currency_id.name,
                                    "PR_RATES": line.actual_rate,
                                    "PR_RATE_DATE": line.date_rate,
                                    "PR_AMOUNT_IDR": line.estimated_cost,
                                }
                                vals["PR_LINE"].append(data_vals)

                    data.append(vals)
            return self.api_response("Success Get Atis", data, 200)
        else:
            return self.api_response("Failed check body", data, 500)

    @validate_token
    @http.route('/mnc_erp/customer/post', auth="none", type="json", methods=['POST'], csrf=False)
    def post_customer(self, **kw):
        vals = request.jsonrequest
        keys = ['name', 'type', 'partner_no']
        if self.check_keys(keys, vals):
            check_partner_no = request.env['res.partner'].search([('partner_no', 'ilike', vals['partner_no'])])
            if check_partner_no:
                return self.api_response("Failed duplicated partner no customer", [], 500)
            partner_type = request.env['res.partner.type'].search([('code', 'ilike', vals['type'])])
            if not partner_type:
                return self.api_response("Failed Please Match Code Customer Type Gen21", [], 500)
            data = {
                'name': vals['name'],
                'partner_type_id': partner_type.id,
                'partner_no': vals['partner_no'],
                'customer_rank': 1,
                'active': True,
                'is_company': True
            }
            customer_gen21 = request.env['res.partner'].create(data)
            if customer_gen21:
                return self.api_response("Success Create Customer Gen21", [], 200)
            else:
                return self.api_response("Failed Create Customer Gen21", [], 500)
        else:
            return self.api_response("Failed check body", [], 500)
