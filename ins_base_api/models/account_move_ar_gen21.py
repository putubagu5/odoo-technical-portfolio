from odoo import models, tools, fields, api, _
from odoo.exceptions import MissingError, ValidationError


class AccountMoveArGen21(models.Model):
    _name = "account.move.ar.gen21"

    name = fields.Char('Name')
    line_ids = fields.One2many('account.move.ar.line.gen21', 'move_id_ar_gen21', string='Invoice Line Ar')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('wait', 'Waiting To Posted'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='wait')
    company_id = fields.Many2one('res.company', string='Company')
    total_amount_net = fields.Float("Total Amount Net", compute="_compute_total_amount")
    is_selected_all = fields.Boolean('Select All Lines', default=False)

    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('line_ids', []):
            lines = vals.get('line_ids', [])
            for idx, line in enumerate(lines):
                line[2].update({'line_number': idx + 1})
        res = super(AccountMoveArGen21, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(AccountMoveArGen21, self).write(vals)
        for idx, line in enumerate(self.line_ids):
            line.line_number = idx + 1
        return res

    def _compute_total_amount(self):
        for record in self:
            if len(record.line_ids) > 0:
                record.total_amount_net = sum([line.total_net for line in record.line_ids])
            else:
                record.total_amount_net = 0

    def button_select_all_lines(self):
        """ function to select all lines in copy budget """
        for rec in self:
            rec.is_selected_all = True
            for line in rec.line_ids:
                if line.state not in ['cancel', 'posted']:
                    line.selected = True
        return True

    def button_unselect_all_lines(self):
        """ function to unselect all lines in copy budget """
        for rec in self:
            rec.is_selected_all = False
            for line in rec.line_ids:
                if line.state not in ['cancel', 'posted']:
                    line.selected = False
        return True

    def _get_partner_api(self, sites_customer, line_site):
        data = False
        for customer in sites_customer:
            if len(customer.site_ids):
                for site in customer.site_ids:
                    if site.code == line_site:
                        return customer
        return data
    
    def _check_all_posted_line(self):
        check = True
        for line in self.line_ids:
            if line.state in ['draft', 'wait']:
                check = False
        if check:
            self.write({'state': 'posted'})

    def button_post(self):
        data_posted = []
        if len(self.line_ids) > 0:
            for line in self.line_ids.filtered(lambda x: x.selected and x.state == 'wait'):
                filter_move = [
                    ('name', '=', line.invoice_no),
                    ('state', 'in', ('draft', 'posted'))
                ]
                check_move = self.env['account.move'].search(filter_move)
                if check_move:
                    raise ValidationError(_("Invoice AR is already created. No Invoice: " + line.invoice_no))

                # customer = False
                # filter_customer = [
                #     ('partner_type_id', 'in', ['THIRD PARTY', 'RELATED PARTIES']),
                #     ('active', '=', True),
                #     ('customer_rank', '>', 0)
                # ]
                # sites_customer = self.env['res.partner'].search(filter_customer)
                # if not sites_customer:
                #     raise MissingError(_("Customer does not exist or not active. No Invoice: " + line.invoice_no))
                # else:
                #     customer = self._get_partner_api(sites_customer, line.site)
                #     if not customer:
                #         raise MissingError(_("Customer code sites does not exist or not active. No Invoice: " + line.invoice_no))
                
                sites = False
                customer = False
                if line.site:
                    filter_sites = [
                        ('code', '=', line.site),
                    ]
                    data_sites = self.env['res.sites'].search(filter_sites)
                    if data_sites:
                        sites = data_sites.id
                        if data_sites.partner_id:
                            customer = data_sites.partner_id
                        else:
                            raise MissingError(_("Customer does not exist or not active. No Invoice: " + line.invoice_no))
                    else:
                        raise MissingError(_("Customer code sites does not exist or not active. No Invoice: " + line.invoice_no))
                
                filter_company = [
                    ('org_id', '=', line.org_id),
                ]
                company = self.env['res.company'].search(filter_company)
                if not company:
                    raise MissingError(_("Company org does not exist or has been deleted. No Invoice: " + line.invoice_no))

                tax_ids = [] 
                account_taxes = self.env['account.tax'].search([('amount', '=', line.perc_tax), ('type_tax_use', '=', 'sale'), ('company_id', '=', company.id), ('active', '=', True)])
                if len(account_taxes) > 0:
                    if len(account_taxes) > 1:
                        for taxes in account_taxes:
                            tax_ids.append((4, taxes.id))
                    else:
                        tax_ids.append((4, account_taxes.id))

                filter_payment_term = [
                    ('is_default_gen21', '=', True),
                ]
                account_payment_term = self.env['account.payment.term'].search(filter_payment_term)
                if not account_payment_term:
                    raise MissingError(_("Set default account payment term. No Invoice: " + line.invoice_no))

                if len(account_payment_term) > 1:
                    account_payment_term = account_payment_term[0]

                transaction_type = False
                if customer.property_account_receivable_id:
                    if customer.partner_type_id.name == 'THIRD PARTY':
                        filter_transaction = [
                           ('name', '=', 'GEN21-Pihak Ke3'),
                           ('company_id', '=', company.id) 
                        ]
                        transaction_type = self.env['account.transaction.type'].search(filter_transaction)
                        if not transaction_type:
                            raise MissingError(_("Transaction type does not exist or has been deleted. No Invoice: " + line.invoice_no))
                    elif customer.partner_type_id.name == 'RELATED PARTIES':
                        filter_transaction = [
                           ('name', '=', 'GEN21-Pihak Berelasi'),
                           ('company_id', '=', company.id)
                        ]
                        transaction_type = self.env['account.transaction.type'].search(filter_transaction)
                        if not transaction_type:
                            raise MissingError(_("Transaction type does not exist or has been deleted. No Invoice: " + line.invoice_no))
                    else:
                        raise MissingError(_("Please set customer type. No Invoice: " + line.invoice_no))
                else:
                    raise MissingError(_("Please set account receivable customer. No Invoice: " + line.invoice_no))

                filter_account = [
                    ('company_id.id', '=', company.id),
                    ('code', '=', '4110101'),
                ]
                account_account = self.env['account.account'].search(filter_account)
                if not account_account:
                    raise MissingError(_("Please Set account 4110101-Pendapatan Iklan - Agency. No Invoice: " + line.invoice_no))
                vals = {
                    "move_type": "out_invoice",
                    "sites_id":  sites,
                    "company_id": company.id,
                    "name":line.invoice_no,
                    "partner_id":customer.id,
                    "ar_receipt_type":"iklan",
                    "source_type_gen21":"iklan_bms",
                    "invoice_payment_term_id": account_payment_term.id,
                    "po_numbers":line.po_no,
                    "ref":"iklan",
                    "period_id":False,
                    "payment_reference": line.invoice_no,
                    "invoice_date":line.invoice_date,
                    "invoice_date_due":line.invoice_date,
                    "category_gen21": "",
                    "advertiser_gen21": line.client_name,
                    "customer_type_gen21": line.cust_type,
                    "ref_person_gen21": line.cust_ref,
                    "attention_contact_gen21": False,
                    "invoice_no_gen21": line.invoice_no,
                    "product_gen21": line.prod_name,
                    "mo_numbers_gen21": line.mo_no,
                    "po_numbers_gen21": line.po_no,
                    "pab_pbb_gen21": line.pab_pbb,
                    "po_type_gen21": line.po_type,
                    "status_transfer_oracle_gen21": line.attribute1,
                    "customer_ref_gen21": line.cust_ref,
                    "code_site_gen21": line.site,
                    "send_flag_gen21": line.send_flag,
                    "send_date_gen21": line.senddate,
                    "ccid_gen21": line.ccid,
                    "code_region_gen21": line.region,
                    "name_region_gen21": line.region_name,
                    "code_region_line_gen21": line.region_line_code,
                    "name_region_line_gen21": line.region_line_name,
                    "periode_gen21": line.ccid,
                    "code_company_gen21": line.company_code,
                    "wilayah_gen21": line.wilayah,
                    "channel_code_gen21": line.channel,
                    "channel_name_gen21": line.channel_name,
                    "perc_tax_gen21": line.perc_tax,
                    "total_tax_gen21": line.total_tax,
                    "sales_person_gen21": line.ae_name,
                    "cm_gen21": "",
                    "transaction_type_id": transaction_type.id,
                    "is_post_gen21": True,
                    "operating_unit_id": False,
                    "invoice_line_ids":
                    [{
                        "name": line.prod_name,
                        "account_id": account_account.id,
                        "total_spots_gen21": line.total_spots,
                        "total_gross_gen21": line.total_gross,
                        "agency_discount_gen21": line.agency_comm,
                        "quantity": 1,
                        "price_unit": line.total_net,
                        "discount": 0,
                        "partner_id": customer.id,
                        "tax_ids": tax_ids
                    }]
                }
                data_posted.append(vals)
        if len(data_posted) > 0:
            account_move = self.env['account.move'].create(data_posted)
            if account_move:
                for line in self.line_ids.filtered(lambda x: x.selected and x.state == 'wait'):
                    line.write({'state': 'posted'})
                self._check_all_posted_line()
            else:
                raise ValidationError(_("Failed post data invoice ar"))
        else:
            raise ValidationError(_("Failed null data invoice ar"))
        return True

    def button_cancel(self):
        for line in self.line_ids:
            if line.state == 'draft':
                line.write({'state': 'cancel'})
            if line.state == 'wait':
                line.write({'state': 'cancel'})
        self._check_all_posted_line()
        return True
