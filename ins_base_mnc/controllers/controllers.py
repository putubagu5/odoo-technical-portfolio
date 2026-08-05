# -*- coding: utf-8 -*-

import zlib
from base64 import urlsafe_b64decode as b64d

from odoo import http


class PurchaseRequestApproval(http.Controller):
    def _unobscure_param(self, obscured: bytes) -> bytes:
        return zlib.decompress(b64d(obscured))

    @http.route('/approve-purchase-request/<string:param>', auth='public', website=True)
    def approve_purchase_request(self, **kw):
        context = {
            'status': 404,
            'message': "The Purchase Request you are looking for was not found."
        }

        param = kw.get('param', False)
        if not param:
            return http.request.render('ins_base_mnc.purchase_request_approval_web', context)

        unobscured_param = self._unobscure_param(kw['param'])
        splitted_unobscured_param = unobscured_param.split(b'/')
        if not splitted_unobscured_param or len(splitted_unobscured_param) < 2:
            return http.request.render('ins_base_mnc.purchase_request_approval_web', context)

        document_id = splitted_unobscured_param[0]
        user_id = splitted_unobscured_param[1]

        pr_id = http.request.env['purchase.request'].browse(int(document_id))
        if pr_id:
            pr_id.with_user(int(user_id)).button_approved()
            context['status'] = 200
            context['message'] = "Purchase Request {} has been approved.".format(pr_id.name)
            return http.request.render('ins_base_mnc.purchase_request_approval_web', context)

        return http.request.render('ins_base_mnc.purchase_request_approval_web', context)
