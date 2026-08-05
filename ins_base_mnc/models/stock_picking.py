from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    allowed_user_ids = fields.Many2many('res.users', string='Allowed Users')
    assignee_id = fields.Many2one('res.assignee', 'Assignee')
    pr_numbers = fields.Char(string="PR Numbers", compute='_compute_pr_numbers')
    po_numbers = fields.Char(string="PO Numbers", compute='_compute_po_numbers', store=True)
    purchase_id = fields.Many2one('purchase.order', related='move_lines.purchase_line_id.order_id',
                                  string="Purchase Orders", readonly=True, store=True)
    # po_numbers_store = fields.Char(string="PO Numbers", compute='_compute_po_numbers_store', store=True)
    requestor_comp = fields.Char(string="Requestor", compute='_compute_requestor', store=True)
    buyer_id = fields.Many2one('res.buyer', 'Buyer')
    document = fields.Char(string="Document")
    is_returned = fields.Boolean(string="Is Returned", compute='_compute_returned')

    @api.depends('move_ids_without_package')
    def _compute_pr_numbers(self):
        for record in self:
            pr_number_list = []
            for line in record.move_ids_without_package:
                pr_number_list.append(line.purchase_request_number if line.purchase_request_number else '')

            pr_number_list = list(set(pr_number_list))
            pr_number_list.sort()
            pr_numbers = ', '.join(pr_number_list)
            record.pr_numbers = pr_numbers

    @api.depends('move_ids_without_package')
    def _compute_po_numbers(self):
        for record in self:
            po_number_list = []
            for line in record.move_ids_without_package:
                po_number_list.append(line.purchase_order_number if line.purchase_order_number else '')

            po_number_list = list(set(po_number_list))
            po_number_list.sort()
            po_numbers = ', '.join(po_number_list)
            record.po_numbers = po_numbers

    @api.depends('move_ids_without_package')
    def _compute_returned(self):
        for record in self:
            qty_return = sum(record.move_ids_without_package.mapped('quantity_return'))
            record.is_returned = qty_return > 0

    # @api.depends('po_numbers')
    # def _compute_po_numbers_store(self):
    #     for record in self:
    #         record.po_numbers_store = record.po_numbers

    @api.depends('move_ids_without_package')
    def _compute_requestor(self):
        for record in self:
            req_number_list = []
            for line in record.move_ids_without_package:
                req_number_list.append(line.requested_by.name if line.requested_by else '')

            req_number_list = list(set(req_number_list))
            req_number_list.sort()
            requestor_comp = ', '.join(req_number_list)
            record.requestor_comp = requestor_comp

    def emergency_cancel(self):
        # TODO FIXME remove after
        for rec in self:
            rec.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        res = super(StockPicking, self).create(vals)
        if vals.get('move_ids_without_package', []):
            lines = vals.get('move_ids_without_package', [])
            for idx, line in enumerate(lines):
                line[2]['line_number'] = idx + 1
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(StockPicking, self).write(vals)
        # find move_ids_without_package, rewrite the line number
        for idx, line in enumerate(self.move_ids_without_package):
            line.line_number = idx + 1
        return res

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        # create new outstanding receiving after return receive
        self.ensure_one()
        # for rec in self:
        if self.purchase_id and self.picking_type_id.sequence_code == 'OUT' \
                and self.move_lines.filtered(lambda x: x.state not in ('done', 'cancel')):
            #     back_order_receive = []
            #     for stock_move in self.move_lines:
            # #     if rec.purchase_id and rec.picking_type_id.sequence_code == 'OUT':
            #         # back_order_receive = []
            #         # for stock_move in rec.move_lines:
            #         print(stock_move.origin_returned_move_id.id,'stock_move in nya')
            #         back_order_receive.append(stock_move.origin_returned_move_id.picking_id.id)
            #     print(back_order_receive,type(back_order_receive),'isi apa', list(set(back_order_receive)))
            #     receive = list(set(back_order_receive))
            #     pickings = self.env['stock.picking']
            #     picking = pickings.browse(receive)
            #     print(picking)
            picking_type_id = self.picking_type_id.return_picking_type_id.id
            picking_name = self.origin.strip("Return of ")
            print(self.origin,"nama picking",picking_name)
            backorder_picking = self.copy({
                'name': '/',
                'picking_type_id': picking_type_id,
                'origin': picking_name,
                'has_deadline_issue': False,
                'state': 'assigned',
                'location_id': self.location_dest_id.id,
                'location_dest_id': self.location_id.id
            })
            print(backorder_picking, 'masuk backorder')
            pick = self.env['stock.picking']
            self.message_post(
                body=_(
                    'The New Receiving <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                         backorder_picking.id, backorder_picking.name))

            pick |= backorder_picking
            pick.action_assign()
            if self.purchase_id.state != 'purchase':
                self.purchase_id.write({'state': 'purchase'})
        return res

    # def button_validate(self):
    #     res = super(StockPicking, self).button_validate()
    #     for rec in self:
    #         if rec.pr_numbers:
    #             purchase_order = self.env['purchase.order'].search([
    #                 ('pr_numbers', '=', rec.pr_numbers),
    #                 ('state', '=', 'purchase')])
    #             po_lines = purchase_order.order_line
    #             picking_lines = rec.move_ids_without_package
    #             if picking_lines and purchase_order:
    #                 for po_item in po_lines:
    #                     for pick_item in picking_lines:
    #                         if po_item.product_id.id == pick_item.product_id.id:
    #                             qty_done = pick_item.quantity_done
    #                             qty_demanded = pick_item.product_uom_qty
    #                             qty_po = po_item.product_qty
    #                             qty_po_receive = po_item.qty_received
    #                             qty_residual = qty_po - qty_done
    #                             if qty_demanded == qty_done:
    #                                 if qty_residual < 0 and qty_demanded == qty_po_receive:
    #                                     raise UserError(_('Already receive all qty or one product received all qty from PO'))
    #                             else:
    #                                 raise UserError(_('Quantity is not the same as demanded, make sure to edit quantity done first'))
    #     return res

    @api.model
    def _get_valid_locations(self):
        """ helper function to get default locations from user """
        user = self.user_id or self.env.user
        locations = user.location_ids
        locations = [(6, 0, locations.ids)]
        return locations

    valid_location_ids = fields.Many2many('stock.location',
                                          string='Valid Locations',
                                          default=_get_valid_locations)

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        """ inherit function to set location_dest_id to False """
        super(StockPicking, self).onchange_picking_type()
        # only set to False if receipt
        if self.picking_type_code == 'incoming':
            self.location_dest_id = False

    def name_get(self):
        """  """
        # check the context existence
        is_return = self._context.get('is_return', False)
        if is_return:
            result = []
            for rec in self:
                name = '%s (%s)' % (rec.name, rec.origin)
                result.append((rec.id, name))
            return result
        else:
            res = super(StockPicking, self).name_get()
            return res
