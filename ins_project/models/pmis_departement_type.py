from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


class ProjectGroupType(models.Model):
    _name = 'pmis.departement.type'
    _description = 'PMIS Department Type'

    name = fields.Char('Type Name')
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('name', 'analytic_account_id')
    def _check_name(self):
        """ constrains function to check code duplicate """
        domain = [('name', '=ilike', self.name), ('id', '!=', self.id), ('analytic_account_id', '=', self.analytic_account_id.id)]
        rec = self.search(domain)
        if rec:
            raise Warning('Name already exists!')
