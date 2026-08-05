from datetime import datetime
import io
import xlsxwriter
from odoo import api, fields, models, _
from odoo.tools.misc import format_date, get_lang


class AccountGeneralLedger(models.AbstractModel):
    _inherit = 'account.general.ledger'

    @api.model
    def _get_columns_name(self, options):
        """ inherit function to add header """
        res = super(AccountGeneralLedger, self)._get_columns_name(options)
        # add to index 1
        res.insert(1, {'name': 'Account Name'})
        res.insert(5, {'name': 'Faktur Pajak'})
        return res

    @api.model
    def _get_templates(self):
        """ inherit function to replace template with custom """
        templates = super(AccountGeneralLedger, self)._get_templates()
        templates['line_template'] = 'ins_base_mnc.line_template_general_ledger_report_mnc'
        return templates

    @api.model
    def _get_account_title_line(self, options, account, amount_currency, debit, credit, balance, has_lines):
        """ override function to use only code for name and change colspan """
        has_foreign_currency = account.currency_id and account.currency_id != account.company_id.currency_id or False
        unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')

        # change name variable and colspan
        # name = '%s\t\t\t%s' % (account.code, account.name)
        name = account.code
        # show_name = u'%s \t \t%s' % (account.code, account.name)
        # show_name = f'{account.code}\t\t\t{account.name}'
        max_length = self._context.get('print_mode') and 100 or 60
        if len(name) > max_length and not self._context.get('no_format'):
            name = name[:max_length] + '...'
        columns = [
            {'name': self.format_value(debit), 'class': 'number'},
            {'name': self.format_value(credit), 'class': 'number'},
            {'name': self.format_value(balance), 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            columns.insert(0, {'name': has_foreign_currency and self.format_value(amount_currency, currency=account.currency_id, blank_if_zero=True) or '', 'class': 'number'})
        return {
            'id': 'account_%d' % account.id,
            'name': name,
            'account_name': account.name,
            'title_hover': name,
            'columns': columns,
            'level': 2,
            'unfoldable': has_lines,
            'unfolded': has_lines and 'account_%d' % account.id in options.get('unfolded_lines') or unfold_all,
            'colspan': 5,
            'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
        }

    @api.model
    def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
        """ inherit function to change colspan from 4 to 5 """
        # inherit and change colspan
        res = super(AccountGeneralLedger, self)._get_initial_balance_line(
            options, account, amount_currency, debit, credit, balance)
        res['colspan'] = 6
        return res

    @api.model
    def _get_aml_line(self, options, account, aml, cumulated_balance):
        """ override function to add account name to first columns """
        if aml['payment_id']:
            caret_type = 'account.payment'
        else:
            caret_type = 'account.move'

        if aml['ref'] and aml['name']:
            title = '%s - %s' % (aml['name'], aml['ref'])
        elif aml['ref']:
            title = aml['ref']
        elif aml['name']:
            title = aml['name']
        else:
            title = ''

        if (aml['currency_id'] and aml['currency_id'] != account.company_id.currency_id.id) or account.currency_id:
            currency = self.env['res.currency'].browse(aml['currency_id'])
        else:
            currency = False

        columns = [
            {'name': format_date(self.env, aml['date']), 'class': 'date'},
            {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']), 'title': title, 'class': 'whitespace_print o_account_report_line_ellipsis'},
            {'name': aml['partner_name'], 'title': aml['partner_name'], 'class': 'whitespace_print'},
            {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
            {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
            {'name': self.format_value(cumulated_balance), 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            columns.insert(3, {'name': currency and aml['amount_currency'] and self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True) or '', 'class': 'number'})

        # add to first place empty slot just to make sure it is tidy
        columns.insert(0, {'name': ''})

        # add to 5th place the tax_invoice_id
        faktur = ''
        move_line = self.env['account.move.line'].browse(aml['id'])
        if move_line:
            faktur = move_line.move_id.tax_invoice_id.name
        columns.insert(4, {'name': faktur})

        return {
            'id': aml['id'],
            'caret_options': caret_type,
            'class': 'top-vertical-align',
            'parent_id': 'account_%d' % aml['account_id'],
            'name': aml['move_name'],
            'columns': columns,
            'level': 2,
        }

    @api.model
    def _get_load_more_line(self, options, account, offset, remaining, progress):
        """ inherit function and change colspan """
        res = super(AccountGeneralLedger, self)._get_load_more_line(
            options, account, offset, remaining, progress)
        res['colspan'] = self.user_has_groups('base.group_multi_currency') and 9 or 8
        return res

    @api.model
    def _get_account_total_line(self, options, account, amount_currency, debit, credit, balance):
        """ inherit function and change colspan """
        res = super(AccountGeneralLedger, self)._get_account_total_line(
            options, account, amount_currency, debit, credit, balance)
        res['colspan'] = 6
        return res

    @api.model
    def _get_total_line(self, options, debit, credit, balance):
        """ inherit function and change colspan """
        res = super(AccountGeneralLedger, self)._get_total_line(
            options, debit, credit, balance)
        res['colspan'] = self.user_has_groups('base.group_multi_currency') and 7 or 6
        return res

    @api.model
    def _get_tax_declaration_lines(self, options, journal_type, taxes_results):
        """ override function to change colspan """
        lines = [{
            'id': 0,
            'name': _('Tax Declaration'),
            'columns': [{'name': ''}],
            'colspan': self.user_has_groups('base.group_multi_currency') and 9 or 8,
            'level': 1,
            'unfoldable': False,
            'unfolded': False,
        }, {
            'id': 0,
            'name': _('Name'),
            'columns': [{'name': v} for v in ['', _('Base Amount'), _('Tax Amount'), '']],
            'colspan': self.user_has_groups('base.group_multi_currency') and 6 or 5,
            'level': 2,
            'unfoldable': False,
            'unfolded': False,
        }]

        tax_report_date = options['date'].copy()
        tax_report_date['strict_range'] = True
        tax_report_options = self.env['account.generic.tax.report']._get_options()
        tax_report_options.update({
            'tax_grids': False,
            'date': tax_report_date,
            'journals': options['journals'],
            'all_entries': options['all_entries'],
            'tax_report': 0,
        })
        journal = self.env['account.journal'].browse(self._get_options_journals(options)[0]['id'])
        tax_report_lines = self.env['account.generic.tax.report'].with_company(journal.company_id)._get_lines(tax_report_options)

        for tax_line in tax_report_lines:
            if tax_line['id'] not in ('sale', 'purchase'):  # We want to exclude title lines here
                tax_line['columns'].append({'name': ''})
                tax_line['colspan'] = self.user_has_groups('base.group_multi_currency') and 7 or 6
                lines.append(tax_line)

        return lines

    def get_xlsx(self, options, response=None):
        """ override function to add account_name """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        # Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 0
        headers, lines = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)._get_table(options)

        # Add headers.
        for header in headers:
            x_offset = 0
            for column in header:
                column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                colspan = column.get('colspan', 1)
                if colspan == 1:
                    sheet.write(y_offset, x_offset, column_name_formated, title_style)
                else:
                    sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated, title_style)
                x_offset += colspan
            y_offset += 1

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        # Add lines.
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            # NOTE: special case for ledger, add account name
            sheet.write(y + y_offset, 1, lines[y].get('account_name', ''), col1_style)

            # write all the remaining cells
            for x in range(2, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        return generated_file
