from odoo import api, fields, models


class ResMncMdm(models.Model):
    _name = 'res.mnc.mdm'

    # TODO think! do we need this or we just put the status in partner?
    # TODO jangan langsung dibuat modelnya, ini masih bisa berubah
    name = fields.Char('Vendor ID', help='This is the Reference ID')
    url = fields.Char('URL')
    state = fields.Selection([
        ('N', 'N'),
        ('E', 'E'),
        ('S', 'S'),
    ], 'State', help='S = Success, N = Nothing, E = Error')
