## -*- coding: utf-8 -*-
{
    'name': "Base Api",
    'summary': "",

    'description': "",

    'author': "Invosa",
    'website': "http://www.invosa.com",

    'category': '',
    'version': '0.1',

    'depends': [
        'base',
        'contacts',
        'account',
        'account_accountant',
        'ins_tax_invoice',
        'ins_accounting',
        'ins_base_mnc',
        'purchase_request'
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/account_rule.xml',
        'views/menu_views.xml',
        'views/res_api_key_views.xml',
        'views/account_move_ar_gen21.xml',
        'views/account_move_ar_line_gen21.xml',
        'views/account_move_trading_gen21.xml',
        'views/account_move_trading_line_gen21.xml',
        'views/account_move_views.xml',
        'views/inventory_costs_gen21.xml',
        'views/inventory_costs_line_gen21.xml',
        'views/program_costs_gen21.xml',
        'views/program_costs_line_gen21.xml',
        'views/usage_costs_gen21.xml',
        'views/usage_costs_line_gen21.xml',
        #'views/res_agency_gen21.xml',
        # 'views/res_channel_gen21.xml',
        # 'views/res_region_gen21.xml',
        'views/res_partner_views.xml',
        'views/purchase_request_views.xml',
        'views/account_payment_term_views.xml',
        'views/account_transaction_type_views.xml',
        'views/purchase_order_line_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_line_views.xml',
        'wizard/purchase_request_line_make_purchase_order_views.xml',
        'wizard/add_to_pr_views.xml',
        'report/report_views.xml',
        'report/report_ar_3tv_templates.xml',
        'report/report_invoice_ar_3tv_templates.xml',
        'report/report_invoice_ar_3tv_bms_templates.xml',
        'report/report_invoice_ar_3tv_bms_new_templates.xml',
        'report/report_ar_3tv_txt_new_templates.xml',
        'report/report_ar_3tv_afidafit_templates.xml',
        'report/report_ar_3tv_afidafit_nologo_templates.xml'
    ],
}