import logging
import requests
from xml.etree import ElementTree as ET
from odoo import api, fields, models


_logger = logging.getLogger()


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_provider = fields.Selection(selection_add=[
        ('bank_indonesia', 'Bank Indonesia')
    ], default='bank_indonesia')

    @api.model
    def set_special_defaults_on_install(self):
        """ override function to set bank_indonesia as default """
        res = super(ResCompany, self).set_special_defaults_on_install()
        all_companies = self.env['res.company'].search([])
        for company in all_companies:
            if company.country_id.code == 'ID':
                company.currency_provider = 'bank_indonesia'
        return res

    def _check_existence(self, code):
        """ function to check if a currency exists in odoo """
        # only process active currency to avoid error
        sql = """
            SELECT COUNT(id) AS id
            FROM res_currency
            WHERE name = '%s' AND active IS TRUE
        """ % (code)
        self.env.cr.execute(sql)
        currency = self.env.cr.dictfetchone()
        return currency and currency is not None and currency.get('id')

    def _parse_currencies(self, date_search):
        """ function to parse currency as dict from web service """
        sdate = date_search.strftime('%Y%m%d')
        url = 'https://www.bi.go.id/biwebservice/wskursbi.asmx/getSubKursLokal4?startdate=%s' % sdate
        try:
            result = requests.get(url)
            result.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError('Connection Error!')

        root = ET.fromstring(result.content)
        table_root = root.findall('{urn:schemas-microsoft-com:xml-diffgram-v1}diffgram')
        table = table_root[0]
        dataset = table.findall('NewDataSet')
        dataset = dataset[0]
        currency = {}
        for child in dataset.findall('Table'):
            unit = child.find('nil_subkurslokal').text
            jual = child.find('beli_subkurslokal').text
            beli = child.find('jual_subkurslokal').text
            mts = child.find('mts_subkurslokal').text
            mts = str(mts.strip())
            if self._check_existence(mts):
                currency[mts] = {
                    'unit': float(unit),
                    'sell': float(jual),
                    'buy': float(beli),
                }
        return currency

    def _parse_bank_indonesia_data(self, available_currencies):
        """ function to parse BI exchange data """
        res = {}
        today = fields.Date.today()
        # get the currencies rate from the web crawler
        rates = self._parse_currencies(today)
        _logger.info('Fetching rates from %s', today.strftime('%d-%b-%Y'))
        # get the main currency from company
        main_currency = self.currency_id.name
        if main_currency not in rates.keys() and main_currency != 'IDR':
            return False  # False if currency is not in BI listed currencies
        # get the base IDR as benchmark
        tmp_idr = 1
        if main_currency != 'IDR':
            rts = rates[main_currency]
            # multiply by unit if any, for IDR directly use the main rate
            tmp_idr = ((rts['sell'] + rts['buy']) / 2) / rts['unit']
        res['IDR'] = (tmp_idr, today)
        # assign all currencies fetched from BI rates
        for curr, val_dict in rates.items():
            # divide by unit
            sell_per_unit = (val_dict['sell'] / val_dict['unit'])
            res[curr] = (tmp_idr / (((val_dict['sell'] + val_dict['buy']) / 2) / val_dict['unit']), today)
        return res
