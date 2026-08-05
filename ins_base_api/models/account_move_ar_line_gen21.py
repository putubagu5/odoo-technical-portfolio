from odoo import models, tools, fields, api, _


class AccountMoveArLineGen21(models.Model):
    _name = "account.move.ar.line.gen21"

    move_id_ar_gen21 = fields.Many2one('account.move.ar.gen21', string='Journal Entry Gen21',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="The move of this entry line.")
    org_id = fields.Char(string='ID Org Unit')
    cust_type = fields.Char(string='Customer/Agency Tipe')
    adv_source = fields.Char(string='Customer/Agency source')
    channel = fields.Char(string='Kode Channel')
    channel_name = fields.Char(string='Nama Channel')
    region = fields.Char(string='Kode Region')
    region_name = fields.Char(string='Nama Region')
    agen_code = fields.Char(string='Kode Agency')
    agen_name = fields.Char(string='Nama Agency')
    client_code = fields.Char(string='Kode Client')
    client_name = fields.Char(string='Name Client')
    invoice_no = fields.Char(string='Nomor Invoice')
    invoice_date = fields.Date(string='Tanggal Invoice')
    invoice_date_formatted = fields.Date(string='Tanggal Invoice Formatted')
    inv_yy = fields.Char(string='Tahun Invoice (2 digit)')
    po_no = fields.Char(string='Nomor PO')
    mo_no = fields.Char(string='Nomor Register/Media Order')
    po_type = fields.Char(string='Kode Tipe PO')
    ae_name = fields.Char(string='Nama Sales')
    prod_name = fields.Char(string='Nama Produk')
    pab_pbb = fields.Char(string='Tipe Bayar')
    generation_date = fields.Datetime(string='Tanggal Generate Invoice')
    rowid_inv = fields.Char(string='ID Row Invoice')
    total_spots = fields.Integer(string='Jumlah Spot iklan')
    total_gross = fields.Float(string='Nilai Kotor')
    agency_disc = fields.Integer(string='Agency diskon')
    agency_comm = fields.Float(string='Agency Komisi')
    total_net = fields.Float(string='Nilai Bersih')
    total_net_formatted = fields.Char(string="Nilai Bersih Formatted")
    perc_tax = fields.Integer(string='Nilai Persentase Pajak')
    total_tax = fields.Float(string='Nilai Pajak')
    update_user = fields.Char(string='Diupdate oleh')
    update_date = fields.Datetime(string='Tanggal Update')
    attribute1 = fields.Char(string='Status Transfer ke Oracle')
    cust_ref = fields.Char(string='Customer Reference')
    site = fields.Char(string='Kode Site')
    send_flag = fields.Char(string='Tanda Kirim ke staging')
    senddate = fields.Date(string='Tanggal kirim ke staging')
    ccid = fields.Char(string='ID CC')
    gl_date = fields.Date(string='Tanggal GL')
    region_line_code = fields.Char(string='Kode Line Region')
    region_line_name = fields.Char(string='Nama Line Region')
    period = fields.Char(string='Periode')
    company_code = fields.Char(string='Kode Perusahaan')
    wilayah = fields.Char(string='Wilayah')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('wait', 'Waiting To Posted'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='wait')
    company_id = fields.Many2one('res.company', string='Company', related="move_id_ar_gen21.company_id")
    line_number = fields.Integer(string='Line Number')
    selected = fields.Boolean('Selected', default=False)

    def button_cancel(self):
        self.move_id_ar_gen21._check_all_posted_line()
        self.write({'state': 'cancel'})
        return True
