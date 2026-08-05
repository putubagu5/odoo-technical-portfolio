from odoo import api, fields, models, _
from odoo.exceptions import Warning


class PmisEpisodeLine(models.Model):
    _name = 'pmis.episode.line'
    _description = 'Episode Line Data'
    _order = 'sequence'

    episode_id = fields.Many2one('pmis.episode', 'Episode', ondelete='cascade')
    episode_no = fields.Integer('Episode No')
    sequence = fields.Integer('No', compute='_compute_sequence')
    name = fields.Char('Episode Name')
    code = fields.Char('Program Code')
    date_start = fields.Date('Start Date', default=fields.Date.today())
    date_end = fields.Date('End Date')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    @api.depends('episode_id.line_ids')
    def _compute_sequence(self):
        """ compute function to get sequence """
        for rec in self:
            no = 0
            rec.sequence = no
            for l in rec.episode_id.line_ids:
                no += 1
                l.sequence = no

    @api.constrains('code')
    def _check_code(self):
        """ constrains function to check code duplicate """
        for rec in self:
            domain = [
                ('code', '=ilike', rec.code),
                ('id', '!=', rec.id),
                ('episode_id', '=', rec.episode_id.id),
            ]
            line = rec.search(domain)
            if line:
                raise Warning('Code already exists!')

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        """ constrains function to check date validity """
        for rec in self:
            if rec.date_end:
                if rec.date_start > rec.date_end:
                    raise Warning('Start Date must be earlier than End Date')

    @api.constrains('episode_no')
    def _check_episode_no(self):
        """ constrains function to check episode_no duplicate """
        for rec in self:
            domain = [
                ('episode_no', '=', rec.episode_no),
                ('id', '!=', rec.id),
                ('episode_id', '=', rec.episode_id.id),
            ]
            line = rec.search(domain)
            if line:
                raise Warning('Duplicate episode number!')

    def unlink(self):
        for rec in self:
            range_obj = rec.env['pmis.project.task.line']
            rule_ranges = range_obj.search([('episode_line_id', '=', rec.id)])
            if rule_ranges:
                raise Warning(_("You are trying to delete a record that is still referenced!"))
        return super(PmisEpisodeLine, self).unlink()
