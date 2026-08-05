# -*- coding: utf-8 -*-
{
    'name': "Dynamic Purchase Approval",

    'summary': """
        Dynamic approval module for purchase
    """,

    'description': """
        Dynamic approval module for purchase
        Enables user to approve Purchase Order from email

        Note:
        Make sure to enable server_wide_module in the configuration and add
        this module in the list
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Approval',
    'version': '1.0',

    'depends': [
        'base',
        'mail',
        'purchase',
        'hr',
    ],

    'data': [
        'data/ir_cron.xml',
        'data/mail_approval_templates.xml',
        'security/ir.model.access.csv',
        'security/approval_security.xml',
        'views/menu_views.xml',
        'views/res_company_views.xml',
        'views/approval_group_views.xml',
        'views/approval_delegation_views.xml',
        'views/approval_hierarchy_line_views.xml',
        'views/approval_hierarchy_views.xml',
        'views/purchase_order_approval_views.xml',
        'views/purchase_order_message_views.xml',
        'views/purchase_order_views.xml',
        'views/portal_templates.xml',
        'views/hr_job_views.xml',
        'views/hr_position_views.xml',
        'views/hr_employee_views.xml',
    ],
}
