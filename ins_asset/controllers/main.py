from odoo import http
from odoo.http import content_disposition, request


class ReportController(http.Controller):
    @http.route('/xls_report/<string:model>/<int:mid>/<string:r_name>',
                type='http', auth='user')
    def get_xlsx_report(self, model, mid, r_name, **kwargs):
        uid = request.session.uid
        obj = request.env[model].with_user(uid).browse(mid)
        response = request.make_response(None, headers=[
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Disposition', content_disposition(r_name + '.xlsx'))
        ])
        data = obj._prepare_report_data()
        obj.get_xlsx(response, data)
        return response
