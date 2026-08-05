from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.web.controllers.main import Home, ensure_db


class Home(Home, http.Controller):
    @http.route('/web', type='http', auth='none')
    def web_client(self, s_action=None, **kw):
        ensure_db()
        user_obj = request.env['res.users'].with_user(SUPERUSER_ID)
        cond1 = request.env.user.id != request.env.ref('base.user_admin')
        logged_user = user_obj.browse(request.session.uid)
        cond2 = not logged_user.has_group('ins_base_mnc.group_forbidden')
        if 'debug' in kw and cond1 and cond2:
            request.session.debug = ''  # empty out the debug session
            return http.redirect_with_hash('/web')

        return super(Home, self).web_client(s_action=s_action, **kw)

