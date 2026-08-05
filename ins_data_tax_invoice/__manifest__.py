# -*- coding: utf-8 -*-
{
    'name': "Tax Invoice Data",

    'summary': """
        Tax Invoice Data for City, Kecamatan, and Kelurahan in Indonesia
    """,

    'description': """
        Tax Invoice Data for City, Kecamatan, and Kelurahan in Indonesia
    """,

    'author': "Invosa Systems",
    'website': "http://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'account_accountant'
    ],

    'data': [
        'security/ir.model.access.csv',
        # 'data/res.country.state.csv',
        # 'data/res.city.csv',
        # 'data/res.kecamatan.csv',
        # 'data/res.kelurahan.csv',
        'views/res_city_views.xml',
        'views/res_kecamatan_views.xml',
        'views/res_kelurahan_views.xml',
        'views/res_partner_views.xml',
    ],
}