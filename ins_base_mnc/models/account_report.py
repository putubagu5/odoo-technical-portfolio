import copy
import json
import io
import logging
import lxml.html
import datetime
import ast
from collections import defaultdict
from math import copysign

from dateutil.relativedelta import relativedelta

from odoo.tools.misc import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import config, date_utils, get_lang
from odoo.osv import expression
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date
from odoo.addons.web.controllers.main import clean_action

_logger = logging.getLogger(__name__)

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_currency = None

    @api.model
    def _get_options_currency(self, options):
        return [
            currency for currency in options.get('currency', []) if currency['selected']
        ]

    @api.model
    def _get_options_currency_domain(self, options):
        domain = []
        if options.get('currency_ids'):
            currency_ids = [int(currency) for currency in options['currency_ids']]
            domain.append(('currency_id', 'in', currency_ids))
        # selected_currency = self._get_options_currency(options)
        # return selected_currency and [('currency_id', 'in', [j['id'] for j in selected_currency])] or []

    @api.model
    def _init_filter_currency(self, options, previous_options=None):
        if not self.filter_currency:
            return

        options['currency'] = True
        options['currency_ids'] = previous_options and previous_options.get('currency_ids') or []
        selected_currency_ids = [int(partner) for partner in options['currency_ids']]
        selected_currencies = selected_currency_ids and self.env['res.currency'].browse(selected_currency_ids) or self.env[
            'res.currency']
        options['selected_currency_ids'] = selected_currencies.mapped('name')

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_currency_domain(options)
        return domain
