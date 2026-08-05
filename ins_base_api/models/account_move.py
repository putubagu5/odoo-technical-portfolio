from odoo import api, fields, models, _
from num2words import num2words
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.context_today(self))
    source_type_gen21 = fields.Selection(string="Source", selection=[("iklan_bms", "Iklan BMS"), ("manual", "Invoice Manual")])
    category_gen21 = fields.Char(string="Category")
    advertiser_gen21 = fields.Char(string="Advertiser")
    customer_type_gen21 = fields.Char(string="Customer Type")
    ref_person_gen21 = fields.Char(string="Attention / Contact Person")
    attention_contact_gen21 = fields.Char(string="Attention / Contact Person")
    invoice_no_gen21 = fields.Char(String="Invoice No")
    product_gen21 = fields.Char(string="Product")
    mo_numbers_gen21 = fields.Char(string="Contract/MO No")
    po_numbers_gen21 = fields.Char(string="PO Numbers Gen21")
    pab_pbb_gen21 = fields.Char(string="PAB/PBB")
    po_type_gen21 = fields.Char(sttring="Kode Tipe PO")
    status_transfer_oracle_gen21 = fields.Char(string="Status Transfer Ke Oracle")
    customer_ref_gen21 = fields.Char(string="Customer Ref")
    code_site_gen21 = fields.Char(string="Kode Site")
    send_flag_gen21 = fields.Char(string="Tanda Kirim Ke Stagging")
    send_date_gen21 = fields.Date(string="Tanggal Kirim Ke Stagging")
    ccid_gen21 = fields.Char(String="ID CC")
    code_region_gen21 = fields.Char(String="Kode Region")
    name_region_gen21 = fields.Char(String="Name Region")
    code_region_line_gen21 = fields.Char(String="Kode Line Region")
    name_region_line_gen21 = fields.Char(String="Name Line Region")
    periode_gen21 = fields.Char(String="Periode")
    code_company_gen21 = fields.Char(String="Code Company")
    wilayah_gen21 = fields.Char(String="Wilayah")
    sales_person_gen21 = fields.Char(String="Sales Person")
    channel_code_gen21 = fields.Char(string="Channel Code")
    channel_name_gen21 = fields.Char(string="Channel Name")
    perc_tax_gen21 = fields.Char(string="Perc tax")
    total_tax_gen21 = fields.Char(string="Total tax")
    cm_gen21 = fields.Char(string="CM / GEN")

    actual_flag_gl_gen21 = fields.Char(string="Actual Flag")
    attribute1_gl_gen21 = fields.Char(string="PO/Contract Number")
    attribute2_gl_gen21 = fields.Char(string="Row ID Episode")
    attribute3_gl_gen21 = fields.Char(string="Episode No")
    attribute4_gl_gen21 = fields.Char(string="Episode Title")
    attribute6_gl_gen21 = fields.Char(string="Episode Name")
    attribute7_gl_gen21 = fields.Char(string="Attribute7")
    attribute8_gl_gen21 = fields.Char(string="Nama Program")
    attribute9_gl_gen21 = fields.Char(string="Attribute9")
    created_by_gl_gen21 = fields.Char(string="Created By")
    material_id_gl_gen21 = fields.Char(string="Material ID")
    group_id_gl_gen21 = fields.Char(string="Group ID")
    reference1_gl_gen21 = fields.Char(string="Journal Name")
    reference4_gl_gen21 = fields.Char(string="Nama Program")
    segment5_gl_gen21 = fields.Char(string="COA SEGMENT5")
    segment6_gl_gen21 = fields.Char(string="COA_SEGMENT6")
    send_date_gl_gen21 = fields.Date(string="Tanggal kirim dari Interface")
    send_flag_gl_gen21 = fields.Char(string="Status Flag")
    update_date_gl_gen21 = fields.Date(string="Update Date")
    update_user_gl_gen21 = fields.Char(string="Nama User Modifikasi")
    usage_number_gl_gen21 = fields.Integer(string="Seq Usage")
    usage_run_id_gl_gen21 = fields.Integer(string="Sequence")

    po_numbers_bill_gen21 = fields.Char(string="PO Numbers Gen21", compute='_compute_po_numbers_bill_gen21', store=True)

    is_post_gen21 = fields.Boolean(string="Is Post Gen21", default=False)
    amount_in_words_gen21 = fields.Char('Amount To Words Gen21', compute='amount_to_text_gen21')

    @api.depends('amount_total', 'currency_id')
    def amount_to_text_gen21(self):
        for rec in self:
            # lang = 'id' if self.currency_id.name == 'IDR' else 'en'
            lang = 'id' if rec.currency_id.name == 'IDR' else 'en'
            currency_in_words = rec.currency_id.currency_unit_label
            # convert to integer to remove decimal place
            words_amount = num2words(int(rec.amount_total), lang=lang)
            rec.amount_in_words_gen21 = words_amount.title() + " " + currency_in_words

    def get_tax_info(self):
        """ function to return tax info in list of tuple """
        taxes = []
        # from line_ids, find records with tax_line_id and take the credit/debit
        lines = self.line_ids.filtered(lambda x: x.tax_line_id)

        # map by tax_line_id
        taxes_map = lines.mapped('tax_line_id')

        # then create a dict based on grouped tax
        taxes_dict = {x.id: [x.name, 0] for x in taxes_map}
        for x in lines:  # loop the lines then map to taxes_dict
            tmp = taxes_dict.get(x.tax_line_id.id)
            if tmp:
                # tmp[1] += (x.credit or x.debit)  # add if any
                tmp[1] += x.amount_currency  # add the amount_currency
        taxes = taxes_dict.values()  # then use the values (list)
        # taxes = [(x.tax_line_id.name, (x.credit or x.debit)) for x in lines]
        return taxes

    def get_partner_remit(self):
        partner_remit = self.env['res.partner.remit'].search([('company_id', '=', self.company_id.id), ('partner_ids', 'in', self.partner_id.id)])
        list_remit = []
        if partner_remit:
            for remit in partner_remit:
                if remit.bank_ids:
                    for bank in remit.bank_ids:
                        if bank.currency_id.id == self.currency_id.id:
                            txt_remit = '- ' + bank.bank_name + ', A/C ' + self.currency_id.name + ' ' + bank.acc_number
                            list_remit.append(txt_remit)
        return list_remit

    @api.depends('invoice_line_ids')
    def _compute_po_numbers_bill_gen21(self):
        for record in self:
            po_number_list = []
            for line in record.invoice_line_ids:
                if line.purchase_order_id:
                    if line.purchase_order_id.po_numbers_gen21:
                        po_number_list.append(line.purchase_order_id.po_numbers_gen21)

                po_number_list = list(set(po_number_list))
                po_number_list.sort()
                po_numbers = ', '.join(po_number_list)
                record.po_numbers_bill_gen21 = po_numbers

    def _get_due_payment_term(self):
        add_days = self.invoice_payment_term_id.line_ids[0].days
        date_due = self.invoice_date + datetime.timedelta(days=add_days)
        date_due = date_due.strftime('%d-%b-%Y')
        return date_due

    def _get_job_position(self, job_position):
        if job_position:
            if "&" in job_position:
                job_position = job_position.replace("&", "And")
        return job_position
