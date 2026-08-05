from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AndReportWizard(models.AbstractModel):
    _name = 'and.report.wizard'
    _description = 'And Report Wizard'

    date_type = fields.Selection(
        selection=[
            ('as_of_date', 'As Of Date'),
            ('current_date', 'Current Date'),
            ('range_of_date', 'Range of Date'),
        ],
        required=True,
        string='Date Type',
        help='Type of date used to filter report',
    )

    start_date = fields.Date(
        string='Start Date',
        help='Start date parameter used to filter AR receipt report',
        default=date.today(),
    )

    end_date = fields.Date(
        string='End Date',
        help='End date parameter used to filter AR receipt report',
        default=date.today() + timedelta(days=30),
    )

    report_type = fields.Selection(
        selection=[],
        string='Report Type',
        help='Abstract field type of report that need to be inherited',
    )

    currency_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Currency'),
        ],
        string='Currency Type',
        help='Currency type used to filter report by all or specific currency',
    )

    account_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Account'),
        ],
        string='Account Type',
        help='Account type used to filter report by all or specific account',
    )

    format_option = fields.Selection(
        selection=[
            ('detailed', 'Detailed'),
        ],
        string='Format Option',
        default='detailed',
        help='Format option of report used to filter report',
    )

    customer_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Customers'),
        ],
        string='Customer Type',
        help='Customer type used to filter report by all or specific customer',
    )

    @api.constrains('start_date', 'end_date')
    def constrains_range_of_date(self):
        for wizard in self:
            if wizard.start_date and wizard.end_date \
                    and wizard.start_date > wizard.end_date:
                raise ValidationError(
                    _('Invalid period!')
                )

    def generate_report_xlsx(self):
        # This method should be inherited
        return True