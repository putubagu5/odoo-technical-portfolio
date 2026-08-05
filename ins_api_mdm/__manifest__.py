# -*- coding: utf-8 -*-
{
    'name': "Master Data Management - API",

    'summary': """
        Module for connecting to MDM
    """,

    'description': """
        Module for connecting to MDM
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Hidden',
    'version': '1.0',

    'depends': [
        'base',
        'ins_base_mnc',
    ],

    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'wizards/mdm_sync_views.xml',
    ],
}
