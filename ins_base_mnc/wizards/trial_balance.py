from datetime import datetime
from io import BytesIO
import json
import xlsxwriter
from odoo import api, fields, models


class WizardTrialBalance(models.TransientModel):
    _name = 'wizard.trial.balance'
    _description = 'Trial Balance Wizard Report'

    json_info = fields.Text('JSON Info')

    @api.model
    def default_get(self, fields_list):
        """ inherit function to add default value """
        res = super().default_get(fields_list)
        if self._context:
            res['json_info'] = json.dumps(self._context)
        return res

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'Trial Balance'
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_default_analytic_account(self):
        """ function to get default analytic account """
        domain = [('is_default', '=', True)]
        account = self.env['account.analytic.account'].search(domain, limit=1)
        return account

    def _get_initial_balance_by_analytic(self, options_list):
        """ function to get sum amount per analytic """
        # NOTE: this function mimics the _get_query_sums function in general ledger
        general_ledger = self.env['account.general.ledger']

        # use default analytic to coalesce in query
        default_analytic = self.get_default_analytic_account()

        options = options_list[0] if options_list else {}

        # get first found options from the list
        ct_query = self.env['res.currency']._get_query_currency_table(options)
        new_options = general_ledger._get_options_initial_balance(options)

        tables, where_clause, where_params = general_ledger._query_get(new_options, domain=[])
        params = where_params

        # result of the query is the list of dict containing the data grouped
        # by analytic_id and account_id per account_move_line. This could be
        # combined with `data` from options
        sql = """
            SELECT COALESCE(analytic.id, %s) AS analytic_id,
            account_move_line.account_id AS account_id,
            SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
            SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
            SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
            FROM %s
            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN account_analytic_account analytic ON analytic.id = account_move_line.analytic_account_id
            WHERE %s
            GROUP BY analytic_id, account_id
        """ % (default_analytic.id, tables, ct_query, where_clause)
        self.env.cr.execute(sql, params)
        res = self.env.cr.dictfetchall()
        return res

    @api.model
    def _get_options_periods_list(self, options):
        ''' Get periods as a list of options, one per impacted period.
        The first element is the range of dates requested in the report, others are the comparisons.

        :param options: The report options.
        :return:        A list of options having size 1 + len(options['comparison']['periods']).
        '''
        periods_options_list = []
        if options.get('date'):
            periods_options_list.append(options)
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                period_options = options.copy()
                period_options['date'] = period
                periods_options_list.append(period_options)
        return periods_options_list

    def _get_report_sql(self, date_from, date_to):
        """  """
        context = self._context
        sql_date = f'''
            AND aml.date >= '{date_from}'
            AND aml.date <= '{date_to}'
        '''
        if context.get('initial', False):
            sql_date = f'''
                AND aml.date < '{date_from}'
            '''

        sql_detail = ''
        sql_group = ''
        if context.get('detail', False):
            sql_detail = ', analytic.code AS analytic_code'
            sql_group = ', analytic.code'

        sql_dict = {
            'sql_date': sql_date,
            'sql_detail': sql_detail,
            'sql_group': sql_group,
            'company_id': self.env.company.id,
        }
        sql = """
            SELECT coa.code AS account_code,
            coa.name AS account_description,
            SUM(aml.balance) AS balance,
            SUM(aml.debit) AS debit,
            SUM(aml.credit) AS credit
            %(sql_detail)s
            FROM account_move_line aml
            LEFT JOIN account_move am ON am.id = aml.move_id
            LEFT JOIN account_account coa ON coa.id = aml.account_id
            LEFT JOIN account_analytic_account analytic ON analytic.id = aml.analytic_account_id
            WHERE am.state != 'cancel'
            AND aml.company_id = %(company_id)s
            %(sql_date)s
            GROUP BY coa.code, coa.name %(sql_group)s
            ORDER BY coa.code
        """ % (sql_dict)
        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchall()
        return res

    def _prepare_normal_data(self):
        """ helper split function to prepare data for Normal Sheet """
        result = {}
        options = json.loads(self.json_info)
        data = options.get('data', [])
        if data:
            data = data[1]  # get index 1 of data list, containing list of data

        # data is already grouped, just loop and assign
        # this is done with the assumption of the data is not grouped whatsoever
        d_key = 'no_format_name'  # key for the data dict
        d_key_2 = 'name'  # key for backup in case no_format_name is not found
        for dt in data:
            col = dt.get('columns', [])

            init_debit_col = col[1].get(d_key, 0) or col[1].get(d_key_2, 0) or 0
            init_credit_col = col[2].get(d_key, 0) or col[2].get(d_key_2, 0) or 0
            trx_debit_col = col[3].get(d_key, 0) or col[3].get(d_key_2, 0) or 0
            trx_credit_col = col[4].get(d_key, 0) or col[4].get(d_key_2, 0) or 0
            end_debit_col = col[5].get(d_key, 0) or col[5].get(d_key_2, 0) or 0
            end_credit_col = col[6].get(d_key, 0) or col[6].get(d_key_2, 0) or 0

            result.setdefault(dt['name'], {})
            result[dt['name']] = {
                'account_code': dt['name'],
                'description': col[0]['name'],
                'start': float(init_debit_col) - float(init_credit_col),
                'debit': float(trx_debit_col),
                'credit': float(trx_credit_col),
                'end': float(end_debit_col) - float(end_credit_col),
            }

        return result

    def _get_analytic_from_move_lines(self, aml_ids):
        """ function to get analytic information from account.move.line """
        # use default analytic to coalesce in query
        default_analytic = self.get_default_analytic_account()

        str_aml_ids = '(%s)' % ', '.join(str(x) for x in aml_ids)

        sql = """
            SELECT aml.id AS move_id,
            COALESCE(analytic.id, %s) AS id,
            COALESCE(analytic.code, '%s') AS code
            FROM account_move_line aml
            LEFT JOIN account_analytic_account analytic ON analytic.id = aml.analytic_account_id
            WHERE aml.id IN %s
        """ % (default_analytic.id, default_analytic.code, str_aml_ids)
        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchall()
        return res

    def _prepare_detail_data(self):
        """ helper split function to prepare data for Detail Sheet """
        # NOTE: data is taken from _do_query instead of context to get lines
        result = []
        options = json.loads(self.json_info)
        options['unfold_all']= True
        options_list = self._get_options_periods_list(options)

        # call _do_query, passing fetch_lines to True to get the lines
        acc_results, _ = self.env['account.general.ledger']._do_query(
            options_list, fetch_lines=True)

        # get initial balance grouped by analytic, check in examples directory
        # trial_balance_analytic_data.json
        analytics = self._get_initial_balance_by_analytic(options_list)

        # to speed things up, take all the analytics from the account move lines
        aml_ids = []
        for acc, res in acc_results:
            lines = res[0].get('lines', [])  # there is only one element
            for line in lines:
                aml_id = line.get('id', False)
                aml_ids.append(aml_id)

        # then execute as whole
        aml_table = self._get_analytic_from_move_lines(aml_ids)

        account_table = {}
        for acc, res in acc_results:
            account_table.setdefault(acc, {})
            lines = res[0].get('lines', [])  # there is only one element
            a_data = account_table[acc]
            for line in lines:
                # get account.move.line id, fetch record and get account_analytic_id
                aml_id = line.get('id', False)
                acc_id = line.get('account_id', False)

                debit = line.get('debit', 0.0)
                credit = line.get('credit', 0.0)

                acc_code = line.get('account_code', '')
                description = line.get('account_name', '')

                # check the same move_id in aml_table
                analytic = [x for x in aml_table if x['move_id'] == aml_id]
                if analytic:
                    analytic = analytic[0]  # get the first element

                # filter out the analytics with same analytic and account id
                f_analytics = [
                    x for x in analytics if x['analytic_id'] == analytic.get('id') and x['account_id'] == acc_id
                ]

                # set the data and sum
                a_data.setdefault(analytic.get('code', ''), {
                    'account_code': acc_code,
                    'description': description,
                    'analytic_code': analytic.get('code', ''),
                    'start': sum(x['balance'] for x in f_analytics),
                    'debit': 0,
                    'credit': 0,
                    'end': 0,
                })
                a_data[analytic.get('code', '')]['debit'] += debit
                a_data[analytic.get('code', '')]['credit'] += credit

        # clean the account_table, remove the record with empty value
        account_table = {k: v for k, v in account_table.items() if v}

        # re-iterate to assign the end value
        # last, re-construct the data into list of the `values` from account_table
        for dt in account_table.values():
            for info in dt.values():
                info['end'] = info['start'] + info['debit'] - info['credit']
                result.append(info)

        return result

    def _prepare_report_data(self):
        """ function to prepare report data containing list of dict """
        normal_table = self._prepare_normal_data()
        detail_table = self._prepare_detail_data()
        result = {
            'normal': normal_table,
            'detail': detail_table,
        }

        return result

    def _get_normal_sheet(self, wb, data={}):
        """ function to construct worksheet for normal TB data """
        ws = wb.add_worksheet('Trial Balance')

        options = json.loads(self.json_info)  # need to get info

        # style
        normal_border = wb.add_format({
            'font_name': 'Arial', 'num_format': '#,###',
        })

        # set column width
        widths = [12, 33, 20, 24, 24, 20]
        for idx, width in enumerate(widths):
            ws.set_column(idx, idx, width)

        # data example, see below
        # {
        #     '000': {
        #         'account_code': '000',
        #         'description': 'COA NAME',
        #         'start': 0,
        #         'debit': 0,
        #         'credit': 0,
        #         'end': 0,
        #     }
        # }

        row = col = 0

        date_print = datetime.now().strftime('%d-%b-%Y %H:%M').upper()
        period = options.get('date', {}).get('string', '')

        # titles
        ws.merge_range(row, col, row, col + 3,
                       'MNC Ledger Trial Balance - Total Currency')
        ws.merge_range(row, col + 4, row, col + 5, f'Report Date: {date_print}')
        ws.merge_range(row + 1, col + 2, row + 1, col + 3, f'Period: {period}')

        row += 3

        ws.write(row, col + 1, 'Currency: IDR')
        ws.write(row + 1, col + 1, 'Balance Type: Year to Date')
        ws.write(row + 2, col + 1, 'Ledger: MNC Ledger')
        ws.write(row + 3, col + 1, f'Company: {self.env.company.name}')

        row += 5

        headers = [
            'Account', 'Description', 'Beginning Balance', 'Debits', 'Credits',
            'Ending Balance',
        ]
        for idx, header in enumerate(headers):
            ws.write(row, col + idx, header, normal_border)

        row += 1

        # loop data list and manage to print contents
        for dt in data.values():
            ws.write(row, col, dt['account_code'])
            ws.write(row, col + 1, dt['description'], normal_border)
            ws.write(row, col + 2, dt['start'], normal_border)
            ws.write(row, col + 3, dt['debit'], normal_border)
            ws.write(row, col + 4, dt['credit'], normal_border)
            ws.write(row, col + 5, dt['end'], normal_border)

            row += 1

    def _get_detail_sheet(self, wb, data=[]):
        """ function to construct worksheet for detail TB data """
        ws = wb.add_worksheet('Detail Trial Balance')

        options = json.loads(self.json_info)  # need to get info

        # style
        normal_border = wb.add_format({
            'font_name': 'Arial', 'num_format': '#,###',
        })

        # set column width
        widths = [12, 33, 20, 24, 24, 20, 24]
        for idx, width in enumerate(widths):
            ws.set_column(idx, idx, width)

        # data example, see below
        # [
        #     {
        #         'account_code': '000',
        #         'description': 'COA NAME',
        #         'analytic_code': '000',
        #         'start': 0,
        #         'debit': 0,
        #         'credit': 0,
        #         'end': 0,
        #     }
        # ]

        row = col = 0

        date_print = datetime.now().strftime('%d-%b-%Y %H:%M').upper()
        period = options.get('date', {}).get('string', '')

        # titles
        ws.merge_range(row, col, row, col + 3, 'MNC Ledger Detail Trial Balance')
        ws.merge_range(row, col + 4, row, col + 5, f'Report Date: {date_print}')
        ws.merge_range(row + 1, col + 2, row + 1, col + 3, f'Period: {period}')

        row += 3

        ws.write(row, col + 1, 'Currency: IDR')
        ws.write(row + 1, col + 1, 'Balance Type: Year to Date')
        ws.write(row + 2, col + 1, 'Ledger: MNC Ledger')
        ws.write(row + 3, col + 1, f'Company: {self.env.company.name}')

        row += 5

        headers = [
            'Account', 'Description', 'Analytic', 'Beginning Balance',
            'Debits', 'Credits', 'Ending Balance',
        ]
        for idx, header in enumerate(headers):
            ws.write(row, col + idx, header, normal_border)

        row += 1

        # loop data list and manage to print contents
        for dt in data:
            ws.write(row, col, dt['account_code'])
            ws.write(row, col + 1, dt['description'], normal_border)
            ws.write(row, col + 2, dt['analytic_code'], normal_border)
            ws.write(row, col + 3, dt['start'], normal_border)
            ws.write(row, col + 4, dt['debit'], normal_border)
            ws.write(row, col + 5, dt['credit'], normal_border)
            ws.write(row, col + 6, dt['end'], normal_border)

            row += 1

    def get_xlsx(self, response, data={}):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)

        self._get_normal_sheet(wb, data.get('normal', {}))
        self._get_detail_sheet(wb, data.get('detail', {}))

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
