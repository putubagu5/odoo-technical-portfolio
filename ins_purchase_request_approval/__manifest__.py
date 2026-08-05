# -*- coding: utf-8 -*-
{
    'name': "Dynamic Purchase Request Approval",

    'summary': """
        Dynamic approval module for purchase request
    """,

    'description': """
        Dynamic approval module for purchase request
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Approval',
    'version': '1.0',

    'depends': [
        'base',
        'purchase',
        'purchase_request',
        'ins_purchase_approval',
        'hr',
    ],

    'data': [
        'data/ir_cron.xml',
        'data/mail_approval_templates.xml',
        'security/ir.model.access.csv',
        'views/purchase_request_approval_views.xml',
        'views/purchase_request_message_views.xml',
        'views/purchase_request_views.xml',
        'views/portal_templates.xml',
    ],
}
