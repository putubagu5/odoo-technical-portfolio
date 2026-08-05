# -*- coding: utf-8 -*-
{
    'name': "MNC Xlsx Reporting",
    'summary': """
        Feature MNC accounting reports
    """,

    'description': """
        Feature MNC accounting reports
    """,

    'author': "PT Media Nusantara Citra Tbk",
    'category': 'Reporting',
    'version': '0.1',
    'depends': [
        'account',
        'mnc_menu_report',
        'ins_accounting',
        'report_xlsx',

    ],
    "data":
        [
            "security/ir.model.access.csv",

            # hrl
            "report/mnc_ar_statement_report.xml",
            "wizard/wizard_mnc_ap_report.xml",
            "wizard/wizard_mnc_ap_standard_report.xml",
            "wizard/wizard_mnc_ar_aging_report.xml",
            "wizard/wizard_mnc_ar_customer_report.xml",
            "wizard/wizard_mnc_ar_pph23_report.xml",
            "wizard/wizard_mnc_ar_receipt_invoice_report.xml",
            "wizard/wizard_mnc_ar_report.xml",
            "wizard/wizard_mnc_ar_statement_report.xml",
            # "menu.xml"

            # pbr
            # "report/aging_pdc_detail_report_dpf.xml",
            "report/and_action_report.xml",
            "report/and_report_paperformating.xml",
            "report/ar_receipt_report.xml",
            "report/receipt_voucher_report_pdf.xml",
            "views/aging_pdc_detail_menu.xml",
            "views/aging_report_detail_menu.xml",
            "views/aging_report_summary_menu.xml",
            "views/ar_receipt_report_menu.xml",
            "views/ar_unapplied_receipt_report_menu.xml",
            "views/invoice_prepayment_paid_supplier_menu.xml",
            "views/unapplied_receipt_register_report_menu.xml",
            "wizard/and_report_wizard.xml",
            "wizard/ar_receipt_report_wizard.xml",
            "wizard/unapplied_receipt_register_report_wizard.xml",
            "wizard/invoice_prepayment_paid_supplier_wizard.xml",
            "wizard/aging_pdc_detail_report_wizard.xml",
            "wizard/ar_unapplied_receipt_report_wizard.xml",
            "wizard/aging_report_detail_wizard.xml",
            "wizard/aging_report_summary_wizard.xml",



        ],
}
