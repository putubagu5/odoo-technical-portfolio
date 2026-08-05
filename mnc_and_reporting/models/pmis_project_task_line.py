from odoo import models, api


class PMISProjectTaskLine(models.Model):
    _inherit = 'pmis.project.task.line'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(PMISProjectTaskLine, self).name_search(name=name, args=args, \
            operator=operator, limit=limit)
        if self.env.context.get('show_episode_code', False):
            new_res = []
            for line in self.browse([data[0] for data in res]):
                new_res.append((line.id, line.episode_code))

            return new_res

        return res