from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class AccountTransactionType(models.Model):
    _name = 'account.transaction.type'
    _description = 'Transaction Type'

    name = fields.Char('Name', copy=False)
    description = fields.Char('Description', copy=False)
    account_id = fields.Many2one('account.account', 'Account',
                                 help='Replaces customer invoice debit account',
                                 domain='[("user_type_id.type", "=", "receivable")]')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id.id)

    def name_get(self):
        result = []
        if self.env.context.get('show_view_search_more_transaction_type'):
            for record in self:
                if record.name and record.description:
                    data = str(record.name) + " - " + str(record.description)
                    result.append((record.id, data))
                if record.name and not record.description:
                    result.append((record.id, record.name))
            return result
        else:
            return super(AccountTransactionType, self).name_get()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """ inherit function to make able to search """
        args = args or []
        domain = []
        if name:
            parts = name.split('-')
            if len(parts) == 2:
                domain = ['|', ('name', operator, parts[0]), ('description', operator, parts[1])]
            else:
                domain = ['|', ('name', operator, name), ('description', operator, name)]

        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.constrains('name')
    def _check_name(self):
        """ constrains function to check on name uniqueness """
        for rec in self:
            domain = [
                ('name', '=ilike', rec.name),
                ('id', '!=', rec.id),
                ('company_id', '=', rec.company_id.id),
            ]
            exists = self.env['account.transaction.type'].search(domain)
            if exists:
                raise ValidationError('Transaction Type already exists')
