from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AndReportWizard(models.AbstractModel):
    _name = 'and.report.wizard'
    _description = 'And Report Wizard'

    def default_get(self, fields):
        res = super(AndReportWizard, self).default_get(fields)
        res['company_id'] = self.env.user.company_id.id
        if self.env.context.get('allowed_company_ids', []):
            res['company_id'] = self.env.context['allowed_company_ids'][0]

        return res

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

    analytic_account_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Analytic Account'),
        ],
        string='Analytic Account Type',
        help='Analytic account type used to filter report by all or specific analytic account',
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
        string='Customer',
        help='Customer type used to filter report by all or specific customer',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        help='Company used to filter report',
    )

    supplier_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Suppliers'),
        ],
        string='Supplier Type',
        help='Supplier type used to filter report by all or specific supplier',
    )

    buyer_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Buyers'),
        ],
        string='Buyer Type',
        help='Buyer type used to filter report by all or specific buyer',
    )

    program_code_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Program Code'),
        ],
        string='Program Code Type',
        help='Program code type used to filter report by all or specific program code',
    )

    item_code_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Item Code'),
        ],
        string='Item Code Type',
        help='Item code type used to filter report by all or specific item code',
    )

    item_id = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Buyers'),
        ],
        string='Item Type',
        help='Item type used to filter report by all or specific Item',
    )

    type_pr = fields.Selection(
        selection=[
            ('all', 'All'),
            ('specific', 'Specific Buyers'),
        ],
        string='Type PR',
        help='Type PR used to filter report by all or specific PR',
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

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.currency_type = 'all'
        self.account_type = 'all'
        self.analytic_account_type = 'all'
        self.customer_type = 'all'
        self.supplier_type = 'all'
        self.buyer_type = 'all'
        self.program_code_type = 'all'
        self.item_code_type = 'all'
        self.item_id = 'all'
        self.type_pr = 'all'
        return {
            'domain': {
                'company_id': [('id', 'in', self.env.user.company_ids.ids)]
            }
        }

    @api.onchange('date_type')
    def onchange_date_type(self):
        self.end_date = False

    def get_date_title(self):
        for wizard in self:
            date_title = '{start_date}'.format(start_date=wizard.start_date)
            if wizard.date_type and wizard.date_type == 'as_of_date':
                date_title = 'until {start_date}'.format(start_date=wizard.start_date)
            elif wizard.date_type and wizard.date_type == 'current_date':
                date_title = '{start_date}'.format(start_date=wizard.start_date)
            elif wizard.date_type and wizard.date_type == 'range_of_date' \
                    and wizard.end_date:
                date_title = '{start_date} - {end_date}'. \
                    format(start_date=wizard.start_date, end_date=wizard.end_date)

            return date_title
