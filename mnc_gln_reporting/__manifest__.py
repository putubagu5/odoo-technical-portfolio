# -*- coding: utf-8 -*-
{
    'name': "All Reports Xlsx of Accounting",

    'summary': """
        Accounting Reports Xlsx
    """,

    'description': """
        Accounting Reports Xlsx
    """,

    'author': "MNC Corporation",

    'category': 'Report',
    'version': '1.0',

    'depends': [
        'account',
        'account_accountant',
        'report_xlsx',
        'mnc_menu_report',
        'purchase_requisition',
    ],

    'data': [
        'security/ir.model.access.csv',
        'report/report_data.xml',
        # 'wizard/wizard_trial_balance_views.xml',
        'wizard/wizard_purchase_requisition_list_views.xml',
    ],
}
