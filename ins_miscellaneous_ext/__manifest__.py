# -*- coding: utf-8 -*-
{
    'name': "ins_miscellaneous_ext",

    'summary': """
        Extended Ins_Miscellaneous Module""",

    'description': """
        this module for extended ins_miscellaneous
    """,

    'author': "Invosa System",
    'website': "http://www.Invosa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['ins_miscellaneous',
                'ins_base_mnc'
                ],

    # always loaded
    'data': [
        'views/miscellaneous_receipt_views.xml',
    ],
}
