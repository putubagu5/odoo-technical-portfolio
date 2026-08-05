from odoo import api, fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', check_company=True)
