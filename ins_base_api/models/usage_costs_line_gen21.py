from odoo import models, tools, fields, api, _


class UsageCostsLineGen21(models.Model):
    _name = "usage.costs.line.gen21"

    usage_costs_id_gen21 = fields.Many2one('usage.costs.gen21', string='Journal Entry Gen21',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="The move of this entry line.")
    user_je_source_name = fields.Char('Kategory Jurnal Entry')
    user_je_category_name = fields.Char('User Category Name')
    accounted_cr = fields.Float('Amount Credit')
    accounted_dr = fields.Float('Amount Debit')
    accounting_date = fields.Date('Accounting Date')
    actual_flag = fields.Char('Actual Flag')
    attribute1 = fields.Char('PO/Contract Number')
    attribute2 = fields.Char('Row ID Episode')
    attribute3 = fields.Char('Episode No')
    attribute4 = fields.Char('Episode Title')
    attribute5 = fields.Char('Nama Vendor / ID Epi')
    attribute6 = fields.Char('Episode Name')
    attribute7 = fields.Char('Attribute7')
    attribute8 = fields.Char('Nama Program')
    attribute9 = fields.Char('Attribute9')
    created_by = fields.Char('Created By')
    date_created = fields.Date('Create Date')
    currency_conversion_date = fields.Date('Currency Conversion Date')
    currency_conversion_rate = fields.Float('Currency Conversion Rate')
    currency_code = fields.Char('Currency Code')
    entered_cr = fields.Float('Entered CR')
    entered_dr = fields.Float('Entered DR')
    material_id = fields.Char('Material ID')
    group_id = fields.Char('Group ID')
    ledger_id = fields.Char('Ledger ID')
    period_name = fields.Char('Period Name')
    rec_number = fields.Integer('Rec Number')
    reference1 = fields.Char('Reference1')
    reference10 = fields.Char('Reference10')
    reference2 = fields.Char('Reference2')
    reference4 = fields.Char('Nama Program')
    reference5 = fields.Char('Reference5')
    segment1 = fields.Char('Company ID')
    segment2 = fields.Char('Account Code')
    segment3 = fields.Char('Analytic Account Code')
    segment4 = fields.Char('Operating Unit Code')
    segment5 = fields.Char('Segment5')
    segment6 = fields.Char('Segment6')
    send_date = fields.Date('Send Date')
    send_flag = fields.Char('Send Flag')
    send_flag_od = fields.Char('Send Flag OD')
    update_date = fields.Date('Update Date')
    update_user = fields.Char('Update User')
    uniqkey = fields.Char('Uniq Key')
    usage_number = fields.Integer('Usage Number')
    usage_run_id = fields.Integer('Usage Run ID')
    user_currency_conversion_type = fields.Char('User Currency Conversion Type')
    status = fields.Char('Status')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('wait', 'Waiting To Posted'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft', related="usage_costs_id_gen21.state")
    company_id = fields.Many2one('res.company', string='Company', related="usage_costs_id_gen21.company_id")
    line_number = fields.Integer(string='Line Number')
