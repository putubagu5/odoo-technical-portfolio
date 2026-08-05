# -*- coding: utf-8 -*-
{
    'name': "Bank Indonesia Exchange",

    'summary': """
        Bank Indonesia Currency Exchange
    """,

    'description': """
        Bank Indonesia Currency Exchange
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'currency_rate_live',
    ],

    'data': [
        'views/res_currency_rate_views.xml',
    ],
}
