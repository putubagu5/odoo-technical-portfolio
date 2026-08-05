from odoo import fields, models, api


class MasterEpisode(models.Model):
    _name = 'purchase.master.episode'

    name = fields.Integer(string='episode')
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The epsiode name is already exist! please use another episode name')
    ]
