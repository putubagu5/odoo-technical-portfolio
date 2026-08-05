from odoo import fields, models


class ResAssigneeBill(models.Model):
    _name = 'res.assignee.bill'
    _description = 'Assignee (Bill)'

    doc_position = fields.Char('Doc Position', copy=False)
    name = fields.Char('Name', copy=False)
    job_position = fields.Char('Job Position', copy=False)
    company_ids = fields.Many2many('res.company', 'res_assignee_bill_company_rel', string='Company')
