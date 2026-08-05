from odoo import api, fields, models


class ResFloor(models.Model):
    _name = 'res.floor'
    _inherit = 'res.master.mixin'
    _description = 'Floor'
