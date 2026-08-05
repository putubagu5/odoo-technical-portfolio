# -*- coding: utf-8 -*-
{
    'name': "ins_miscellaneous",

    'summary': """
        Miscellaneous (Bill Payment / Cash Bank Receipt) transaction in accounting module""",

    'description': """
        this module for use miscellaneous (Bill Payment / Cash Bank Receipt) transaction in accounting module
    """,

    'author': "Invosa System",
    'website': "http://www.Invosa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'account', 'operating_unit', 'account_operating_unit', 'oi_bank_reconciliation',
        'ins_accounting', 'account_document_reversal'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/miscellaneous_security.xml',
        'data/miscellaneous_data.xml',
        'views/miscellaneous_menu.xml',
        'views/payment_type.xml',
        'views/payable_activity.xml',
        'views/receipt_type.xml',
        'views/receivable_activity.xml',
        'views/misc_receipts_view.xml',
        'views/misc_payment_view.xml',
        'views/applied_invoice.xml',
        'views/applied_bill.xml',
        'views/account_move_view.xml',
        'report/report_views.xml',
        'report/report_check_templates.xml',
        'report/report_giro_templates.xml',
        'report/report_payment_invoice_templates.xml',
        'report/report_payment_slip_templates.xml',

        'wizards/account_bank_statement_generate.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
