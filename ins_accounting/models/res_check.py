import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCheck(models.Model):
    _name = 'res.check'
    _description = 'Check'

    name = fields.Char('Serial', copy=False)
    code = fields.Char('Code', copy=False)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', 'Journal', check_company=True)
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account',
                                      related='journal_id.bank_account_id')
    start = fields.Char('Start')
    end = fields.Char('End')
    series = fields.Char('Series')
    line_ids = fields.One2many('res.check.line', 'check_id', 'Used Checks')

    @api.constrains('start', 'end')
    def _check_start_end(self):
        """ constrains to check if length of start and end is same """
        self.ensure_one()
        # check if length is same
        if len(self.start) != len(self.end):
            raise ValidationError('Start and End must have the same length')

        # check if start and end are integers
        pattern = r"\d+$"
        if not re.match(pattern, self.start) or not re.match(pattern, self.end):
            raise ValidationError('Start/End must contain only number')

        # if all are numbers, start must be <= end
        start = int(self.start)
        end = int(self.end)
        if start > end:
            raise ValidationError('Start sequence must be lesser than End')

    @api.constrains('name', 'journal_id')
    def _check_name_journal_id(self):
        """ constrains to check duplicate of record with same name & journal """
        self.ensure_one()
        # find all other records with the same serial and journal_id
        domain = [
            ('id', '!=', self.id),
            ('name', 'ilike', self.name),
            ('journal_id', '=', self.journal_id.id),
        ]
        existing = self.env['res.check'].search_count(domain)
        if existing:
            msg = 'Serial %s with journal %s already exists'
            raise ValidationError(msg % (self.name, self.journal_id.name))

    @api.onchange('code', 'start')
    def _onchange_code_start(self):
        """ onchange function to change series based on code and start """
        self.ensure_one()
        self.series = '%s%s' % (self.code or '', self.start or '')

    def button_generate(self):
        """ function to generate check numbers based on range """

        start = self.start
        end = self.end
        prefix = self.name
        pad = len(start)

        # add existing names
        names = [x.name for x in self.line_ids]

        # clear but re-add existing
        lines = [(5, 0, 0)]
        lines += [(4, x.id) for x in self.line_ids]
        for x in range(int(start), int(end) + 1):
            # name = '%s %s' % (prefix, str(x).zfill(pad))
            name = '%s' % (str(x).zfill(pad))
            if name in names:
                raise ValidationError('Number is already generated!')

            data = {'name': name, 'series': self.series}
            lines.append((0, 0, data))
        self.line_ids = lines

        return True
