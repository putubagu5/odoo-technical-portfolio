# -*- coding: utf-8 -*-
{
    'name': "Report Xlsx Sub Ledger Detail",

    'summary': """
    
    """,

    'description': """
        Accounting Reports Xlsx
    """,

    'author': "MNC Corporation",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'ins_accounting',
                'ins_base_mnc',
                'account_accountant',
                'report_xlsx',
                'mnc_menu_report', ],

    # always loaded
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Report
        'report/report_data.xml',
        # Wizard
        'wizard/wizard_purchase_order_list_views.xml',
        'wizard/wizard_asset_clearing_views.xml',
        # 'wizard/wizard_mnc_sub_ledger_report.xml',
        # 'wizard/wizard_trial_balance_report_views.xml',
    ],
}