from odoo import models, tools, fields, api, _
from odoo.exceptions import MissingError, ValidationError


class UsageCostsGen21(models.Model):
    _name = "usage.costs.gen21"

    name = fields.Char('Name')
    line_ids = fields.One2many('usage.costs.line.gen21', 'usage_costs_id_gen21', string='Usage Costs Line', readonly=True)
    company_id = fields.Many2one('res.company', string='Company')
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('wait', 'Waiting To Posted'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='wait')
    total_amount_debit = fields.Float("Total Amount Debit", compute="_compute_total_debit")
    total_amount_credit = fields.Float("Total Amount Credit", compute="_compute_total_credit")
    total_line = fields.Float("Total Line", compute="_compute_total_line")
    header_attribute1 = fields.Char("PO/Contract Number", compute="_compute_header_line", store=True)
    header_attribute2 = fields.Char("Approval Hierarchy", compute="_compute_header_line", store=True)
    header_attribute3 = fields.Char("Name Program", compute="_compute_header_line", store=True)
    header_attribute4 = fields.Char("Episode No", compute="_compute_header_line", store=True)
    header_attribute5 = fields.Char("Name Title Episode", compute="_compute_header_line", store=True)

    def _compute_header_line(self):
        for record in self:
            attribute1 = ''
            attribute2 = ''
            attribute3 = ''
            attribute4 = ''
            attribute5 = ''
            if len(record.line_ids) > 0:
                for line in record.line_ids:
                    if line.attribute1:
                        attribute1 = line.attribute1
                    
                    if line.attribute2:
                        attribute2 = line.attribute2
                    
                    if line.attribute3:
                        attribute3 = line.attribute3
                    
                    if line.attribute4:
                    
                        attribute4 = line.attribute4
                    if line.attribute5:
                        attribute5 = line.attribute5
            record.header_attribute1 = attribute1
            record.header_attribute2 = attribute2
            record.header_attribute3 = attribute3
            record.header_attribute4 = attribute4
            record.header_attribute5 = attribute5
    
    @api.model
    def create(self, vals):
        """ inherit function to create line_number """
        if vals.get('line_ids', []):
            lines = vals.get('line_ids', [])
            for idx, line in enumerate(lines):
                line[2].update({'line_number': idx + 1})
        res = super(UsageCostsGen21, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite line number """
        res = super(UsageCostsGen21, self).write(vals)
        for idx, line in enumerate(self.line_ids):
            line.line_number = idx + 1
        return res
    
    def _compute_total_debit(self):
        for record in self:
            if len(record.line_ids) > 0:
                record.total_amount_debit = sum([line.entered_dr for line in record.line_ids])
            else:
                record.total_amount_debit = 0
    
    def _compute_total_credit(self):
        for record in self:
            if len(record.line_ids) > 0:
                record.total_amount_credit = sum([line.entered_cr for line in record.line_ids])
            else:
                record.total_amount_credit = 0

    def _compute_total_line(self):
        for record in self:
            record.total_line = len(record.line_ids)
    
    def button_post(self):
        data_posted = []
        if len(self.line_ids) > 0:
            for line in self.line_ids:
                check_journal = self.env['account.move'].search([('name', '=', line['reference1'] + "-" + self.name), ('move_type', '=', 'entry'), ('state', '!=', 'cancel')])
                if check_journal:
                    raise ValidationError(_("Can't duplicated journal. No Usage Costs: "+ line['reference1']))
                journal_usage = self.env['account.journal'].search([('name', '=', line['user_je_category_name']), ('company_id', '=', line['company_id'].id)])
                if not journal_usage:
                    raise ValidationError(_("Journal does not exist or not active. No Usage Costs: "+ line['reference1']))
                else:
                    journal_usage = journal_usage[0]
                if journal_usage:
                    new_journal = True
                    if len(data_posted) > 0:
                        for data in data_posted:
                            if (data['reference1_gl_gen21'] == line['reference1']) and (data['date'] == line['accounting_date']):
                                analytic_account_id = self.env['account.analytic.account'].search([('code', '=', line['segment3']), ('company_id', '=', data['company_id'])])
                                if not analytic_account_id:
                                    raise ValidationError(_("Analytic Account does not exist or not active. No Usage Costs: "+ line['reference1']))
                                else:
                                    analytic_account_id = analytic_account_id[0].id
                                operating_unit_id = self.env['operating.unit'].search([('code', '=', line['segment4'])])
                                if not operating_unit_id:
                                    raise ValidationError(_("Operating Unit does not exist or not active. No Usage Costs: "+ line['reference1']))
                                else:
                                    operating_unit_id = operating_unit_id[0].id
                                account_id = self.env['account.account'].search([('code', '=', line['segment2']), ('company_id', '=', data['company_id'])])
                                if not account_id:
                                    raise ValidationError(_("Account does not exist or not active. No Usage Costs: "+ line['reference1']))
                                else:
                                    account_id = account_id[0].id
                                check_currency_id = self.env['res.currency'].search([('id', '=', data['currency_id'])])
                                amount_currency = 0
                                if check_currency_id.name != 'IDR':
                                    if line['entered_dr'] != 0:
                                        amount_currency = line['entered_dr']
                                    if line['entered_cr'] != 0:
                                        amount_currency = line['entered_cr'] * -1
                                name_line = ''
                                if line['attribute1']:
                                    name_line = name_line + line['attribute1']
                                if line['attribute3']:
                                    name_line = name_line + '-' + line['attribute3']
                                if line['attribute4']:
                                    name_line = name_line + '-' + line['attribute4']
                                values_line = (0, 0, {
                                    "account_id": account_id,
                                    "name": name_line,
                                    "analytic_account_id": analytic_account_id,
                                    "operating_unit_id": operating_unit_id,
                                    "currency_id": data['currency_id'],
                                    "amount_currency": amount_currency,
                                    "quantity": 1.0,
                                    "debit": line['accounted_dr'],
                                    "credit": line['accounted_cr']
                                })
                                data['line_ids'].append(values_line)
                                new_journal = False
                    if new_journal:
                        company_id = self.env['res.company'].search([('company_code', '=', line['segment1'])])
                        if not company_id:
                            raise ValidationError(_("Company does not exist or not active. No Usage Costs: "+ line['reference1']))
                        else:
                            company_id = company_id[0].id
                        account_id = self.env['account.account'].search([('code', '=', line['segment2']), ('company_id', '=', company_id)])
                        if not account_id:
                            raise ValidationError(_("Account does not exist or not active. No Usage Costs: "+ line['reference1']))
                        else:
                            account_id = account_id[0].id
                        manual_currency_rate_active = False
                        manual_currency_rate = False
                        if line['user_currency_conversion_type'] == 'IDR':
                            currency_id = self.env['res.currency'].search([('name', '=', line['user_currency_conversion_type'])])
                            if not currency_id:
                                currency_id = False
                            else:
                                currency_id = currency_id[0].id
                        else:
                            currency_id = self.env['res.currency'].search([('name', '=', line['currency_code'])])
                            if not currency_id:
                                currency_id = False
                            else:
                                currency_id = currency_id[0].id
                            manual_currency_rate = line['currency_conversion_rate']
                            manual_currency_rate_active = True
                        analytic_account_id = self.env['account.analytic.account'].search([('code', '=', line['segment3']), ('company_id', '=', company_id)])
                        if not analytic_account_id:
                            raise ValidationError(_("Analytic Account does not exist or not active. No Usage Costs: "+ line['reference1']))
                        else:
                            analytic_account_id = analytic_account_id[0].id
                        
                        operating_unit_id = self.env['operating.unit'].search([('code', '=', line['segment4'])])
                        if not operating_unit_id:
                            raise ValidationError(_("Operating Unit does not exist or not active. No Usage Costs: "+ line['reference1']))
                        else:
                            operating_unit_id = operating_unit_id[0].id
                        check_currency_id = self.env['res.currency'].search([('id', '=', currency_id)])
                        amount_currency = 0
                        if check_currency_id.name != 'IDR':
                            if line['entered_dr'] != 0:
                                amount_currency = line['entered_dr']
                            if line['entered_cr'] != 0:
                                amount_currency = line['entered_cr'] * -1
                        name_line = ''
                        if line['attribute1']:
                            name_line = name_line + line['attribute1']
                        if line['attribute3']:
                            name_line = name_line + '-' + line['attribute3']
                        if line['attribute4']:
                            name_line = name_line + '-' + line['attribute4']
                        values = {
                            "name": line['reference1'] + "-" + self.name,
                            "move_type": "entry",
                            "company_id": company_id,
                            "journal_id": journal_usage.id,
                            "currency_id": currency_id,
                            "manual_currency_rate_active": manual_currency_rate_active,
                            "manual_currency_rate": manual_currency_rate,
                            "date": line['accounting_date'],
                            "line_ids": [
                                (0, 0, {
                                    "account_id": account_id,
                                    "name": name_line,
                                    "analytic_account_id": analytic_account_id,
                                    "operating_unit_id": operating_unit_id,
                                    "currency_id": currency_id,
                                    "amount_currency": amount_currency,
                                    "quantity": 1.0,
                                    "debit": line['accounted_dr'],
                                    "credit": line['accounted_cr']
                                })
                            ],
                            "actual_flag_gl_gen21": line['actual_flag'],
                            "attribute1_gl_gen21": line['attribute1'],
                            "attribute2_gl_gen21": line['attribute2'],
                            "attribute3_gl_gen21": line['attribute3'],
                            "attribute4_gl_gen21": line['attribute4'],
                            "attribute6_gl_gen21": line['attribute6'],
                            "attribute7_gl_gen21": line['attribute7'],
                            "attribute8_gl_gen21": line['attribute8'],
                            "attribute9_gl_gen21": line['attribute9'],
                            "created_by_gl_gen21": line['created_by'],
                            "material_id_gl_gen21": line['material_id'],
                            "group_id_gl_gen21": line['group_id'],
                            "reference1_gl_gen21": line['reference1'],
                            "reference4_gl_gen21": line['reference4'],
                            "segment5_gl_gen21": line['segment5'],
                            "segment6_gl_gen21": line['segment6'],
                            "send_date_gl_gen21": line['send_date'],
                            "send_flag_gl_gen21": line['send_flag'],
                            "update_date_gl_gen21": line['update_date'],
                            "update_user_gl_gen21": line['update_user'],
                            "usage_number_gl_gen21": line['usage_number'],
                            "usage_run_id_gl_gen21": line['usage_run_id'],
                            "state": "draft",
                            "is_post_gen21": True,
                        }
                        data_posted.append(values)
            if len(data_posted) > 0:
                account_move = self.env['account.move'].create(data_posted)
                if account_move:
                    self.write({'state': 'posted'})
                else:
                    raise ValidationError(_("Failed null data Usage Costs"))    
        else:
            raise ValidationError(_("Failed null data Usage Costs"))
        return True
    
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True
