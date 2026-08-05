from odoo import api, fields, models
from odoo.exceptions import Warning


class PmisEpisode(models.Model):
    _name = 'pmis.episode'
    _description = 'Episode Data'
    _rec_name = 'program_id'

    program_id = fields.Many2one('pmis.program', 'Program', ondelete='restrict')
    main_project_id = fields.Many2one('pmis.main.project', 'Main Project ID',
                                      related='program_id.main_project_id',
                                      store=True)
    line_ids = fields.One2many('pmis.episode.line', 'episode_id', 'Lines')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)

    @api.constrains('program_id')
    def _check_main_project_name(self):
        """ constrains function to check code duplicate """
        domain = [
            ('program_id', '=', self.program_id.id),
            ('id', '!=', self.id),
        ]
        rec = self.search(domain)
        if rec:
            raise Warning('Progam already exist in another episode!')
