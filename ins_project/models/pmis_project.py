from odoo import api, fields, models


class PmisProject(models.Model):
    _name = 'pmis.project'
    _description = 'Project'

    program_id = fields.Many2one(
        'res.users', string="Program ID",
        default=lambda self: self.env.user.id)
    name = fields.Char('Program Name', copy=False)
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project ID')
    category_id = fields.Many2one(
        'project.classification',
        'Category / Classification')
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account")
    budget_type = fields.Selection([
        ('absolute', "Absolute"),
        ('advisory', "Advisory"),
        ], string="Budget Type")
    company_id = fields.Many2one(
        'res.company', string='Company', store=True,
        default=lambda self: self.env.company)
    description = fields.Char('Description / Sinopsis')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    create_date = fields.Datetime(string='Created On')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for record in self:
            if record.company_id.default_budget_type_project:
                record.budget_type = record.company_id.default_budget_type_project
