from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ReportConfig(models.Model):
    _name = 'report.config'
    _description = 'Report Configuration'
    _rec_name = 'report_id'

    report_id = fields.Many2one('ir.actions.report', 'Report',
                                domain='[("model", "=", model]')
    is_idr = fields.Boolean('Is IDR', default=True)
    model = fields.Selection([
        ('account.payment', 'Payment'),
        ('purchase.order', 'Purchase Order'),
    ], 'Model', default='account.payment')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)  # DEPRECATED
    company_ids = fields.Many2many('res.company', string='Companies')
    journal_id = fields.Many2one('account.journal', 'Journal', check_company=False,
                                 domain='[("company_id", "in", company_ids)]')
    report_type = fields.Selection([
        ('manual', 'Manual'),
        ('check_printing', 'Check'),
        ('giro', 'Giro'),
    ], 'Report Type', default='manual')
    attachment_report_id = fields.Many2one(
        'ir.actions.report', 'Report', domain='[("model", "=", model]')

    @api.constrains('model', 'company_id', 'report_id', 'journal_id')
    def _check_company_report_journal(self):
        """ constrains function to check on unique data """
        # unique: company + report + journal + model
        for rec in self:
            # only valid for account.payment model
            if rec.model == 'account.payment':
                domain = [
                    ('id', '!=', rec.id),
                    ('model', '=', rec.model),
                    # ('report_id', '=', rec.report_id.id),
                    ('is_idr', '=', rec.is_idr),
                    ('journal_id', '=', rec.journal_id.id),
                    ('report_type', '=', rec.report_type),
                ]
                config = self.env['report.config'].search(domain)
                if config:
                    msg = 'Config with report %s and journal %s already exists'
                    raise ValidationError(msg % (rec.report_id.name, rec.journal_id.name))
