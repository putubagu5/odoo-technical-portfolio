# -*- coding: utf-8 -*-
{
    'name': "Asset Management",

    'summary': """
        Fixed Asset Management Module
    """,

    'description': """
        Handles data for fixed assets
    """,

    'author': "Invosa Systems",
    'website': "http://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'account_asset',
        'purchase_request',
        'budget_control',
        'ins_asset',
    ],

    'data': [
        'security/ir.model.access.csv',
        # 'views/cip_configuration_views.xml',
        'views/purchase_order_line_views.xml',
        'views/phase_project_cip_views.xml',
        'views/product_template_views.xml',
        'wizard/mass_cip_generate_views.xml',
    ],
}
