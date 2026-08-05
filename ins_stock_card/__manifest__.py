# -*- coding: utf-8 -*-
{
    'name': "Stock Card",

    'summary': """
        Handles stock card process
    """,

    'description': """
        Handles stock card process
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Warehouse',
    'version': '1.0',

    'depends': [
        'base',
        'product',
        'stock',
    ],

    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/stock_card_views.xml',
        'views/stock_card_summary_views.xml',
    ],
}
