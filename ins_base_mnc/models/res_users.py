from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def analytic_default_get(self, uid2=False):
        if not uid2:
            uid2 = self._uid
        user = self.env['res.users'].browse(uid2)
        return user.default_account_analytic_id

    @api.model
    def _default_analytic(self):
        return self.analytic_default_get()

    @api.model
    def _default_analytics(self):
        return self._default_analytic()

    select_all_units = fields.Boolean('Select All Units', default=True)
    select_all_analytics = fields.Boolean('Select All Cost Centers', default=True)
    buyer_ids = fields.Many2many('res.buyer', string='Buyer Types')
    location_ids = fields.Many2many('stock.location', string='Locations')
    default_account_analytic_id = fields.Many2one(
        'account.analytic.account', 'Default Cost Center',
        default=lambda self: self._default_analytic())
    account_analytic_ids = fields.Many2many('account.analytic.account',
                                            'user_analytic_rel', 'user_id',
                                            'analytic_id', string='Cost Centers')
    assigned_account_analytic_ids = fields.Many2many(
        'account.analytic.account', 'assign_user_analytic_rel', 'user_id',
        'analytic_id', default=lambda self: self._default_analytics())
    # id_users = fields.Integer('ID Users', copy=False)
    # code_gen21 = fields.Char('Code Gen21')

    @api.depends('groups_id', 'assigned_account_analytic_ids')
    def _compute_account_analytic_ids(self):
        """ compute function to get account analytic """
        for rec in self:
            if rec.has_group('analytic.group_analytic_accounting'):
                domain = []
                if self.env.context.get('allowed_company_ids'):
                    domain = [
                        '|',
                        ('company_id', '=', False),
                        ('company_id', 'in', self.env.context['allowed_company_ids']),
                    ]
                rec.account_analytic_ids = self.env['account.analytic.account'].sudo().search(domain)
            else:
                rec.account_analytic_ids = rec.assigned_account_analytic_ids

    def _inverse_account_analytic_ids(self):
        """ inverse function to set account analytic """
        for rec in self:
            rec.assigned_account_analytic_ids = rec.account_analytic_ids

    def write(self, vals):
        """ inherit function to clear rule cache """
        # self.env['ir.rule'].clear_cache()
        res = super(ResUsers, self).write(vals)
        return res

    @api.onchange('select_all_units')
    def _onchange_select_all_units(self):
        """ onchange function to select or empty out all units """
        self.ensure_one()
        if not self.select_all_units:  # make sure all empty
            lines = [(3, x.id) for x in self.operating_unit_ids]
            self.operating_unit_ids = lines
        else:  # proceed to take base on user group
            if self.has_group('operating_unit.group_manager_operating_unit'):
                domain = []
                if self.env.context.get('allowed_company_ids'):
                    domain = [
                        '|',
                        ('company_id', '=', False),
                        ('company_id', 'in', self.env.context['allowed_company_ids']),
                    ]
                self.operating_unit_ids = self.env['operating.unit'].sudo().search(domain)
            else:
                self.operating_unit_ids = self.assigned_operating_unit_ids

    @api.onchange('select_all_analytics')
    def _onchange_select_all_analytics(self):
        """ onchange function to select or empty out all analytics """
        self.ensure_one()
        if not self.select_all_analytics:  # make sure all empty
            lines = [(3, x.id) for x in self.account_analytic_ids]
            self.account_analytic_ids = lines
        else:  # proceed to take base on user group
            if self.has_group('analytic.group_analytic_accounting'):
                domain = []
                if self.env.context.get('allowed_company_ids'):
                    domain = [
                        '|',
                        ('company_id', '=', False),
                        ('company_id', 'in', self.env.context['allowed_company_ids']),
                    ]
                self.account_analytic_ids = self.env['account.analytic.account'].sudo().search(domain)
            else:
                self.account_analytic_ids = self.assigned_account_analytic_ids
