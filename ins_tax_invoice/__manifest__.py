# -*- coding: utf-8 -*-
{
    'name': "Indonesian Tax Invoice",

    'summary': """
        Handles tax invoice process (e-faktur)
    """,

    'description': """
        Handles tax invoice process (e-faktur)
        This module also includes the list of cities existing in Indonesia
    """,

    'author': "Invosa Systems",
    'website': "http://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'account_accountant',
        'ins_data_tax_invoice',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/tax_invoice_views.xml',
        'views/account_move_views.xml',
        'report/report_views.xml',
        'report/report_tax_invoice_views.xml',
        'wizard/tax_invoice_auto_views.xml',
        'wizard/tax_invoice_generate_views.xml',
        'wizard/tax_invoice_out_views.xml',
        'wizard/tax_invoice_out_multi_views.xml',
        'wizard/tax_invoice_in_views.xml',
        'wizard/product_template_views.xml',
    ],
}
