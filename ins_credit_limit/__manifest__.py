# -*- coding: utf-8 -*-
{
    'name': "Credit Limit",

    'summary': """
        Check credit limit of customer
    """,

    'description': """
        Check credit limit of the customer and compare to Sale Order amount.\n
        If the credit limit is below the due credit and sales order amount,
        warning will be raised
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'sale',
        'ins_accounting',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/credit_note_limit.xml',
    ],
}
