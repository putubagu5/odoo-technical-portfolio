from odoo import models, tools, fields, api, _
from odoo.exceptions import MissingError, ValidationError, UserError


class ProgramCostsGen21(models.Model):
    _name = "program.costs.gen21"

    name = fields.Char('Name')
    line_ids = fields.One2many('program.costs.line.gen21', 'program_costs_id_gen21', string='Program Costs Line', readonly=True)
    company_id = fields.Many2one('res.company', string='Company')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('wait', 'Waiting To Posted'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='wait')
    is_change = fields.Boolean(string="is change", default=False)
    total_line = fields.Float("Total Line", compute="_compute_total_line")
    total_amount = fields.Float("Total Amount", compute="_compute_total_amount")
    header_attribute1 = fields.Char("PO/Contract Number", compute="_compute_header_line", store=True)
    header_attribute2 = fields.Char("Approval Hierarchy", compute="_compute_header_line", store=True)
    header_attribute3 = fields.Char("Name Program", compute="_compute_header_line", store=True)
    header_attribute4 = fields.Char("Episode No", compute="_compute_header_line", store=True)
    header_attribute5 = fields.Char("Name Title Episode", compute="_compute_header_line", store=True)
    purchase_request_ids = fields.Many2many('purchase.request', string='Related PR',
                                            compute='_compute_purchase_request_id')
    purchase_request_numbers = fields.Char(
        'Purchase Requests', compute='_compute_purchase_request_id', store=True)

    @api.depends('line_ids')
    def _compute_purchase_request_id(self):
        """ compute function to get related PR based on lines """
        for rec in self:
            names = ''
            requests = [(5, 0, 0)]
            keys = rec.line_ids.mapped('uniqkey')
            pr_lines = self.env['purchase.request.line'].search([('uniqkey_gen21', 'in', keys)])
            if pr_lines:
                names = ', '.join(pr_lines.mapped('request_id.name'))
                requests += [(4, x.request_id.id) for x in pr_lines]
            rec.purchase_request_ids = requests
            rec.purchase_request_numbers = names

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('line_ids', []):
            lines = vals.get('line_ids', [])
            for idx, line in enumerate(lines):
                line[2].update({'line_number': idx + 1})
        res = super(ProgramCostsGen21, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(ProgramCostsGen21, self).write(vals)
        # find project_ids, rewrite the line number
        for idx, line in enumerate(self.line_ids):
            line.line_number = idx + 1
        return res

    @api.depends('line_ids')
    def _compute_header_line(self):
        for record in self:
            header_attribute1 = ''
            header_attribute2 = ''
            header_attribute3 = ''
            header_attribute4 = ''
            header_attribute5 = ''
            if len(record.line_ids) > 0:
                for line in record.line_ids:
                    if line.header_attribute1:
                        header_attribute1 = line.header_attribute1

                    if line.header_attribute2:
                        header_attribute2 = line.header_attribute2

                    if line.header_attribute3:
                        header_attribute3 = line.header_attribute3

                    if line.header_attribute4:
                        header_attribute4 = line.header_attribute4

                    if line.header_attribute5:
                        header_attribute5 = line.header_attribute5
            record.header_attribute1 = header_attribute1
            record.header_attribute2 = header_attribute2
            record.header_attribute3 = header_attribute3
            record.header_attribute4 = header_attribute4
            record.header_attribute5 = header_attribute5

    @api.depends('line_ids')
    def _compute_total_line(self):
        """ compute function to calculate total_line """
        for record in self:
            record.total_line = len(record.line_ids)

    @api.depends('line_ids')
    def _compute_total_amount(self):
        """ compute function to calculate total_amount """
        for record in self:
            if len(record.line_ids) > 0:
                record.total_amount = sum([line.unit_price_decimal for line in record.line_ids])
            else:
                record.total_amount = 0

    def _get_currency_name(self, name):
        """ function to get currency data """
        currency = self.env['res.currency'].search([('name', '=', name)])
        return currency.id if currency else False

    def button_post(self):
        if self.is_change:
            for line in self.line_ids:
                request_line = self.env['purchase.request.line'].search([('uniqkey_gen21', '=', line.uniqkey)])
                if request_line:
                    if request_line.request_id.state in ('draft', 'to_approve'):
                        request_line.write({'original_price': line.unit_price})
                    else:
                        raise ValidationError(_("Failed post to PR"))
                self.write({'state': 'posted', 'is_change': False})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
        else:
            data_posted = []
            if len(self.line_ids) > 0:
                new_journal = True
                for line in self.line_ids:
                    if len(data_posted) > 0:
                        for data in data_posted:
                            property_account_expense_id = False
                            uom_id = False
                            filter_product = [
                                ('default_code', '=', line['item_segment1']),
                                ('active', '=', True),
                            ]
                            product_id = self.env['product.product'].search(filter_product)
                            if not product_id:
                                raise MissingError(_("Product does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                if product_id.property_account_expense_id:
                                    property_account_expense_id = product_id.property_account_expense_id.id
                                else:
                                    raise MissingError(_("Set account expense in product. No Item Segment: " + line.item_segment1))
                                if product_id.uom_id:
                                    uom_id = product_id.uom_id.id
                                else:
                                    raise MissingError(_("Set uom in product. No Item Segment: " + line.item_segment1))
                                product_id = product_id[0].id

                            filter_company = [
                                ('org_id', '=', line['org_id']),
                            ]
                            company_id = self.env['res.company'].search(filter_company)
                            if not company_id:
                                raise MissingError(_("Company does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                company_id = company_id[0].id
                            
                            filter_buyer = [
                                ('code', '=', str(line['suggested_buyer_id'])),
                            ]
                            buyer_id = self.env['res.buyer'].search(filter_buyer)
                            if not buyer_id:
                                raise MissingError(_("Buyer does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                buyer_id = buyer_id[0].id

                            filter_analytic = [
                                # ('code', '=', '000'),
                                ('is_default', '=', True),
                                ('company_id', '=', company_id)
                            ]
                            analytic_id = self.env['account.analytic.account'].search(filter_analytic)
                            if not analytic_id:
                                raise MissingError(_("Analytic account does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                analytic_id = analytic_id[0].id

                            name_line = ''
                            if line['attribute1']:
                                name_line = name_line + line['attribute1']
                            if line['attribute4']:
                                name_line = name_line + '-' + line['attribute4']
                            if line['attribute3']:
                                name_line = name_line + '-' + line['attribute3']
                            values_line = (0, 0, {
                                "product_id": product_id,
                                "account_id": property_account_expense_id,
                                "product_uom_id": uom_id,
                                "name": name_line,
                                "uniqkey_gen21": line['uniqkey'],
                                "buyer_id": buyer_id,
                                "analytic_account_id": analytic_id,
                                "product_qty": line['quantity'],
                                "original_price": line['currency_unit_price'] if line['currency_code'] != 'IDR' else line['unit_price'],
                                'select_currency_id': self._get_currency_name(line['currency_code']),
                                'manual_currency_rate': line['currency_rate_price'],
                                'manual_currency_rate_active': True if line['currency_rate_price'] else False,
                                "header_attribute4": line['header_attribute4']
                            })
                            data['line_ids'].append(values_line)
                    if new_journal:
                        filter_request = [
                            ('partner_id.id_users', '=', line['preparer_id']),
                            ('active', '=', True),
                        ]
                        request = self.env['res.users'].search(filter_request)
                        if not request:
                            raise MissingError(_("Request by does not exist or not active. No Item Segment: " + line.item_segment1))
                        hierarchy_id = False
                        approval_hierarchy = self.env['approval.hierarchy.line'].search([])
                        if approval_hierarchy:
                            for approval in approval_hierarchy:
                                if len(approval.employee_ids) > 0:
                                    for employee in approval.employee_ids:
                                        if employee.user_id:
                                            if employee.user_id.id == request.id:
                                                hierarchy_id = approval.hierarchy_id.id
                                                break
                        if not hierarchy_id:
                            raise MissingError(_("Check hierarchy . No Item Segment: " + line.item_segment1))
                        property_account_expense_id = False
                        uom_id = False
                        filter_product = [
                            ('default_code', '=', line['item_segment1']),
                            ('active', '=', True),
                        ]
                        product_id = self.env['product.product'].search(filter_product)
                        if not product_id:
                            raise MissingError(_("Product does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            if product_id.property_account_expense_id:
                                property_account_expense_id = product_id.property_account_expense_id.id
                            else:
                                raise MissingError(_("Set account expense in product. No Item Segment: " + line.item_segment1))
                            if product_id.uom_id:
                                uom_id = product_id.uom_id.id
                            else:
                                raise MissingError(_("Set uom in product. No Item Segment: " + line.item_segment1))
                            product_id = product_id[0].id

                        filter_company = [
                            ('org_id', '=', line['org_id']),
                        ]
                        company_id = self.env['res.company'].search(filter_company)
                        if not company_id:
                            raise MissingError(_("Company does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            company_id = company_id[0].id
                        
                        filter_buyer = [
                            ('code', '=', str(line['suggested_buyer_id'])),
                        ]
                        buyer_id = self.env['res.buyer'].search(filter_buyer)
                        if not buyer_id:
                            raise MissingError(_("Buyer does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            buyer_id = buyer_id[0].id

                        filter_analytic = [
                            ('code', '=', '000'),
                            ('company_id', '=', company_id)
                        ]
                        analytic_id = self.env['account.analytic.account'].search(filter_analytic)
                        if not analytic_id:
                            raise MissingError(_("Analytic account does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            analytic_id = analytic_id[0].id
                        nomer_seq = self.env["ir.sequence"].next_by_code("purchase.request")
                        if not nomer_seq:
                            raise MissingError(_("Sequence does not exist or not active. No Item Segment: " + line.item_segment1))

                        if line['uniqkey'] and line['uniqkey'] != "":
                            filter_purchase_request_line = [
                                ('uniqkey_gen21', '=', line['uniqkey']),
                                ('request_id.state', 'not in', ('rejected', 'returned', 'cancel')),
                                ('request_state', 'not in', ('rejected', 'returned', 'cancel'))
                            ]
                            purchase_request_line = self.env["purchase.request.line"].search(filter_purchase_request_line)
                            if purchase_request_line:
                                raise MissingError(_("Cant duplicated PR No " + purchase_request_line[0].request_id.name + " Number Line: " + str(purchase_request_line[0].line_number) + ". No Item Segment: " + line.item_segment1))

                        name_line = ''
                        if line['header_attribute1']:
                            name_line = name_line + line['header_attribute1']
                        if line['header_attribute3']:
                            name_line = name_line + '-' + line['header_attribute3']
                        if line['header_attribute4']:
                            name_line = name_line + '-' + line['header_attribute4']
                        values = {
                            "name": nomer_seq,
                            "origin": self.name,
                            "requested_by": request.id,
                            "hierarchy_id": hierarchy_id,
                            "description": name_line,
                            "company_id": company_id,
                            "line_ids": [
                                (0, 0, {
                                    "product_id": product_id,
                                    "account_id": property_account_expense_id,
                                    "product_uom_id": uom_id,
                                    "name": name_line,
                                    "uniqkey_gen21": line['uniqkey'],
                                    "buyer_id": buyer_id,
                                    "analytic_account_id": analytic_id,
                                    "product_qty": line['quantity'],
                                    "original_price": line['currency_unit_price'] if line['currency_code'] != 'IDR' else line['unit_price'],
                                    'select_currency_id': self._get_currency_name(line['currency_code']),
                                    'manual_currency_rate': line['currency_rate_price'],
                                    'manual_currency_rate_active': True if line['currency_rate_price'] else False,
                                    "header_attribute4": line['header_attribute4']
                                })
                            ],
                            "state": "draft",
                            "is_post_gen21": True,
                        }
                        data_posted.append(values)
                        new_journal = False
                if len(data_posted) > 0:
                    purchase_request = self.env['purchase.request'].create(data_posted)
                    if purchase_request:
                        self.write({'state': 'posted'})
                    else:
                        raise ValidationError(_("Failed null data Program Costs"))
            else:
                raise ValidationError(_("Failed null data Program Costs"))
        return True

    def button_bundle_post(self):
        data_posted = []
        new_journal = True
        for record in self:
            if record.state == 'posted':
                raise ValidationError(_("Failed posting status bundle posted"))

        number_po_gen21 = ''
        check_loop = 0
        for record in self:
            if len(record.line_ids) == 0:
                raise ValidationError(_("Failed posting line null"))
            else:
                for line in record.line_ids:
                    if not line.header_attribute1:
                        raise ValidationError(_("Failed PO Numbers Gen21 Not Null : " + line.item_segment1))
                    if check_loop == 0:
                        number_po_gen21 = line.header_attribute1
                    else:
                        if number_po_gen21 != line.header_attribute1:
                            raise ValidationError(_("Failed deferent po numbers : " + line.item_segment1))
                    check_loop += 1

        for record in self:
            if len(record.line_ids) > 0:
                for line in record.line_ids:
                    if not line.item_segment1:
                        raise MissingError(_("Item segment not null. No Bundle: " + record.name))
                    if len(data_posted) > 0:
                        for data in data_posted:
                            property_account_expense_id = False
                            uom_id = False
                            filter_product = [
                                ('default_code', '=', line['item_segment1']),
                                ('active', '=', True),
                            ]
                            product_id = self.env['product.product'].search(filter_product)
                            if not product_id:
                                raise MissingError(_("Product does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                if product_id.property_account_expense_id:
                                    property_account_expense_id = product_id.property_account_expense_id.id
                                else:
                                    raise MissingError(_("Set account expense in product. No Item Segment: " + line.item_segment1))
                                if product_id.uom_id:
                                    uom_id = product_id.uom_id.id
                                else:
                                    raise MissingError(_("Set uom in product. No Item Segment: " + line.item_segment1))
                                product_id = product_id[0].id

                            filter_company = [
                                ('org_id', '=', line['org_id']),
                            ]
                            company_id = self.env['res.company'].search(filter_company)
                            if not company_id:
                                raise MissingError(_("Company does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                company_id = company_id[0].id
                            
                            filter_buyer = [
                                ('code', '=', str(line['suggested_buyer_id'])),
                            ]
                            buyer_id = self.env['res.buyer'].search(filter_buyer)
                            if not buyer_id:
                                raise MissingError(_("Buyer does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                buyer_id = buyer_id[0].id

                            filter_analytic = [
                                ('code', '=', '000'),
                                ('company_id', '=', company_id)
                            ]
                            analytic_id = self.env['account.analytic.account'].search(filter_analytic)
                            if not analytic_id:
                                raise MissingError(_("Analytic account does not exist or not active. No Item Segment: " + line.item_segment1))
                            else:
                                analytic_id = analytic_id[0].id

                            name_line = ''
                            if line.header_attribute1:
                                name_line = name_line + line.header_attribute1
                            if line.header_attribute4:
                                name_line = name_line + '-' + line.header_attribute4
                            if line.header_attribute5:
                                name_line = name_line + '-' + line.header_attribute5
                            values_line = (0, 0, {
                                "product_id": product_id,
                                "account_id": property_account_expense_id,
                                "product_uom_id": uom_id,
                                "name": name_line,
                                "uniqkey_gen21": line['uniqkey'],
                                "buyer_id": buyer_id,
                                "analytic_account_id": analytic_id,
                                "product_qty": line['quantity'],
                                "original_price": line['currency_unit_price'] if line['currency_code'] != 'IDR' else line['unit_price'],
                                'select_currency_id': self._get_currency_name(line['currency_code']),
                                'manual_currency_rate': line['currency_rate_price'],
                                'manual_currency_rate_active': True if line['currency_rate_price'] else False,
                                "header_attribute4": line['header_attribute4']
                            })
                            data['line_ids'].append(values_line)
                    if new_journal:
                        filter_request = [
                            ('partner_id.id_users', '=', line['preparer_id']),
                            ('active', '=', True),
                        ]
                        request = self.env['res.users'].search(filter_request)
                        if not request:
                            raise MissingError(_("Request by does not exist or not active. No Item Segment: " + line.item_segment1))

                        hierarchy_id = False
                        approval_hierarchy = self.env['approval.hierarchy.line'].search([])
                        if approval_hierarchy:
                            for approval in approval_hierarchy:
                                if len(approval.employee_ids) > 0:
                                    for employee in approval.employee_ids:
                                        if employee.user_id:
                                            if employee.user_id.id == request.id:
                                                hierarchy_id = approval.hierarchy_id.id
                                                break
                        if not hierarchy_id:
                            raise MissingError(_("Check hierarchy . No Item Segment: " + line.item_segment1))

                        property_account_expense_id = False
                        uom_id = False
                        filter_product = [
                            ('default_code', '=', line['item_segment1']),
                            ('active', '=', True),
                        ]
                        product_id = self.env['product.product'].search(filter_product)
                        if not product_id:
                            raise MissingError(_("Product does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            if product_id.property_account_expense_id:
                                property_account_expense_id = product_id.property_account_expense_id.id
                            else:
                                raise MissingError(_("Set account expense in product. No Item Segment: " + line.item_segment1))
                            if product_id.uom_id:
                                uom_id = product_id.uom_id.id
                            else:
                                raise MissingError(_("Set uom in product. No Item Segment: " + line.item_segment1))
                            product_id = product_id[0].id

                        filter_company = [
                            ('org_id', '=', line['org_id']),
                        ]
                        company_id = self.env['res.company'].search(filter_company)
                        if not company_id:
                            raise MissingError(_("Company does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            company_id = company_id[0].id
                        
                        filter_buyer = [
                            ('code', '=', str(line['suggested_buyer_id'])),
                        ]
                        buyer_id = self.env['res.buyer'].search(filter_buyer)
                        if not buyer_id:
                            raise MissingError(_("Buyer does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            buyer_id = buyer_id[0].id

                        filter_analytic = [
                            ('code', '=', '000'),
                            ('company_id', '=', company_id)
                        ]
                        analytic_id = self.env['account.analytic.account'].search(filter_analytic)
                        if not analytic_id:
                            raise MissingError(_("Analytic account does not exist or not active. No Item Segment: " + line.item_segment1))
                        else:
                            analytic_id = analytic_id[0].id
                        nomer_seq = self.env["ir.sequence"].next_by_code("purchase.request")
                        if not nomer_seq:
                            raise MissingError(_("Sequence does not exist or not active. No Item Segment: " + line.item_segment1))

                        if line['uniqkey'] and line['uniqkey'] != "":
                            filter_purchase_request_line = [
                                ('uniqkey_gen21', '=', line['uniqkey']),
                                ('request_id.state', 'not in', ('rejected', 'returned', 'cancel')),
                                ('request_state', 'not in', ('rejected', 'returned', 'cancel'))
                            ]
                            purchase_request_line = self.env["purchase.request.line"].search(filter_purchase_request_line)
                            if purchase_request_line:
                                raise MissingError(_("Cant duplicated PR No " + purchase_request_line[0].request_id.name + " Number Line: " + str(purchase_request_line[0].line_number) + ". No Item Segment: " + line.item_segment1))
                        origin = ''
                        for orig in self:
                            if orig.name:
                                origin = orig.name + ',' + origin

                        name_line = ''
                        if line['header_attribute1']:
                            name_line = name_line + line['header_attribute1']
                        if line['header_attribute3']:
                            name_line = name_line + '-' + line['header_attribute3']
                        if line['header_attribute4']:
                            name_line = name_line + '-' + line['header_attribute4']
                        values = {
                            "name": nomer_seq,
                            "origin": origin,
                            "requested_by": request.id,
                            "hierarchy_id": hierarchy_id,
                            "description": name_line,
                            "company_id": company_id,
                            'po_numbers_gen21': number_po_gen21,
                            "line_ids": [
                                (0, 0, {
                                    "product_id": product_id,
                                    "account_id": property_account_expense_id,
                                    "product_uom_id": uom_id,
                                    "name": name_line,
                                    "uniqkey_gen21": line['uniqkey'],
                                    "buyer_id": buyer_id,
                                    "analytic_account_id": analytic_id,
                                    "product_qty": line['quantity'],
                                    "original_price": line['currency_unit_price'] if line['currency_code'] != 'IDR' else line['unit_price'],
                                    'select_currency_id': self._get_currency_name(line['currency_code']),
                                    'manual_currency_rate': line['currency_rate_price'],
                                    'manual_currency_rate_active': True if line['currency_rate_price'] else False,
                                    "header_attribute4": line['header_attribute4']
                                })
                            ],
                            "state": "draft",
                            "is_post_gen21": True,
                        }
                        data_posted.append(values)
                        new_journal = False
        if len(data_posted) > 0:
            # TODO check here, there could be a possibility to merge n-records
            purchase_request = self.env['purchase.request'].create(data_posted)
            if purchase_request:
                for record in self:
                    record.write({'state': 'posted'})
            else:
                raise ValidationError(_("Failed null data Program Costs"))
        else:
            raise ValidationError(_("Failed null data Program Costs"))
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def button_change_cancel(self):
        for line in self.line_ids:
            request_line = self.env['purchase.request.line'].search([('uniqkey_gen21', '=', line.uniqkey)])
            if request_line:
                if len(request_line) > 1:
                    for r_line in request_line:
                        if r_line.request_id.state not in ('draft', 'to_approve'):
                            raise ValidationError(_("Failed cancel PR not in (draft, to_approve), No PR :" + r_line.request_id.name))
                else:
                    if request_line.request_id.state not in ('draft', 'to_approve'):
                        raise ValidationError(_("Failed cancel PR not in (draft, to_approve), No PR :" + request_line.request_id.name))
        self.write({'state': 'cancel', 'is_change': True})
        return True

    def button_change_post(self):
        for line in self.line_ids:
            request_line = self.env['purchase.request.line'].search([('uniqkey_gen21', '=', line.uniqkey)])
            if request_line:
                if request_line.request_id.state in ('draft', 'to_approve'):
                    request_line.write({'original_price': line.unit_price})
                else:
                    raise ValidationError(_("Failed post to PR"))
        self.write({'state': 'posted', 'is_change': False})
        return True

    def action_add_to_pr_show(self):
        """ function to open wizard to select Program Cost record """
        return {
            'name': 'Add to PR',
            'res_model': 'wizard.add.to.pr',
            'view_mode': 'form',
            'view_id': self.env.ref('ins_base_api.view_wizard_add_to_pr_form').id,
            'context': {
                'active_model': 'program.costs.gen21',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
