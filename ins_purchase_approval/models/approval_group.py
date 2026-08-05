from odoo import api, fields, models


class ApprovalGroup(models.Model):
    _name = 'approval.group'
    _description = 'Approval Group'

    name = fields.Char('Name', copy=False, help='Unique Name')
    group_type = fields.Selection([
        ('exclude', 'Exclude'),
        ('include', 'Include'),
    ])
    amount_limit = fields.Float('Approve Limit', default=0.0)
    company_id = fields.Many2one('res.company', 'Company')
    currency_id = fields.Many2one('res.currency', 'Currency')
