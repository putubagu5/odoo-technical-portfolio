import base64
import io
import xlsxwriter
import os
from odoo import fields, models, api, tools
from odoo.exceptions import UserError, ValidationError


class cash_flow_xlsx_report(models.TransientModel):
    _name = 'cash.flow.report'
    _rec_name = 'filename'

    xls_file = fields.Binary('XLS Report', filters='.xls',
                             readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('all', 'All'),
    ], 'Status')
    date = fields.Date(string='Transfer Date', required=True, index=True,
                       copy=False, default=fields.Datetime.now)
    selected_period_id = fields.Many2one('account.period', 'Current Periods')
    selected_date_start = fields.Date('Start of Period', related='selected_period_id.date_start')
    selected_date_stop = fields.Date('End of Period', related='selected_period_id.date_stop')
    comparison_period_id = fields.Many2one('account.period', 'Comparison Periods')
    comparison_date_start = fields.Date('Start of Period', related='comparison_period_id.date_start')
    comparison_date_stop = fields.Date('End of Period', related='comparison_period_id.date_stop')
    filename = fields.Char('File Name')
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'cashflow_report')
        self.env.cr.execute("""
                CREATE OR REPLACE VIEW cashflow_report as (
                select	case when ap.payment_type = 'inbound' then '+' end as value, 
                        sum(ap.amount) as amount, 
                        coalesce(ca.name,'Null'::character varying) as activity_name,
                        coalesce(cac.name,'Null'::character varying) as activity_category, 
                        am.state, am.date,
                        am.company_id as company_id
                from  cashflow_activity_category cac
                join  cashflow_activity ca
                  on  cac.id = ca.cf_category_id
                left join account_payment ap
                  on  ca.id = ap.cf_activity_id
                 and  ap.payment_type = 'inbound'
                 and ap.journal_id in (select id from account_journal where exclude_cf_report = coalesce(null,False))
                 and ap.is_matched = true 
                left join  account_move am
                  on  ap.move_id = am.id
                 and  am.company_id = ca.company_id
                group by ca.name, ap.payment_type, cac.name,am.state, am.date, am.company_id
                union 
                select	case when ap.payment_type = 'outbound' then '-' end as value, 
                        sum(ap.amount) * -1 as amount, 
                        coalesce(ca.name,'Null'::character varying) as activity_name,
                        coalesce(cac.name,'Null'::character varying) as activity_category, 
                        am.state, am.date,
                        am.company_id as company_id
                from  cashflow_activity_category cac
                join  cashflow_activity ca
                  on  cac.id = ca.cf_category_id 
                left join account_payment ap
                  on  ap.cf_activity_id = ca.id
                 and  ap.payment_type = 'outbound'
                 and ap.journal_id in (select id from account_journal where exclude_cf_report = coalesce(null,False))
                 and ap.is_matched = true 
                left join  account_move am
                  on  ap.move_id = am.id
                 and  am.company_id = ca.company_id
                group by ca.name, ap.payment_type, cac.name, am.state, am.date, am.company_id
                union
                select	case when mm.misc_type = 'payment' then '-' end as value, 
                        sum(mm.amount) * -1 as amount, 
                        coalesce(ca.name,'Null'::character varying) as activity_name,
                        coalesce(cac.name,'Null'::character varying) as activity_category,
                        am.state, am.date,
                        am.company_id as company_id
                from  cashflow_activity_category cac 
                join  cashflow_activity ca
                  on  cac.id = ca.cf_category_id
                left join miscellaneous_miscellaneous mm
                  on  mm.cf_activity_id = ca.id
                 and  mm.company_id = ca.company_id
                 and  mm.misc_type = 'payment'
                 and  mm.journal_id in (select id from account_journal where exclude_cf_report = coalesce(null,False))
                 and mm.is_matched = true
                left join  account_move am
                  on  mm.move_id = am.id
                 and  am.company_id = ca.company_id
                 group by ca.name, mm.misc_type, cac.name, am.state, am.date, am.company_id
                union
                select	case when mm.misc_type = 'receive' then '+' end as value, 
                        sum(mm.amount) as amount, 
                        coalesce(ca.name,'Null'::character varying) as activity_name,
                        coalesce(cac.name,'Null'::character varying) as activity_category,
                        am.state, am.date,
                        am.company_id as company_id
                from  cashflow_activity_category cac 
                join  cashflow_activity ca
                  on  cac.id = ca.cf_category_id
                left join miscellaneous_miscellaneous mm
                  on  mm.cf_activity_id = ca.id
                 and  mm.company_id = ca.company_id
                 and  mm.misc_type = 'receive'
                 and  mm.journal_id in (select id from account_journal where exclude_cf_report = coalesce(null,False))
                 and mm.is_matched = true
                left join  account_move am
                  on  mm.move_id = am.id
                 and  am.company_id = ca.company_id
                 group by ca.name, mm.misc_type, cac.name,am.state, am.date, am.company_id
                order by 1 asc
                )
               """)

    def create_cashflow_xlsx_report(self):
        params = self.env.company.id
        param_state = (self.state)
        param_start_date = self.selected_date_start
        param_end_date = self.selected_date_stop
        print(type(param_start_date), param_start_date)
        if params:
            header = [
                'Sign',  # a
                'Activity Category',  # b
                'Activity Name',  # c
                'Amount',  # d
                'state',  # e
            ]  #

            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': True, 'border': 1})
            main_title = workbook.add_format({
                'bold': True,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter', })
            worksheet.merge_range('A1:D2', 'Cash Flow Report', main_title)
            row = 3
            for col in range(0, len(header)):
                worksheet.write(row, col, header[col], bold)
            query = """
                        select	value, activity_name, activity_category, sum(amount) as amount
                        from	cashflow_report
                        where	company_id = %s
                          and   date >= '%s' and date <= '%s'
                          and   (case 
                                    when '%s' in ('posted', 'draft') 
                                        then state = '%s'
                                    when '%s' = 'all'
                                        then state in ('posted', 'draft') 
                                 end
                                )
                        group by value, activity_name, activity_category
                        union
                        select 	'Total' as value, null as activity_name, null as activity_category, 
                                a.amount as amount
                        from	(select	sum(amount) as amount
                                from	cashflow_report
                                where	company_id = %s
                                  and   date >= '%s' and date <= '%s'
                                  and   (case 
                                            when '%s' in ('posted', 'draft') 
                                                then state = '%s'
                                            when '%s' = 'all'
                                                then state in ('posted', 'draft')
                                        end
                                        )
                                 ) as a
                        order by value asc
                    """ % (params, param_start_date, param_end_date, param_state, param_state, param_state,
                           params, param_start_date, param_end_date, param_state, param_state, param_state)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
            for line in result:
                row += 1
                worksheet.write(row, 0, line['value'])
                worksheet.write(row, 1, line['activity_category'])
                worksheet.write(row, 2, line['activity_name'])
                worksheet.write(row, 3, line['amount'])
                # worksheet.write(row, 4, line['state'])

            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 20)
            # worksheet.set_column('E:E', 10)
            workbook.close()
            output.seek(0)
            out = base64.encodestring(output.getvalue())
            tmp = 'Cash Flow Report.xls'
            self.write({
                'xls_file': out,
                'filename': '%s.xls' % tmp
            })
            output.close()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'cash.flow.report',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'current',
                'name': 'Cash FLow Report.xls'
            }
