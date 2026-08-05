from odoo import http
from odoo.http import content_disposition, request


class CsvReportController(http.Controller):
    @http.route('/efaktur/<string:model>/<int:mid>/<string:r_name>', auth='user', type='http')
    def get_csv_report(self, model, mid, r_name, **kwargs):
        uid = request.session.uid  # get uid
        report = request.env[model].with_user(uid).browse(mid)  # find model
        data = report.get_csv()  # get data in bytes
        # pass data to response
        response = request.make_response(data, headers=[
            ('Content-Type', 'text/csv'),
            ('Content-Disposition', content_disposition(r_name + '.csv'))
        ])
        return response

    @http.route('/efaktur_multi/<string:model>/<int:mid>/<string:r_name>/<string:sids>', auth='user', type='http')
    def get_csv_report_multi(self, model, mid, r_name, sids, **kwargs):
        uid = request.session.uid  # get uid
        report = request.env[model].with_user(uid).browse(mid)  # find model
        header = report._generate_headers()
        title = report._generate_titles()
        data = report.with_context({'enc_ids': sids})._prepare_report_data()  # get data in bytes
        response = report.get_csv(header, title, data)
        # pass data to response
        response = request.make_response(response, headers=[
            ('Content-Type', 'text/csv'),
            ('Content-Disposition', content_disposition(r_name + '.csv'))
        ])
        return response
