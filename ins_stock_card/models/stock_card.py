from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class StockCard(models.Model):
    _name = 'stock.card'
    _description = 'Stock Card'

    name = fields.Char('Number', copy=False, default='/')
    date_start = fields.Datetime('From', default=fields.date.today())
    date_end = fields.Datetime('To', default=fields.date.today())
    location_id = fields.Many2one('stock.location', 'Location')
    product_id = fields.Many2one('product.product', 'Product')
    line_ids = fields.One2many('stock.card.line', 'stock_card_id', 'Details')
    user_id = fields.Many2one('res.users', 'Responsible',
                              default=lambda self: self.env.uid)
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
        res = super(StockCard, self).create(vals)
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
        """ generate stock card """
        lines = [(2, ln.id, 0) for ln in self.line_ids]  # remove old lines
        location = self.location_id
        product = self.product_id

        date_prev = self.date_start + relativedelta(days=-1)  # get day before
        # get qty_available till the day before in the location
        qty_start = product.with_context({
            'to_date': date_prev,
            'location': location.id,
        }).qty_available

        value = product.with_context({
            'to_date': date_prev,
            'location': location.id,
        }).value_svl

        price = product.with_context({
            'to_date': date_prev,
            'location': location.id,
        }).standard_price

        init_data = {
            'stock_card_id': self.id,
            'date': False,
            'qty_start': 0.0,
            'qty_in': 0.0,
            'qty_out': 0.0,
            'qty_balance': qty_start,
            'price': price,
            'value': value,
            'product_uom_id': product.uom_id.id,
            'name': 'Initial',
        }
        lines.append((0, 0, init_data))  # add to line

        # get all done moves that move in/out to location within certain date
        domain = [
            ('product_id', '=', product.id),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('state', '=', 'done'),
            '|',
            ('location_dest_id', '=', location.id),
            ('location_id', '=', location.id),
        ]
        moves = self.env['stock.move'].search(domain, order='date asc')
        for move in moves:
            qty_in = qty_out = 0.0
            # if location_dest_id == location means in, else out
            if location == move.location_dest_id:
                qty_in = move.product_uom_qty
            elif location == move.location_id:
                qty_out = move.product_uom_qty

            balance = qty_start + qty_in - qty_out

            value = move.product_id.with_context({
                'to_date': move.date,
                'location': move.location_id.id,
            }).value_svl

            price = move.product_id.with_context({
                'to_date': move.date,
                'location': move.location_id.id,
            }).standard_price

            # prepare data
            data = {
                'stock_card_id': self.id,
                'move_id': move.id,
                'picking_id': move.picking_id.id,
                'date': move.date,
                'qty_start': qty_start,
                'qty_in': qty_in,
                'qty_out': qty_out,
                'qty_balance': balance,
                'product_uom_id': product.uom_id.id,
                'name': move.name,
                'price': price,
                'value': value,
            }

            lines.append((0, 0, data))
            qty_start = balance  # use last balance as start
        self.line_ids = lines
        return True
