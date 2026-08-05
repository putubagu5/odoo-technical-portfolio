# -*- coding: utf-8 -*-
{
    'name': "MNC Sync",

    'summary': """
        MNC Sync Module
        
        1. Sync Odoo Staging Table with Oracle Staging Table """,

    'description': """
        Sync Odoo Staging Table with Oracle Staging Table
    """,
    'author': 'Badra Wiryadinata + Syarif Hidayatullah',
    'website': 'https://www.mncgroup.com/',
    'license': 'OPL-1',
    'category': 'Tools',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'stock', 'ins_asset',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/mnc_man_sync_main_menu.xml',
        'views/mnc_sync_logger.xml',
        'views/mnc_r12_po_receives.xml',
        'views/mnc_token_management.xml',
        'views/mnc_xitem.xml',
        'views/mnc_xlocation.xml',
        'views/mnc_xpeople.xml',
        'views/mnc_xasset.xml',
        'views/account_asset_views.xml',
        'wizard/wizard_reconcile_data_views.xml',
        'wizard/wizard_atis_fix_asset_report_views.xml',
    ],
    'installable': True,
    'auto_install': False,

}