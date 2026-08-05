from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


class ProjectGroupType(models.Model):
    _name = 'project.group.type'
    _inherit = 'project.mixin'
    _description = 'Project Group Type'

    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('code', 'analytic_account_id')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id), ('analytic_account_id', '=', self.analytic_account_id.id)]
        rec = self.search(domain)
        if rec:
            raise Warning('Code already exists!')

    def unlink(self):
        for rec in self:
            range_obj = rec.env['pmis.project.task']
            range_obj_2 = rec.env['product.template']
            rule_ranges = range_obj.search([('group_type_id', '=', rec.id)])
            rule_ranges_2 = range_obj_2.search([('group_type_id', '=', rec.id)])
            if rule_ranges:
                raise UserError(_("You are trying to delete a record that is still referenced in task!"))
            if rule_ranges_2:
                raise UserError(_("You are trying to delete a record that is still referenced in product!"))
        return super(ProjectGroupType, self).unlink()

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.code}] {rec.name}'
            result.append((rec.id, name))
        return result
