from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError


class BroadcastType(models.Model):
    _name = 'broadcast.type'
    _description = 'Broadcast Type'

    name = fields.Char('Name', copy=False)
    description = fields.Char('Description', copy=False)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')

    @api.constrains('name')
    def _check_name(self):
        """ constrains function to check code duplicate """
        domain = [('name', '=ilike', self.name), ('id', '!=', self.id)]
        rec = self.search(domain)
        if rec:
            raise Warning('Name already exists!')

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        self.ensure_one()
        if self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Start Date must be earlier than End Date')

    def unlink(self):
        range_obj = self.env['pmis.project.task']
        rule_ranges = range_obj.search([('live_tapping', '=', self.id)])
        if rule_ranges:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(BroadcastType, self).unlink()
