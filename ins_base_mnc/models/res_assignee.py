from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResAssignee(models.Model):
    _name = 'res.assignee'
    _description = 'Assignee'

    doc_position = fields.Char('Doc Position', copy=False)
    name = fields.Char('Name', copy=False)
    job_position = fields.Char('Job Position', copy=False)

    # @api.constrains('name')
    # def _check_name(self):
    #     """ constrains function to check name duplicate """
    #     domain = [('name', '=ilike', self.name), ('id', '!=', self.id)]
    #     rec = self.search(domain)
    #     if rec:
    #         raise ValidationError('Name already exists!')

    # @api.constrains('code')
    # def _check_code(self):
    #     """ constrains function to check code duplicate """
    #     domain = [('code', '=ilike', self.code), ('id', '!=', self.id)]
    #     rec = self.search(domain)
    #     if rec:
    #         raise ValidationError('Code already exists!')
