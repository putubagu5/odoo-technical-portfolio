from datetime import date
from io import BytesIO
import xlsxwriter
from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)


class SettlementCaReport(models.Model):
    _name = 'settlement.ca.report'

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    company_id = fields.Many2one('res.company')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')], 'Status')

    @api.onchange('date_from', 'date_to')
    def onchange_periode(self):
        if self.date_from and self.date_to:
            if self.date_to < self.date_from:
                return {
                    'value': {
                        'date_end': None,
                        'date_start': None,
                    },
                    'warning': {
                        'title': 'Warning',
                        'message': 'Cannot back date!',
                    },
                }

    def _get_moves(self):
        """ function to get valid moves """
        # get all moves within filter date with bill_type prepayment, sort by date
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('bill_type', '=', 'prepayment'),
        ]

        # add domain with state and company_id if filter is filled

        if self.state:
            domain += [('state', '=', self.state)]

        if self.company_id:
            domain += [('company_id', '=', self.company_id.id)]

        moves = self.env['account.move'].search(domain, order='date')
        return moves

    def _get_settlement_moves(self, move_id):
        """ helper function to get settlement moves by move_id """
        domain = [
            ('invoice_line_ids.account_move_prepayment_match_id', '=', move_id),
        ]
        moves = self.env['account.move'].search(domain, order='date')
        return moves

    def _group_moves(self, moves):
        """ function to group moves """
        print()

    def _prepare_report_data(self):
        """ function to prepare report data containing dict """
        # NOTE: the report will be grouped by vendors (res.partner)

        # get valid moves, keep in variable, do loop per point
        # 1. setdefault to partner_id as key, value is dict
        # 2. setdefault to payment_reference as key, value is dict
        # 3. setdefault to name as key, value is dict
        # example:
        # {
        #     'partner_1': {
        #         'name': 'name',
        #         'site': 'site',
        #         'department': 'department',
        #         'lines': {
        #             'payment_reference_1': {
        #                 'name': 'name1',
        #                 'employee': 'employee',
        #                 'date': 'date',
        #                 'amount': 'amount',
        #                 'project': 'project',
        #                 'task': 'task',
        #                 'invoices': {
        #                     'inv1': {
        #                         'name': 'number',
        #                         'type': 'type',
        #                         'date': 'date',
        #                         'amount': 'amount',
        #                     },
        #                 },
        #             },
        #         },
        #     },
        # }

        result = {}

        vendor_dict = {}
        moves = self._get_moves()

        # first loop: constructing vendor_dict
        for move in moves:
            vendor_dict.setdefault(move.partner_id.id, {
                'name': move.partner_id.name,
                'site': move.sites_id.name,
                'department': '',
                'lines': {},
            })

        # second loop: constructing lines
        for move in moves:
            line_dict = vendor_dict[move.partner_id.id]['lines']
            line_dict.setdefault(move.payment_reference, {})
            line_dict[move.payment_reference] = {
                'name': move.payment_reference,
                'employee': move.employee_text or '',
                'date': move.date.strftime('%d-%b-%y') if move.date else '',
                'amount': move.amount_total,
                'project': '',
                'task': '',
                'invoices': {},
            }

        # third loop: constructing settlement invoices. To obtain settlement
        # invoices, brute search the account.move with field
        # invoice_line_ids.account_move_prepayment_match_id equals to move.id
        # sort by date
        for move in moves:
            line_dict = vendor_dict[move.partner_id.id]['lines']
            inv_dict = line_dict[move.payment_reference]['invoices']
            settlement_moves = self._get_settlement_moves(move.id)
            for mv in settlement_moves:
                # NOTE: need to filter one more time due to the nature of the
                # invoice. Sum all price_subtotal of the lines, but abs first
                tmp_move = mv.invoice_line_ids.filtered(lambda x: x.account_move_prepayment_match_id == move)
                amt_move = sum(abs(x.price_subtotal) for x in tmp_move)
                inv_dict.setdefault(mv.id, {})
                inv_dict[mv.id] = {
                    'name': mv.payment_reference or mv.name or '',
                    'type': mv.bill_type,
                    'date': mv.date.strftime('%d-%b-%y') if mv.date else '',
                    'amount': amt_move,
                }

        result = {
            'vendor_data': vendor_dict,
        }

        return result

    def print_report(self):
        """ function to print report """
        self.ensure_one()
        name = 'Settlement CA %s - %s' % (self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/xls_report/%s/%s/%s' % (self._name, self.id, name),
            'target': 'new',
        }

    def get_xlsx(self, response, data={}):
        """ function to generate xls report """
        fp = BytesIO()
        wb = xlsxwriter.Workbook(fp)
        ws = wb.add_worksheet('Settlement CA')

        f_title = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 14, 'font_name': 'Arial',
        })

        f_title2 = wb.add_format({
            'bold': 1, 'align': 'left', 'font_size': 10, 'font_name': 'Arial',
        })

        f_header_border = wb.add_format({
            'bold': 1, 'align': 'left', 'font_size': 10, 'font_name': 'Arial',
        })
        f_header_border.set_top(1)
        f_header_border.set_left(1)
        f_header_border.set_right(1)

        f_header_border2 = wb.add_format({
            'bold': 1, 'align': 'left', 'font_size': 10, 'font_name': 'Arial',
        })
        f_header_border2.set_left(1)
        f_header_border2.set_right(1)

        f_header_border3 = wb.add_format({
            'bold': 1, 'align': 'left', 'font_size': 10, 'font_name': 'Arial',
        })

        f_header_border3.set_left(1)
        f_header_border3.set_right(1)
        f_header_border3.set_bottom(1)

        f_header_vendor_border = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })
        f_header_vendor_border.set_bg_color('#969696')

        f_header_border3.set_left(1)
        f_header_border3.set_right(1)

        f_total_vendor = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })
        f_total_vendor.set_bg_color('#ffcc99')

        f_total_vendor2 = wb.add_format({
            'bold': 1, 'align': 'left', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })
        f_total_vendor2.set_bg_color('#ffcc99')

        f_total_vendor3 = wb.add_format({
            'bold': 1, 'align': 'right', 'font_size': 10, 'font_name': 'Arial',
            'border': 1, 'num_format': '#,##0'
        })
        f_total_vendor3.set_bg_color('#ffcc99')

        f_body_border = wb.add_format({
            'align': 'center', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })
        f_body_str_left = wb.add_format({
            'align': 'left', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })

        f_body_date = wb.add_format({
            'align': 'right', 'num_format': 'd-mmm-yy', 'font_size': 10,
            'border': 1,
        })

        f_body_num_right = wb.add_format({
            'align': 'right', 'font_size': 10, 'font_name': 'Arial',
            'border': 1, 'num_format': '#,##0'
        })

        f_total_vendor_grand = wb.add_format({
            'bold': 1, 'align': 'left', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })
        f_total_vendor_grand.set_bg_color('#00ccff')

        f_total_vendor_null_blue = wb.add_format({
            'bold': 1, 'align': 'center', 'font_size': 10, 'font_name': 'Arial',
            'border': 1,
        })
        f_total_vendor_null_blue.set_bg_color('#00ccff')

        f_total_vendor_pay_amount = wb.add_format({
            'bold': 1, 'align': 'right', 'font_size': 10, 'font_name': 'Arial',
            'border': 1, 'num_format': '#,##0'
        })
        f_total_vendor_pay_amount.set_bg_color('#00ccff')

        # set width
        width = [10, 38, 38, 16, 18, 7, 5, 38, 11, 11, 38, 18]
        for idx, w in enumerate(width):
            ws.set_column(idx, idx, w)

        # static headers
        headers = [
            'Employee', 'Prepayment Invoice', 'Prepayment Date', 'Prepayment Amount',
            'Project', 'Task', 'Invoice Number', 'Invoice Type', 'Invoice Date',
            'Settlement Amount', 'Outstanding Amount'
        ]

        date_print = date.today().strftime('%d-%b-%Y').upper()
        date_from = self.date_from.strftime('%d-%b-%Y').upper()
        date_to = self.date_to.strftime('%d-%b-%Y').upper()
        company = self.company_id.name if self.company_id else self.env.company.name

        row = col = 0

        # title
        ws.merge_range('B4:L4', 'SETTLEMENT & OUTSTANDING REPORT', f_title)
        ws.merge_range('B5:L5', '----------------------------------------------------------------------------------------------', f_title)

        ws.merge_range('B6:L6', 'Print Date : ' + date_print, f_title2)
        ws.merge_range('B7:L7', company, f_title2)
        ws.merge_range('B8:L8', 'Prepayment Date : ' + date_from + ' - ' + date_to, f_title2)

        row += 9  # start from row index 9 (real 10)
        col = 1  # start from col index 1

        vendors = data.get('vendor_data', {})
        for vendor in vendors.values():
            amt_vendor = 0  # to store the last total (in blue)
            amt_prepayment_total = 0  # to store the prepayment amount as it is

            ws.merge_range(row, col, row, col + 10, f'Supplier: {vendor["name"]}', f_header_border)
            ws.merge_range(row + 1, col, row + 1, col + 10, f'Supplier Site: {vendor["site"]}', f_header_border2)
            ws.merge_range(row + 2, col, row + 2, col + 10, f'Department: {vendor["department"]}', f_header_border3)

            row += 3

            # print static headers
            for hidx, header in enumerate(headers):
                ws.write(row, col + hidx, header, f_header_vendor_border)

            row += 1

            prepayment_invoices = vendor['lines']
            for pinv in prepayment_invoices.values():
                amt_prepayment = pinv['amount']  # set amount to prepayment
                amt_prepayment_total += pinv['amount']

                ws.write(row, col, pinv['employee'], f_body_border)
                ws.write(row, col + 1, pinv['name'], f_body_str_left)
                ws.write(row, col + 2, pinv['date'], f_body_date)
                ws.write(row, col + 3, pinv['amount'], f_body_num_right)
                ws.write(row, col + 4, pinv['project'], f_body_border)
                ws.write(row, col + 5, pinv['task'], f_body_str_left)

                inv_col = col + 6
                # check for `invoices`
                for inv in pinv['invoices'].values():
                    amt_prepayment -= inv['amount']  # subtract with invoice amount
                    ws.write(row, inv_col, inv['name'], f_body_str_left)
                    ws.write(row, inv_col + 1, inv['type'], f_body_border)
                    ws.write(row, inv_col + 2, inv['date'], f_body_date)
                    ws.write(row, inv_col + 3, inv['amount'], f_body_num_right)
                    ws.write(row, inv_col + 4, amt_prepayment, f_body_num_right)  # print the remaining
                    row += 1

                if not pinv['invoices']:
                    ws.write(row, inv_col, '', f_body_str_left)
                    ws.write(row, inv_col + 1, '', f_body_border)
                    ws.write(row, inv_col + 2, '', f_body_date)
                    ws.write(row, inv_col + 3, '', f_body_num_right)
                    ws.write(row, inv_col + 4, '', f_body_num_right)
                    row += 1

                # total
                ws.merge_range(row, col, row, col + 8, '', f_total_vendor)
                ws.write(row, col + 9, f'TOTAL {pinv["name"]}', f_total_vendor2)
                ws.write(row, col + 10, amt_prepayment, f_total_vendor3)  # print the remaining total if any

                amt_vendor += amt_prepayment  # add the rest

                row += 1

            ws.merge_range(row, col, row, col + 2, f'Grand Total: {vendor["name"]}', f_total_vendor_grand)
            ws.write(row, col + 3, amt_prepayment_total, f_total_vendor_pay_amount)
            ws.merge_range(row, col + 4, row, col + 9, '', f_total_vendor_null_blue)
            ws.write(row, col + 10, amt_vendor, f_total_vendor_pay_amount)

            row += 2

        wb.close()
        fp.seek(0)
        response.stream.write(fp.read())
        fp.close()
