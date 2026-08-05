from odoo import models, tools, fields, api, _
from odoo.tools import consteq
from odoo.exceptions import UserError, ValidationError, AccessError
from uuid import uuid4


class ResApiKey(models.Model):
    _name = "res.api.key"

    name = fields.Char(required=True)
    key = fields.Char(
        required=True,
        help="""The API key. Enter a dummy value in this field if it is
        obtained from the server environment configuration.""",
        default= uuid4()
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        help="""The user used to process the requests authenticated by
        the api key""",
    )

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Api Key name must be unique.")
    ]

    @api.model
    def _retrieve_api_key(self, key):
        return self.browse(self._retrieve_api_key_id(key))
    
    def generate_token(self):
        self.key = uuid4()
    
    @api.model
    def _del_token_key(self, user_id):
        res = self.search([('user_id', '=', user_id)]).unlink()
        if res:
            return True
        else:
            return False
    
    @api.model
    def _retrieve_api_by_username(self, username):
        ada = False
        hasil = ''
        for api_key in self.sudo().search([]):
            if consteq(username, api_key.user_id.login):
                data = {'key': uuid4()}
                result = api_key.write(data)
                if result:
                    hasil = api_key.key
                else:
                    hasil = 'Invalid'
                ada = True
        if ada == False:
            users = self.env['res.users'].search([('login', '=', username)])
            if users:
                api_key = self.sudo().create({'name': username,'user_id': users.id, 'key': uuid4()})
                hasil = api_key.key
            else:
                hasil = 'Invalid'
        return hasil

    @api.model
    @tools.ormcache("key")
    def _retrieve_api_key_id(self, key):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("User is not allowed"))
        ada = False
        for api_key in self.search([]):
            if consteq(key, api_key.key):
                ada = True
                return api_key.id
        if ada == False:
            return False
            
    @api.model
    @tools.ormcache("key")
    def _retrieve_uid_from_api_key(self, key):
        return self._retrieve_api_key(key).user_id.id

    def _clear_key_cache(self):
        self._retrieve_api_key_id.clear_cache(self.env[self._name])
        self._retrieve_uid_from_api_key.clear_cache(self.env[self._name])

    @api.model
    def create(self, vals):
        record = super(ResApiKey, self).create(vals)
        if "key" in vals or "user_id" in vals:
            self._clear_key_cache()
        return record

    def write(self, vals):
        super(ResApiKey, self).write(vals)
        if "key" in vals or "user_id" in vals:
            self._clear_key_cache()
        return True
