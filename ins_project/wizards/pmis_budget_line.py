from odoo import api, fields, models
from odoo.exceptions import Warning


class WizardPmisBudgetLine(models.TransientModel):
    _name = 'wizard.pmis.budget.line'
    _description = 'PMIS Budget Line Wizard'

    line_id = fields.Many2one('pmis.budget.line', 'Related Line')
    detail_ids = fields.One2many('wizard.pmis.budget.detail', 'line_id', 'Details')

    def _check_lines(self):
        """ helper function to check lines """
        if self.line_id.budget != sum(self.detail_ids.mapped('amount')):
            raise Warning('Budget Amount is not equal with the total!')

        if len(self.detail_ids) > self.line_id.line_id.episode_number:
            raise Warning('Episode is only %d!' % self.line_id.line_id.episode_number)

    def button_save(self):
        """ function to save to line_id """
        self.ensure_one()
        self._check_lines()
        lines = [(2, x.id) for x in self.line_id.detail_ids]
        for line in self.detail_ids:
            data = {
                'code': line.code,
                'name': line.name,
                'no': line.no,
                'amount': line.amount,
            }
            lines.append((0, 0, data))
        self.line_id.detail_ids = lines


class WizardPmisBudgetDetail(models.TransientModel):
    _name = 'wizard.pmis.budget.detail'
    _description = 'Wizard Budget Detail'

    line_id = fields.Many2one('wizard.pmis.budget.line', 'Related Line', ondelete='cascade')
    no = fields.Integer('Episode No')
    name = fields.Char('Episode Name')
    code = fields.Char('Episode Code')
    amount = fields.Float('Amount')
