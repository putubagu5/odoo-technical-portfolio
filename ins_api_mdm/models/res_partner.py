from copy import deepcopy
from datetime import datetime
import logging
import requests
from odoo import api, models, SUPERUSER_ID


_logger = logging.getLogger(__name__)
VENDOR_SITE_KEYS = ('vendor_site_code', 'vendor_site_name', 'vendor_type')
INDIVIDUAL_VENDOR_SITE_CODE = ('EMPLOYEE', 'PERSONAL', 'TALENT')  # valid SITE CODE
BANK_KEYS = ('bank_name', 'bank_branch', 'bank_address', 'bank_account_name',
             'bank_account_number')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_name_map(self):
        """ function to help map fields """
        return {
            'VENDOR_NAME': 'name',
            'ADDRESS_LINE1': 'street',
            'CITY': 'city',
            'PROVINCE': '',
            'REGION': '',
            'COMPANY': '',
            'VENDOR_NAME_ALT': 'alias_name',
            'ALAMAT_NPWP': 'blok',
            'ZIP': 'zip',
            'VAT_REGISTRATION_NUM': 'npwp',
            'FIRST_NAME': 'cp_first_name',
            'LAST_NAME': 'cp_last_name',
            'TITLE': '',
            'AREA_CODE': '',
            'PHONE': 'phone',
            'EMAIL_ADDRESS': '',
            'ALT_AREA_CODE': '',
            'ALT_PHONE': 'mobile',
            'FAX_AREA_CODE': '',
            'FAX': '',
            'BANK_NAME': 'bank_name',
            'BANK_BRANCH': 'bank_branch',
            'BANK_ADDRESS': 'bank_address',
            'BANK_ACCOUNT_NAME': 'bank_account_name',
            'BANK_ACCOUNT_NUMBER': 'bank_account_number',
            'NPWP_ADDRESS': 'blok',
            'FLAG': '',
            'SITE': 'vendor_site_name',
            'VENDOR_INTERFACE_ID': 'partner_no',
            'VENDOR_TYPE_LOOKUP_CODE': 'vendor_type',
            'VENDOR_SITE_CODE': 'vendor_site_code',
            'REQUESTOR': '',
            'VENDOR_ID': 'mnc_mdm_vendor_id',
            'NEW_VENDOR_ID': 'new_mnc_mdm_vendor_id',
            'ODOO_INTERFACE_ID': 'zip',
            'ATTRIBUTE10': '',
            'EMAIL_REQUESTOR': '',
            'ISGEN': '',
            'CREATION_DATE': 'create_date',
            'LASTUPDATE_DATE': 'write_date',
            'FLAG_ODOO': '',
        }
        ## dev 25 jul 2023 - p1 - begin
        # 'ODOO_INTERFACE_ID': 'odoo_interface_id',
        ## dev 25 jul 2023 - p1 - end


    def _get_token(self):
        """ helper function to get token """
        token = ''
        url = 'http://mdm.mncgroup.com/api/gettoken?pass=0d00mdm_2022'
        try:  # try and check if anything happens
            response = requests.get(url, timeout=5)  # set timeout to 5s
        except requests.exceptions.RequestException as e:
            _logger.info(e)
            _logger.info('Connection to MDM error')
            return token

        # nothing wrong happens, then get the response.json() and look for
        # `token`. If found, then assign to token, else skip
        body = response.json()

        token = body.get('token', '')

        return token

    def _search_bank_by_name(self, name):
        """ helper function to search bank by name to get its id """
        bank_id = False
        sql = """
            SELECT id AS id
            FROM res_bank
            WHERE name = '%s'
            LIMIT 1
        """ % (name)
        self.env.cr.execute(sql)
        bank = self.env.cr.dictfetchone()
        if bank and bank.get('id'):
            bank_id = bank.get('id')
        return bank_id

    def _search_partner_by_reference(self, partner_no):
        partner_id = False
        sql = """
            SELECT id AS id
            FROM res_partner
            WHERE partner_no = '%s'
        """ % (partner_no)
        self.env.cr.execute(sql)
        partner = self.env.cr.dictfetchone()
        if partner and partner.get('id'):
            partner_id = partner.get('id')
        return partner_id

    def _process_url(self, token, company_id):
        """ function to contact endpoint and write/create data """
        partner = self.env['res.partner'].with_user(SUPERUSER_ID)
        response_list = []
        response_list_data = []
        url = 'http://mdm.mncgroup.com/api/getsupplierlist?token=%s&orgid=%s' % (
            token, company_id
        )
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            _logger.info(e)
            _logger.info('Error contacting getsupplierlist')
            return

        body = response.json()  # get json
        data = body.get('data', [])

        # happily map the data with key
        name_map = self._get_name_map()
        # cleaned_map = {k: v for k, v in name_map.items() if v}  # only get map with values
        # map data and make sure the keys are in cleaned_map
        map_data = [
            dict(zip(map(lambda x: name_map.get(x), r.keys()), r.values())) for r in data
        ]
        mapped_data = [{k: v for k, v in x.items() if k} for x in map_data]

        # then we need to clean the data for specific fields
        for x in mapped_data:
            for k in x.keys():  # make cheaper, loop only keys
                if k in ('create_date', 'write_date'):  # if date specific field
                    # try to get the data and parse
                    if x.get(k, ''):  # exists, then convert to title case
                        tmp = datetime.strptime((x[k]).title(), '%d-%b-%y').date()
                        x[k] = tmp  # replace

        # prepare url
        url = 'http://mdm.mncgroup.com/api/odooflagchange?token=%s' % token

        # then finally loop mapped_data and create/write
        for mp in mapped_data:
            # vendor code: take from mnc_mdm_vendor_id or new_mnc_mdm_vendor_id
            vendor_id = mp.get('mnc_mdm_vendor_id', False)
            _logger.info('kena 1')
            if not vendor_id:
                _logger.info('kena 2')
                vendor_id = mp.get('new_mnc_mdm_vendor_id', False)
            if not vendor_id:
                _logger.info('kena 3')
                vendor_id = mp.get('partner_no', False)

            partner_id = self._search_partner_by_reference(vendor_id)
            ## dev 25 jul 2023 - p2 - begin
            #partner_url = '&odoointerfaceid=%s' % vendor_id
            odoo_interface_id = mp.get('zip', False)
            partner_url = '&odoointerfaceid=%s' % odoo_interface_id
            ## dev 25 jul 2023 - p2 - end

            status_url = ''
            status = ''

            # generate vendor site and bank dict
            vendor_site_dict = {
                k: v for k, v in mp.items() if k in VENDOR_SITE_KEYS if v
            }
            bank_dict = {
                k: v for k, v in mp.items() if k in BANK_KEYS if v
            }

            # pop mnc_mdm_vendor_id here instead of down there
            mdm_vendor = False
            if mp.get('mnc_mdm_vendor_id', ''):
                mdm_vendor = mp.pop('mnc_mdm_vendor_id', False)

            if mp.get('new_mnc_mdm_vendor_id', ''):
                mdm_vendor = mp.pop('new_mnc_mdm_vendor_id', False)

            p_data = deepcopy(mp)  # deepcopy and make sure mp is not mutated
            # p_data.pop('mnc_mdm_vendor_id')
            # p_data.pop('new_mnc_mdm_vendor_id')

            # obtain site code and type
            site_code = vendor_site_dict.get('vendor_site_code')
            vendor_type = vendor_site_dict.get('vendor_type')

            is_company = vendor_type not in INDIVIDUAL_VENDOR_SITE_CODE
            # then update is_company
            p_data.update({'is_company': is_company})

            ## dev 25 jul 2023 - p3 - begin
            # then update supplier_rank
            p_data.update({'supplier_rank': 1})

            ### perbaiki ini , saat ini masih hard code, tolong diupdate codenya - PENTING - begin
            vendor_type_id = 9

            if   vendor_type == "EMPLOYEE": vendor_type_id = 20
            elif vendor_type == "INTERNAL": vendor_type_id = 22
            elif vendor_type == "ORGANIZATION": vendor_type_id = 19
            elif vendor_type == "PERSONAL": vendor_type_id = 13
            elif vendor_type == "PROGRAM": vendor_type_id = 16
            elif vendor_type == "RELATED PARTIES": vendor_type_id = 12
            elif vendor_type == "TALENT": vendor_type_id = 14
            elif vendor_type == "TALENT BANDAN USAHA": vendor_type_id = 21
            elif vendor_type == "TAX AUTHORITY": vendor_type_id = 15
            elif vendor_type == "THIRD PARTY": vendor_type_id = 23
            elif vendor_type == "VENDOR": vendor_type_id = 9
            elif vendor_type == "VENDOR BADAN USAHA": vendor_type_id = 11
            elif vendor_type == "VENDOR PERORANGAN": vendor_type_id = 10
            ### perbaiki ini , saat ini masih hard code, tolong diupdate codenya - PENTING - begin

            p_data.update({'partner_type_id': vendor_type_id})
            ## dev 25 jul 2023 - p3 - end

            # remember to pop the contact person info
            first_name = p_data.pop('cp_first_name', False)
            last_name = p_data.pop('cp_last_name', False)

            # then try to get bank
            bank_id = False
            if bank_dict.get('bank_name'):
                bank_id = self._search_bank_by_name(bank_dict.get('bank_name'))

            # then spring clean this
            for x in VENDOR_SITE_KEYS:
                p_data.pop(x, False)
            for x in BANK_KEYS:
                p_data.pop(x, False)

            if partner_id:
                _logger.info('partner id')
                _logger.info(partner_id)
                # partner found, we have to check the vendor site first
                # pop every vendor data found into a dict, same goes for bank
                # from the vendor site dict, get code and find if any site_ids
                # contains the same code, if yes, then get the id and add write
                # triplet code. If not found, then add using 0 triplet

                # get partner data and write
                pt = partner.browse(partner_id)

                sites = pt.site_ids.filtered(lambda x: x.code == site_code)
                site_data = []
                if sites:
                    for st in sites:
                        tmp = {
                            'name': st.name,
                            'code': st.code,
                            'account_name': st.account_name,
                            'account_no': st.account_no,
                            'bank_id': st.bank_id.id,
                            'type': 'vendor',
                            'contact_person': '%s %s' % (first_name, last_name),
                        }
                        # only update
                        site_data.append((1, st.id, tmp))
                else:
                    # no site found, meaning add
                    tmp = {
                        'name': vendor_site_dict.get('vendor_site_name'),
                        'code': site_code,
                        'account_name': bank_dict.get('bank_account_name'),
                        'account_no': bank_dict.get('bank_account_number'),
                        'bank_id': bank_id,
                        'type': 'vendor',
                        'address': p_data.get('street'),
                        'contact_person': '%s %s' % (first_name, last_name),
                    }
                    site_data.append((0, 0, tmp))

                # NOTE: if mnc_mdm_vendor_id exists, we need to put the site_data
                if mdm_vendor:
                    p_data.update({'site_ids': site_data})

                write = pt.write(p_data)
                status_url = '&statusflag=E'
                status = 'E'
                if write:  # change statusflag
                    status_url = '&statusflag=S'
                    status = 'S'
            else:
                _logger.info('non partner')
                # create vendor site data and the bank inside, pop every vendor
                site_data = []
                tmp = {
                    'name': vendor_site_dict.get('vendor_site_name'),
                    'code': site_code,
                    'account_name': bank_dict.get('bank_account_name'),
                    'account_no': bank_dict.get('bank_account_number'),
                    'bank_id': bank_id,
                    'type': 'vendor',
                    'address': p_data.get('street'),
                    'contact_person': '%s %s' % (first_name, last_name),
                    'partner_no': vendor_id,
                }
                site_data.append((0, 0, tmp))

                # NOTE: if mnc_mdm_vendor_id exists, we need to put the site_data
                if mdm_vendor:
                    p_data.update({'site_ids': site_data})

                # data into a new dict and pop the unused field
                partner_data = deepcopy(p_data)
                partner_data.pop('mnc_mdm_vendor_id', False)
                partner_data.pop('new_mnc_mdm_vendor_id', False)
                pt = partner.create(partner_data)
                status_url = '&statusflag=E'
                status = 'E'
                if pt:  # success, construct URL, append to list
                    status_url = '&statusflag=S'
                    status = 'S'

            _logger.info('url')
            _logger.info(url)
            _logger.info(partner_url)
            _logger.info(status_url)
            _logger.info(status)

            response_url = '%s%s%s' % (url, partner_url, status_url)
            response_data = {
                'name': mp['partner_no'],
                'url': response_url,
                'state': status,
            }
            response_list_data.append((0, 0, response_data))
            response_list.append(response_url)

            _logger.info('response_url')
            _logger.info(response_url)


            _logger.info('response list')
            _logger.info(response_list)
            # NOTE: this will send response to production, uncomment if finalize
            # then we gang the server with our response
            for x in response_list:
                try:  # try to call the url and see if something happen?
                    response = requests.get(x)
                    #pass
                except requests.exceptions.RequestException as e:
                    _logger.info('Error in sync with MDM')

    def _process_data(self):
        """ function to process data """
        # get token, find all companies then loop
        # based on the company org_id, call the URL to get data with N or E *
        # then loop the data found (in JSON), remember to check the existence
        # in Odoo. If exists then write, else create
        # possibly use try-except to create/write partner.
        # every failed attempt to create/write will be put inside a list (possibly
        # put inside a new model? containing the VENDOR_INTERFACE_ID which will
        # be sent to the URL in separate cron function)
        # * is this better separated into function?

        token = self._get_token()
        if not token:
            _logger.info('No Token found, cannot connect to API')
            return

        # get all companies and mapped based on the necessary field
        # NOTE: the field is org_id to sync with MDM
        companies = self.env['res.company'].with_user(
            SUPERUSER_ID).search([]).mapped('org_id')
        for cmp_id in companies:
            self._process_url(token, cmp_id)
        return

    @api.model
    def _sync_to_mdm(self):
        """ function to sync data to MDM application """
        self._process_data()
        return
