from odoo import fields, models


class ResAssigneePo(models.Model):
    _name = 'res.assignee.po'
    _description = 'Assignee (PO)'

    doc_position = fields.Char('Doc Position', copy=False)
    name = fields.Char('Name', copy=False)
    job_position = fields.Char('Job Position', copy=False)
    company_ids = fields.Many2many('res.company', 'res_assignee_po_company_rel', string='Company')
