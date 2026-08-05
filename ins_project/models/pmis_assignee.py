from odoo import api, fields, models
from odoo.exceptions import Warning


class PmisAssigneeLine(models.Model):
    _name = 'pmis.assignee.line'
    _description = 'PMIS Assignee Line'
    _order = 'sign_id, sequence, id'

    emp_position = fields.Char('Position')
    emp_name = fields.Char('Employee Name')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')
    department_type_id = fields.Many2one(
        'pmis.departement.type', 'Department Type')
    seq = fields.Integer('Sequence')
    sign_id = fields.Many2one('pmis.assignee', 'Assignee ID',
                              ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    # @api.constrains('seq')
    # def _check_code(self):
    #     """ constrains function to check sequence duplicate """
    #     for rec in self:
    #         domain = [
    #             ('seq', '=ilike', self.seq),
    #             ('analytic_account_id', '=', self.analytic_account_id.id),
    #             ('id', '!=', self.id),
    #             ('sign_id', '=', rec.sign_id.id),
    #         ]
    #         line = self.search(domain)
    #         if line:
    #             raise Warning('Duplicate Sequence per analytic account!')

    # @api.depends('sign_id.sign_ids')
    # def _compute_sequence(self):
    #     """ compute function to get sequence """
    #     for rec in self:
    #         no = 0
    #         rec.seq = no
    #         for l in rec.sign_id.sign_ids:
    #             no += 1
    #             l.seq = no


class PmisAssignee(models.Model):
    _name = 'pmis.assignee'
    _description = 'PMIS Assignee'

    # position = fields.Char('Position')
    name = fields.Char('Name')
    report_id = fields.Many2one('ir.actions.report', 'Report')
    model = fields.Selection([
        ('pmis.budget', 'PMIS Budget'),
    ], 'Model', default='pmis.budget')
    company_line_id = fields.Many2one('res.company', 'Company',
                                      default=lambda self: self.env.company)
    sign_ids = fields.One2many(
        'pmis.assignee.line',
        'sign_id',
        string="Signatures")

    @api.model
    def create(self, vals):
        if vals.get('sign_ids', []):  # check if sign_ids exist
            lines = vals.get('sign_ids', [])  # loop and assign line_number
            for idx, line in enumerate(lines):
                line[2]['seq'] = idx + 1
        res = super(PmisAssignee, self).create(vals)
        return res

    def write(self, vals):
        """ inherit function to rewrite seq """
        # find order_line, rewrite the seq
        res = super(PmisAssignee, self).write(vals)
        for idx, line in enumerate(self.sign_ids):
            line.seq = idx + 1
        return res
