# -*- coding: utf-8 -*-
{
    'name': "MNC Sync Ext",

    'summary': """
        MNC Sync Module Ext
        
         """,

    'description': """

2	Get List Master Warehouse Location	This class purpose to insert data into tabel ATIS Master Location for LOV parameter in ATIS
3	Get List Master Employee	This class purpose to insert data into tabel ATIS Master Employee for LOV parameter in ATIS
4	Get List Master Item	This class purpose to insert data into tabel ATIS Master Item for LOV parameter in ATIS
5	Class Receipt Number	This class purpose to insert data into tabel ATIS Receipt Number for LOV parameter in ATIS
6	Class PO Number	This class purpose to insert data into tabel ATIS PO Number for LOV parameter in ATIS
7	Class PR Number	This class purpose to insert data into tabel ATIS PR Number for LOV parameter in ATIS
        
    """,
    'author': 'Badra Wiryadinata',
    'website': 'https://www.mncgroup.com/',
    'license': 'OPL-1',
    'category': 'Tools',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','hr','purchase_request','mnc_man_sync'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,

}