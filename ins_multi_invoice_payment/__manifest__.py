{
    "name": "Multi Invoice Payment For Customer and Vendor || Multiple Invoice Payment",
    "version": "14.0.0.1",
    "description": """
        Using this module you can pay multiple invoice payment in one click.
    """,
    # 'price': 12,
    # 'currency': 'EUR',
    'license': 'LGPL-3',
    "author": "Invosa Systems",
    # "email": 'apps@maisolutionsllc.com',
    "website": 'http://invosa.com/',
    'category': "Accounting",
    'summary': "Using this module you can pay multiple invoice payment in one click. Multiple invoice payment in one click for customer",
    "depends": [
        "account", "account_check_printing"
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/multi_invoice_payment_views.xml'
    ],
    'qweb': [
        # 'static/src/xml/pos_receipt.xml',
    ],
    'css': [],
    'js': [],
    # "images": ['static/description/main_screenshot.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
