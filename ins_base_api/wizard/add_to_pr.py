from odoo import api, fields, models
from odoo.exceptions import MissingError, ValidationError


class WizardAddToPR(models.TransientModel):
    _name = 'wizard.add.to.pr'
    _description = 'Add to PR'

    cost_ids = fields.Many2many('program.costs.gen21', string='Selected Costs')
    request_id = fields.Many2one('purchase.request', 'Purchase Request')

    @api.model
    def default_get(self, fields_list):
        """ inherit function to add default value """
        res = super().default_get(fields_list)
        ctx = self._context
        active_ids = ctx.get('active_ids', [])
        if active_ids:
            res['cost_ids'] = [(6, 0, active_ids)]
        return res

    def _check_record(self):
        """ helper function to check record before processing """
        states = set(self.cost_ids.mapped('state'))
        only_waiting = len(states) == 1 and 'wait' in states
        draft_request = self.request_id.state == 'draft'
        if not only_waiting or not draft_request:
            msg = 'Could only process waiting records and Purchase Request must be draft'
            raise ValidationError(msg)

    def _process_data(self):
        """ helper function to help process data before adding to triplet """
        data = []
        # loop every cost_ids, find product and respective fields then construct
        for cost in self.cost_ids:
            for line in cost.line_ids:
                segment = line.item_segment1
                product = self.env['product.product'].search([
                    ('default_code', '=', segment),
                    ('active', '=', True),
                ])
                if not product:
                    raise MissingError('Product does not exist/active. Item Segment: %s' % segment)

                if not product.uom_id:
                    raise MissingError('No UoM found in product. Item Segment: %s' % segment)

                buyer = self.env['res.buyer'].search([
                    ('code', '=ilike', line.suggested_buyer_id),
                ])
                if not buyer:
                    raise MissingError('No Buyer found. Item Segment: %s' % segment)

                company = self.env['res.company'].search([
                    ('org_id', '=', line.org_id),
                ])
                if not company:
                    raise MissingError('Company does not exist. Item Segment: %s' % segment)

                analytic = self.env['account.analytic.account'].search([
                    ('code', '=', '000'),
                    ('company_id', '=', company[0].id),
                ])
                if not analytic:
                    raise MissingError('Analytic does not exist. Item Segment: %s' % segment)

                currency = self.env['res.currency'].search([('name', '=', line.currency_code)])

                account_id = product.property_account_expense_id.id if product.property_account_expense_id else False
                uom_id = product.uom_id.id if product.uom_id else False

                name = ''
                if line.header_attribute1:
                    name += line.header_attribute1
                if line.header_attribute4:
                    name += ' - %s' % line.header_attribute4
                if line.header_attribute3:
                    name += ' - %s' % line.header_attribute3

                vals = {
                    'product_id': product[0].id,  # take first
                    'account_id': account_id,
                    'product_uom_id': uom_id,
                    'name': name,
                    'uniqkey_gen21': line.uniqkey,
                    'buyer_id': buyer[0].id,
                    'analytic_account_id': analytic[0].id,
                    'product_qty': line.quantity,
                    'original_price': line.unit_price,
                    'select_currency_id': currency.id if currency else False,
                    'manual_currency_rate': line.currency_rate_price,
                    'manual_currency_rate_active': True if line.currency_rate_price else False,
                    'header_attribute4': line.header_attribute4,
                }
                data.append(vals)
        return data

    def button_add(self):
        """ function to add to PR """
        self.ensure_one()

        # check record validity
        self._check_record()

        # valid, proceed. Get the request_id
        # use 0 triplet to add to its line_ids, then set cost_ids state to posted
        data = self._process_data()
        if data:
            request = self.request_id
            request.write({'line_ids': [(0, 0, x) for x in data]})
            self.cost_ids.write({'state': 'posted'})
        return True
