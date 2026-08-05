from odoo import api, fields, models


class ApprovalDelegation(models.Model):
    _name = 'approval.delegation'
    _description = 'Approval Delegation'
    _rec_name = 'delegator_id'

    module = fields.Selection([
        ('purchase.order', 'Purchase Order'),
    ], 'Module', default='purchase.order')
    delegator_id = fields.Many2one('hr.employee', 'Delegator', ondelete='restrict')
    delegatee_id = fields.Many2one('hr.employee', 'Delegatee', ondelete='restrict')
    company_id = fields.Many2one('res.company', 'Company')
    date_from = fields.Date('Delegated From')
    date_to = fields.Date('Delegated To')
    note = fields.Text('Note')
