# -*- coding: utf-8 -*-
# from odoo import http


# class MncFznReporting(http.Controller):
#     @http.route('/mnc_fzn_reporting/mnc_fzn_reporting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mnc_fzn_reporting/mnc_fzn_reporting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mnc_fzn_reporting.listing', {
#             'root': '/mnc_fzn_reporting/mnc_fzn_reporting',
#             'objects': http.request.env['mnc_fzn_reporting.mnc_fzn_reporting'].search([]),
#         })

#     @http.route('/mnc_fzn_reporting/mnc_fzn_reporting/objects/<model("mnc_fzn_reporting.mnc_fzn_reporting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mnc_fzn_reporting.object', {
#             'object': obj
#         })
