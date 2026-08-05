# -*- coding: utf-8 -*-
# from odoo import http


# class ApBudgetControl(http.Controller):
#     @http.route('/budget_control/budget_control/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/budget_control/budget_control/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('budget_control.listing', {
#             'root': '/budget_control/budget_control',
#             'objects': http.request.env['budget_control.budget_control'].search([]),
#         })

#     @http.route('/budget_control/budget_control/objects/<model("budget_control.budget_control"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('budget_control.object', {
#             'object': obj
#         })
