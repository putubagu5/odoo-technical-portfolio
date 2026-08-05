from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


class ProjectGenre(models.Model):
    _name = 'project.genre'
    _inherit = 'project.mixin'
    _description = 'Project Genre'

    category_id = fields.Many2one(
        'project.classification',
        'Category / Classification')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)

    def name_get(self):
        result = []
        for rec in self:
            name = f'[{rec.code}] {rec.name}'
            result.append((rec.id, name))
        return result

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    @api.constrains('code', 'category_id')
    def _check_code(self):
        """ constrains function to check code duplicate """
        domain = [('code', '=ilike', self.code), ('id', '!=', self.id), ('category_id', '=', self.category_id.id)]
        rec = self.search(domain)
        if rec:
            raise Warning('Code already exists!')

    def unlink(self):
        for rec in self:
            range_obj = rec.env['pmis.program']
            rule_ranges = range_obj.search([('genre_id', '=', rec.id)])
            if rule_ranges:
                raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(ProjectGenre, self).unlink()
