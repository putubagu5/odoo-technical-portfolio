from odoo import api, fields, models, _


class AccountCoaReport(models.AbstractModel):
    _inherit = 'account.coa.report'

    # filter_currency = True


    def _get_reports_buttons(self):
        """ inherit function to add print report buttons """
        res = super(AccountCoaReport, self)._get_reports_buttons()
        res.append({'name': 'Print Report TB', 'action': 'view_report_tb_wizard'})
        return res

    def view_report_tb_wizard(self, options):
        """  """
        form = self.env.ref('ins_base_mnc.view_trial_balance_form', False)
        options.pop('headers')

        # pass data as report data for Trial Balance report
        options['data'] = self.with_context(
            no_format=True, print_mode=True, prefetch_fields=False)._get_table(options)

        return {
            'name': 'Trial Balance Print',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.trial.balance',
            'view_mode': 'form',
            'view_id': form.id,
            'views': [(form.id, 'form')],
            'multi': 'True',
            'target': 'new',
            'context': options,
        }

    @api.model
    def _get_columns(self, options):
        """ inherit function to add headers """
        # add header to the index 1 of the parent header
        header1, header2 = super(AccountCoaReport, self)._get_columns(options)
        header1.insert(1, {'name': 'Account Name', 'class': 'number'})
        header2.insert(1, {'name': '', 'class': 'o_account_coa_column_contrast'})
        return [header1, header2]

    @api.model
    def _get_lines(self, options, line_id=None):
        """ override function to inject the account name """
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute all sums/unaffected earnings/initial balances for all comparisons.
        new_options = options.copy()
        new_options['unfold_all'] = True
        options_list = self._get_options_periods_list(new_options)
        accounts_results, taxes_results = self.env['account.general.ledger']._do_query(options_list, fetch_lines=False)

        lines = []
        # NOTE: add to first element of totals
        totals = [0] + [0.0] * (2 * (len(options_list) + 2))

        # Add lines, one per account.account record.
        for account, periods_results in accounts_results:
            sums = []
            account_balance = 0.0
            sums += [account.name]  # NOTE: add account.name
            for i, period_values in enumerate(reversed(periods_results)):
                account_sum = period_values.get('sum', {})
                account_un_earn = period_values.get('unaffected_earnings', {})
                account_init_bal = period_values.get('initial_balance', {})

                if i == 0:
                    # Append the initial balances.
                    initial_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
                    sums += [
                        initial_balance > 0 and initial_balance or 0.0,
                        initial_balance < 0 and -initial_balance or 0.0,
                    ]
                    account_balance += initial_balance

                # Append the debit/credit columns.
                sums += [
                    account_sum.get('debit', 0.0) - account_init_bal.get('debit', 0.0),
                    account_sum.get('credit', 0.0) - account_init_bal.get('credit', 0.0),
                ]
                account_balance += sums[-2] - sums[-1]

            # Append the totals.
            sums += [
                account_balance > 0 and account_balance or 0.0,
                account_balance < 0 and -account_balance or 0.0,
            ]

            # account.account report line.
            columns = []
            for i, value in enumerate(sums):
                # Update totals.
                # NOTE: check the value type if not string then number
                val = value
                col_class = 'text'
                if type(val) is not str:
                    totals[i] += value
                    val = self.format_value(value, blank_if_zero=True)
                    col_class = 'number'

                # NOTE: change line below to use variables
                # Create columns.
                columns.append({'name': val, 'class': col_class, 'no_format_name': val})

            # name = account.name_get()[0][1]
            name = account.code

            lines.append({
                'id': account.id,
                'name': name,
                'title_hover': name,
                'columns': columns,
                'unfoldable': False,
                'caret_options': 'account.account',
                'class': 'o_account_searchable_line o_account_coa_column_contrast',
            })

        # add all columns for total, but pop the first and add empty name
        cols = [{'name': self.format_value(total), 'class': 'number'} for total in totals]
        # cols.pop(0)
        cols.pop(0)
        cols = [{'name': ''}] + cols
        # Total report line.
        lines.append({
            'id': 'grouped_accounts_total',
            'name': _('Total'),
            'class': 'total o_account_coa_column_contrast',
            'columns': cols,
            'level': 1,
        })

        return lines
