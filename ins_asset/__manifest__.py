# -*- coding: utf-8 -*-
{
    'name': "Asset Management",

    'summary': """
        Asset Management Module
    """,

    'description': """
        Handles data for assets
    """,

    'author': "Invosa Systems",
    'website': "http://www.invosa.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': [
        'base',
        'account',
        'account_asset',
        'hr',
        'purchase',
        'stock',
        'stock_account',
        'ins_accounting',
        'ins_data_tax_invoice',
        'fiscal_year_sync_app',
    ],

    'data': [
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu_views.xml',
        'views/res_area_views.xml',
        'views/res_building_views.xml',
        'views/res_floor_views.xml',
        'views/asset_condition_views.xml',
        'views/asset_segment_views.xml',
        'views/asset_location_views.xml',
        'views/account_asset_templates.xml',
        'views/account_asset_views.xml',
        'views/asset_cost_progress_views.xml',
        'views/asset_progress_views.xml',
        'views/cip_configuration_views.xml',
        'views/account_move_views.xml',
        'views/product_template_views.xml',
        'views/asset_assignment_views.xml',
        'views/account_asset_account_move_views.xml',
        'views/asset_period_views.xml',
        'views/asset_period_line_views.xml',
        'wizard/mass_asset_generate_views.xml',
        'wizard/asset_modify_alt_views.xml',
        # 'wizard/asset_modify_views.xml',
        'wizard/asset_retire_views.xml',
        'wizard/asset_addition_views.xml',
        'wizard/sell_asset_views.xml',
        'report/asset_outstanding_report_views.xml',
    ],
}
