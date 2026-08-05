from odoo import models, tools, fields, api, _


class ProgramCostsLineGen21(models.Model):
    _name = "program.costs.line.gen21"

    program_costs_id_gen21 = fields.Many2one(
        'program.costs.gen21', string='Journal Entry Gen21',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="The move of this entry line.")
    transaction_id = fields.Integer("Transaction ID")
    interface_source_code = fields.Char("Interface Source Code")
    source_type_code = fields.Char("Source Type Code")
    requisition_type = fields.Char("Requisition Type")
    destination_type_code = fields.Char("Destination Type Code")
    quantity = fields.Integer("Quantity")
    uom_code = fields.Char("Uom Code")
    unit_price = fields.Char("Price per unit")
    unit_price_decimal = fields.Float("Price per unit", compute="_compute_unit_price_decimal")
    currency_unit_price = fields.Float("Currency Unit Price")
    currency_rate_price = fields.Float("Currency Rate Price")
    authorization_status = fields.Char("Authorization Status")
    group_code = fields.Char("Group Code")
    header_attribute_category = fields.Char("Header Attribute Category")
    header_attribute1 = fields.Char("PO/Contract Number")
    header_attribute2 = fields.Char("Approval Hierarchy")
    header_attribute3 = fields.Char("Name Program")
    header_attribute4 = fields.Char("Episode No")
    header_attribute5 = fields.Char("Name Title Episode")
    header_attribute6 = fields.Char("Episode Updated By")
    header_attribute10 = fields.Char("Episode Updated By")
    deliver_to_location_id = fields.Char("ID Lokasi")
    item_segment1 = fields.Char("Nomor PR Oracle/Odoo")
    item_description = fields.Char("Nama Title Episode")
    destination_organization_code = fields.Char("Kode Destinasi Org")
    destination_subinventory = fields.Char("Destination Sub Inventory")
    need_by_date = fields.Date("PO/Contract Tanggal")
    gl_date = fields.Datetime("Tanggal Kirim Dari Interface")
    org_id = fields.Integer("ID Org")
    deliver_to_requestor_id = fields.Integer("ID Delivery Requestor")
    preparer_id = fields.Integer("ID Preparer")
    suggested_buyer_id = fields.Integer("ID Buyer")
    suggested_vendor_id = fields.Integer("ID Vendor")
    suggested_vendor_name = fields.Char("Nama Distributor")
    charge_account_id = fields.Integer("ID Charge Account")
    variance_account_id = fields.Integer("ID Charge Account")
    budget_account_id = fields.Integer("ID Charge Account")
    currency_code = fields.Char("EpIsode Currency")
    rate = fields.Integer("Episode Rate Value")
    rate_type = fields.Char("Tipe Rate")
    charge_account_segment1 = fields.Char("COA_SEGMENT1")
    charge_account_segment2 = fields.Char("COA_SEGMENT2")
    charge_account_segment3 = fields.Char("COA_SEGMENT3")
    charge_account_segment4 = fields.Char("COA_SEGMENT4")
    charge_account_segment5 = fields.Char("COA_SEGMENT5")
    charge_account_segment6 = fields.Char("COA_SEGMENT6")
    last_update_date = fields.Date("Tanggal terakhir Modifikasi Episode")
    last_updated_by = fields.Integer("Nama terakhir Modifikasi Episode")
    rate_date = fields.Date("PO/Contract Tanggal")
    line_attribute15 = fields.Char("PO/Contract Number")
    uniqkey = fields.Char('Uniq Key')
    line_attribute_category = fields.Char("Line Attribute Category")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('wait', 'Waiting To Posted'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft', related="program_costs_id_gen21.state")
    line_number = fields.Integer(string='Line Number')

    def _compute_unit_price_decimal(self):
        for record in self:
            record.unit_price_decimal = float(record.unit_price)
