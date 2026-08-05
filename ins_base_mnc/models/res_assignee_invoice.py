from odoo import fields, models


class ResAssigneeInvoice(models.Model):
    _name = 'res.assignee.invoice'
    _description = 'Assignee (Invoice)'

    doc_position = fields.Char('Doc Position', copy=False)
    name = fields.Char('Name', copy=False)
    job_position = fields.Char('Job Position', copy=False)
    company_ids = fields.Many2many('res.company', 'res_assignee_invoice_company_rel', string='Company')
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)
    signature = fields.Binary(string="Signature")
    is_default = fields.Boolean(string="Is Default")
