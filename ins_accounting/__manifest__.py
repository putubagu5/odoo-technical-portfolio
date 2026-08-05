# -*- coding: utf-8 -*-
{
    'name': "Base Accounting",

    'summary': """
        Base Accounting
    """,

    'description': """
        Base Accounting\n
        1. Ability to change Customer Invoice (AR) account\n
        2. Ability to deplete subscriptions based in pre-paid customer invoice\n
        3. Ability to add state and related invoices to payment\n
        4. Show Bank Menu\n
        5. Check Data\n
        6. Payment Document Number\n
    """,

    'author': "Invosa Systems",
    'website': "https://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'account_payment',
        'sale_subscription',
        'l10n_us_check_printing',
        'account_document_reversal'
    ],

    'data': [
        'data/ir_sequence.xml',
        'data/payment_method_data.xml',
        'security/ir.model.access.csv',
        'security/ins_accounting_security.xml',
        'wizard/payment_invoice_views.xml',
        'views/account_transaction_type_views.xml',
        'views/account_move_views.xml',
        'views/res_bank_views.xml',
        'views/account_payment_views.xml',
        'views/bank_cash_transfer.xml',
        'views/sale_subscription_views.xml',
        'views/res_check_views.xml',
        'views/res_giro_views.xml',
        'views/res_payment_document_views.xml',
        'views/remittance_views.xml',
        'views/account_journal_views.xml',
        'views/adjustment_account_receivable_views.xml',
        'views/adjustment_account_payable_views.xml',
        'views/account_invoice_reversal_view.xml',
        'report/report_views.xml',
        'report/report_payment_invoice_templates.xml',
        # 'report/report_payment_invoice_valas_templates.xml',
        'report/report_payment_slip_templates.xml',
        'report/report_payment_slip_valas_templates.xml',
        'report/report_check_templates.xml',
        'report/report_giro_templates.xml',
        'report/report_check_muamalat_templates.xml',
        'report/report_check_mandiri_templates.xml',
        'report/report_check_konversi_templates.xml',
        'report/report_check_muamalat_konversi_templates.xml',
        'report/report_check_mandiri_konversi_templates.xml',
        "report/report_check_bca_templates.xml",
        "report/report_check_bjb_templates.xml",
        "report/report_check_bri_templates.xml",
        "report/report_check_capital_templates.xml",
        "report/report_check_mncbank_templates.xml",
        "report/report_check_permata_templates.xml",
        "report/report_check_sinarmas_templates.xml",
        "report/report_payment_slip_bca_templates.xml",
        "report/report_payment_slip_bjb_templates.xml",
        "report/report_payment_slip_bri_templates.xml",
        "report/report_payment_slip_mncbank_templates.xml",
        "report/report_payment_slip_kliring_mandiri_templates.xml",
        "report/report_payment_slip_multi_mandiri_templates.xml",
    ],
}
