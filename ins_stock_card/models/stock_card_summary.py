from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone
from odoo import api, fields, models


class StockCardSummary(models.Model):
    _name = 'stock.card.summary'
    _description = 'Stock Card Summary'

    name = fields.Char('Number', default='/')
    date_start = fields.Datetime('Date Start', default=fields.Date.today())
    date_end = fields.Datetime('Date End', default=fields.Date.today())
    location_id = fields.Many2one('stock.location', 'Location')
    line_ids = fields.One2many('stock.card.summary.line', 'summary_id',
                               'Details')
    user_id = fields.Many2one('res.users', 'Responsible',
                              default=lambda self: self.env.uid)
    product_ids = fields.Many2many('product.product', string='Products',
                                   help='Keep empty to process all products')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Done'),
    ], 'State', default='draft')

    @api.model
    def create(self, vals):
        """ override create function to generate sequence """
        if vals.get('name') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.card')
        res = super(StockCardSummary, self).create(vals)
        return res

    def button_open(self):
        """ change state to open """
        for rec in self:
            rec.write({'state': 'open'})
        return True

    def button_done(self):
        """ change state to done """
        for rec in self:
            rec.write({'state': 'done'})
        return True

    def button_calculate(self):
        """ generate stock card summary """
        location = self.location_id.id
        lines = [(2, x.id, 0) for x in self.line_ids]  # reset all lines
        products = self.product_ids.ids
        date_prev = self.date_start + timedelta(seconds=-1)  # get day before

        # convert timezone to use Asia/Jakarta
        utc = pytz.utc
        tz = timezone(self.env.user.tz or 'Asia/Jakarta')
        # create date string with start and end
        date_start_obj = self.date_start.replace(tzinfo=tz).astimezone(utc)
        date_end_obj = self.date_end.replace(tzinfo=tz).astimezone(utc)
        # reconvert to string now in utc
        date_start = date_start_obj.strftime('%Y-%m-%d %H:%M:%S')
        date_end = date_end_obj.strftime('%Y-%m-%d %H:%M:%S')

        # find all active products, filter if any
        p_domain = [('active', '=', True)]
        p_domain += [('id', 'in', products)] if products else []
        products = self.env['product.product'].search(p_domain)

        # generate dict containing product data
        product_dict = {}
        for x in products:
            product_dict[x.id] = {
                'uom': '',
                'in': 0,
                'out': 0,
            }

        # filter for incoming products to a location
        sql = """
            SELECT sm.product_id,
            uom.id,
            SUM(sm.product_uom_qty)
            FROM stock_move sm
            JOIN product_product pp ON pp.id = sm.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN uom_uom uom ON uom.id = sm.product_uom
            JOIN stock_location loc_src ON loc_src.id = sm.location_id
            JOIN stock_location loc_dest ON loc_dest.id = sm.location_dest_id
            WHERE sm.date >= '%s'
            AND sm.date <= '%s'
            AND loc_dest.id = '%s'
            AND sm.state = 'done'
            GROUP BY sm.product_id, uom.id
        """ % (date_start, date_end, location)
        self.env.cr.execute(sql)
        incoming = self.env.cr.fetchall()

        for x in incoming:
            if product_dict.get(x[0]):
                product_dict[x[0]]['uom'] = x[1]
                product_dict[x[0]]['in'] += x[2]

        # filter for outgoing products from a location
        sql = """
            SELECT sm.product_id,
            uom.id,
            SUM(sm.product_uom_qty)
            FROM stock_move sm
            JOIN product_product pp ON pp.id = sm.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN uom_uom uom ON uom.id = sm.product_uom
            JOIN stock_location loc_src ON loc_src.id = sm.location_id
            JOIN stock_location loc_dest ON loc_dest.id = sm.location_dest_id
            WHERE sm.date >= '%s'
            AND sm.date <= '%s'
            AND loc_src.id = '%s'
            AND sm.state = 'done'
            GROUP BY sm.product_id, uom.id
        """ % (date_start, date_end, location)
        self.env.cr.execute(sql)
        outgoing = self.env.cr.fetchall()

        for x in outgoing:
            if product_dict.get(x[0]):
                product_dict[x[0]]['uom'] = x[1]
                product_dict[x[0]]['out'] += x[2]

        product = self.env['product.product']
        # loop and add lines using triplet (0, 0, {})
        # reconstruct dict with non-zero in, out, or opname
        product_dict = {k: v for k, v in product_dict.items() if any(
            [v['in'], v['out']])}
        for product_id, info in product_dict.items():
            prod = product.browse(product_id)
            # get starting balance
            start = prod.with_context({
                'to_date': date_prev,
                'location': location,
            }).qty_available

            # NOTE: use start date
            # value = prod.with_context({
            #     'to_date': date_start,
            #     'location': location,
            # }).value_svl

            price = prod.with_context({
                'to_date': date_prev,
                'location': location,
            }).standard_price

            qty_in = info['in']
            qty_out = info['out']

            data = {
                'summary_id': self.id,
                'product_id': product_id,
                'product_uom_id': info['uom'],
                'qty_start': start,
                'qty_in': qty_in,
                'qty_out': qty_out,
                'price': price,
                'qty_balance': (start + qty_in - qty_out),
                'value': ((start + qty_in - qty_out) * price),
            }
            lines.append((0, 0, data))

        self.write({'line_ids': lines})  # write records
        return True
