from datetime import date
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WizardCoverNote(models.TransientModel):
    _name = 'wizard.cover.note'
    _description = 'Cover Note Report'
    
    move_ids = fields.Many2many('account.move')
    
    @api.model
    def default_get(self, fields_list):
        vals = super(WizardCoverNote, self).default_get(fields_list)
        move_ids = self._context.get('active_ids')
        vals['move_ids'] = move_ids
        return vals

    def generate(self):
        report = self.env['ir.actions.report'].sudo().search(
            [('report_name', '=', 'ins_base_mnc.cover_note_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1)
        data = {
            'move_ids': self._context.get('active_ids')
        }
        return report.report_action(self)
