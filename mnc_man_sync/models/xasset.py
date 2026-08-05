from odoo import api, fields, models, _, tools
from datetime import date, datetime
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class XAsset(models.Model):
    _name = 'x.asset'
    _description = 'xasset - Odoo Staging Table - prepared for ATIS - Oracle Staging'

    # asset_id = fields.Char(string="Asset")
    #
    # company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
    #                              default=lambda self: self.env.company)
    book_type_code = fields.Char(string="Book Type")
    asset_number = fields.Char(string="Asset Number")
    unit_qty = fields.Float(string="Unit Qty")
    asset_description = fields.Text(string="Asset Description")
    major_category = fields.Char(string="Major Category")
    minor_category = fields.Char(string="Minor Category")
    date_in_service = fields.Char(string="Date in Service")
    prorate_convention = fields.Char(string="Prorate Convention")
    prorate_date = fields.Char(string="Prorate Date")
    life_in_months = fields.Integer(string="Life in Months")
    life_year = fields.Integer(string="Life Year")
    remaining_life_year = fields.Char(string="Remaining life Year")
    remaining_life_months = fields.Char(string="Remaining life Months")
    fixed_asset_cost = fields.Float(string="Fixed asset Cost")
    accumulated_depreciation_cost = fields.Float(string="Accumulated Depreciation Cost")
    net_book_value = fields.Char(string="Net Book Value")
    child_barcode = fields.Char(string="Child Barcode")
    component_barcode = fields.Char(string="Component Barcode")
    component_barcode_label = fields.Char(string="Component Barcode Label")
    serial_number = fields.Char(string="Serial Number")
    tag_number = fields.Char(string="Tag Number")
    goods_brand = fields.Char(string="Goods Brand")
    brand_model = fields.Char(string="Brand Model")
    specification = fields.Char(string="Specification")
    condition = fields.Char(string="Condition")
    remarks = fields.Char(string="Remarks")
    payment_voucher = fields.Char(string="Payment Voucher")
    invoice_number = fields.Char(string="Invoice Number")
    invoice_line_number = fields.Char(string="Invoice Line Number")
    item_code = fields.Char(string="Item Code")
    item_name = fields.Char(string="Item Name")
    item_description = fields.Char(string="Item Description")
    po_number = fields.Char(string="Po Number")
    po_date = fields.Char(string="Po Date")
    po_vendor_name = fields.Char(string="Po Vendor Name")
    po_line_number = fields.Char(string="Po Line Number")
    po_qty = fields.Float(string="Po Qty")
    po_uom = fields.Char(string="Po Uom")
    po_uom_description = fields.Char(string="Po Uom Description")
    pr_number = fields.Char(string="Pr Number")
    pr_date = fields.Char(string="Pr Date")
    pr_line_number = fields.Char(string="Pr Line Number")
    pr_qty = fields.Float(string="Pr Qty")
    pr_uom = fields.Char(string="Pr Uom")
    pr_uom_description = fields.Char(string="Pr Uom Description")
    atis_doc_number = fields.Char(string="Atis Doc Number")
    atis_doc_date = fields.Char(string="Atis Doc Date")
    department_owner = fields.Char(string="Department Owner")
    atis_line_number = fields.Char(string="Atis Line Number")

    # asset_date_placed_in_service = fields.Char(string="Date Asset")
    # invoice_id = fields.Char(string="Invoice ID")
    # payment_number = fields.Char(string="Payment Number")
    # asset_qty = fields.Char(string="Asset Qty")

    month = fields.Selection([
        ('01', 'Januari'), ('02', 'Februari'),
        ('03', 'Maret'), ('04', 'April'),
        ('05', 'Mei'), ('06', 'Juni'),
        ('07', 'Juli'), ('08', 'Agustus'),
        ('09', 'September'), ('10', 'Oktober'),
        ('11', 'November'), ('12', 'Desember')], string="Month")

    @api.model
    def get_year_selection(self):
        years = []
        show_year = 0
        next_year = datetime.today().year + 2
        while show_year < 10:
            years.append(next_year)
            next_year -= 1
            show_year += 1
        return [(str(year), str(year)) for year in years]

    @api.model
    def get_this_year(self):
        return str(datetime.today().year)

    year = fields.Selection(selection="get_year_selection", default="get_this_year", string="Year")
