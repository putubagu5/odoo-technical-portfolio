from odoo import api, fields, models
from odoo.exceptions import Warning


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char('Company ID', copy=False)
    printout_type = fields.Selection([
        ('print1', "Printout 1"),
        ('print2', "Printout 2"),
        ], string="Printout Type")
    assignee_ids = fields.One2many(
        comodel_name="pmis.assignee",
        inverse_name="company_line_id",
        string="Assignee",
    )
    signature_id = fields.Many2one(
        comodel_name="pmis.assignee",
        string="Signatures",
    )
    default_budget_type_project = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
        ], string="Program")
    default_budget_type_task = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
        ], string="Task (Phase)")
    default_budget_type_subtask = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
        ], string="Sub Task (Episode)")
    default_budget_type_category = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
        ], string="Category Expenditure")
    default_budget_type_subcategory = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
        ], string="Sub Category Expenditure")
    status_task = fields.Selection([
        ('active', "Active"),
        ('inactive', "Inactive"),
        ], string="Status Task")

    @api.constrains('company_code')
    def _check_company_code(self):
        """ constrains function to check company_code duplicate """
        domain = [
            ('company_code', '!=', '/'),
            ('company_code', '=ilike', self.company_code),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Company ID already exists!')
