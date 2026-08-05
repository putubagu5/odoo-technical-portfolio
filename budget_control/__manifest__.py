# -*- coding: utf-8 -*-
{
    'name': "Budget Control",

    'author': "Invosa",

    'category': 'Accounting',
    'version': '0.1',

    'depends': [
        'base', 
        'account',
        'account_budget',
        'purchase_request',
        'purchase',
        'purchase_requisition',
        'stock',
        'purchase_stock',
    ],

    'data': [
        'security/ir.model.access.csv',
        'wizards/purchase_request_line_make_purchase_agreement.xml',
        'views/account_budget_post.xml',
        'views/crossovered_budget.xml',
        'views/purchase_request.xml',
        'views/purchase_order.xml',
        'views/stock_picking.xml',
        'views/budget_allocation.xml',
        'views/crossovered_budget_period.xml',
        'views/res_company.xml',
        'wizards/budget_summary.xml',
        'wizards/search_budget_line.xml',
        'wizards/reject_budget_reason.xml',
        'wizards/budget_summary_group.xml',
    ],
}
