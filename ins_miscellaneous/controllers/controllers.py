# -*- coding: utf-8 -*-
# from odoo import http


# class InsMiscReceipt(http.Controller):
#     @http.route('/ins_misc_receipt/ins_misc_receipt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ins_misc_receipt/ins_misc_receipt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ins_misc_receipt.listing', {
#             'root': '/ins_misc_receipt/ins_misc_receipt',
#             'objects': http.request.env['ins_misc_receipt.ins_misc_receipt'].search([]),
#         })

#     @http.route('/ins_misc_receipt/ins_misc_receipt/objects/<model("ins_misc_receipt.ins_misc_receipt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ins_misc_receipt.object', {
#             'object': obj
#         })
