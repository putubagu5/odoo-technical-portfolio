from odoo import api, fields, models


class ApprovalHierarchy(models.Model):
    _name = 'approval.hierarchy'
    _description = 'Approval Hierarchy'

    name = fields.Char('Name', copy=False)
    module = fields.Selection([
        ('purchase.order', 'Purchase Order'),
    ], 'Module', default='purchase.order')
    company_id = fields.Many2one('res.company', 'Company')
    line_ids = fields.One2many('approval.hierarchy.line', 'hierarchy_id',
                               'Details')
