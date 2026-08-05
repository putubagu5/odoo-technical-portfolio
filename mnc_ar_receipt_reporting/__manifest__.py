# -*- coding: utf-8 -*-
{
    'name': "AR Receipt Report",
    'summary': """
        Feature AR receipt report
    """,
    'description': """
        Feature AR receipt report
    """,
    'author': 'Hutomo Pebri Anditya',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'account',
        'report_xlsx',
        'mnc_menu_report'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/ar_receipt_report_wizard.xml',
        'views/ar_receipt_report_menu.xml',
        'report/ar_receipt_report.xml',
    ],
}
