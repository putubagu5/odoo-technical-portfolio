# -*- coding: utf-8 -*-
{
    "name": "MNC Reporting by HR",
    "author": "PT Media Nusantara Citra Tbk, "
              "Herul Ramdani",
    "website": "https://www.mnc.co.id",
    "version": "14.0",
    "category": "Reporting",
    "summary": "Reporting",
    "description": "Reporting",
    "depends": [
        "base", "account", "ins_accounting", "ins_project", "mnc_menu_report"
    ],
    "data":
        [
            "wizard/wizard_mnc_ar_report.xml",
            "wizard/wizard_mnc_ap_report.xml",
            "wizard/wizard_mnc_ar_customer_report.xml",
            "wizard/wizard_mnc_ap_standard_report.xml",
            "wizard/wizard_mnc_ar_receipt_invoice_report.xml",
            "wizard/wizard_mnc_ar_statement_report.xml",
            "wizard/wizard_mnc_ar_aging_report.xml",
            "wizard/wizard_mnc_ar_pph23_report.xml",
            "wizard/wizard_mnc_ar_collection_old_report.xml",
            "wizard/wizard_mnc_ar_collection_new_report.xml",
            "wizard/wizard_mnc_trial_balance_report.xml",
            "wizard/wizard_mnc_fix_asset_report.xml",
            "wizard/wizard_mnc_project_costing_report.xml",
            "wizard/wizard_mnc_project_costing_detail_report.xml",
            "wizard/wizard_mnc_ar_statement_account_report.xml",
            "wizard/wizard_mnc_asset_addition_report.xml",

            "report/mnc_ar_statement_report.xml",

            "security/ir.model.access.csv",

            "menu.xml",
        ],
    'installable': True,
    'application': True,
}
