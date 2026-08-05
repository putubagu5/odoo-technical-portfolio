from odoo import api, fields, models, _

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    
    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.filtered(lambda r:r.is_reverse_budget == False).ids
            acc_reverse_budget_ids = line.general_budget_id.account_ids.filtered(lambda r:r.is_reverse_budget == True).ids
            date_to = line.date_to
            date_from = line.date_from
            # if line.analytic_account_id.id:
            #     analytic_line_obj = self.env['account.analytic.line']
            #     domain = [
            #         ('account_id', '=', line.analytic_account_id.id),
            #         ('date', '>=', date_from), ('date', '<=', date_to),
            #     ]
            #     if acc_ids:
            #         domain += [('general_account_id', 'in', acc_ids)]
            #
            #     where_query = analytic_line_obj._where_calc(domain)
            #     analytic_line_obj._apply_ir_rules(where_query, 'read')
            #     from_clause, where_clause, where_clause_params = where_query.get_sql()
            #     select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            # else:
            aml_obj = self.env['account.move.line']
            domain = [
                ('account_id', 'in', acc_ids),
                ('date', '>=', date_from), ('date', '<=', date_to),
                ('move_id.state', '=', 'posted'),
                ('analytic_account_id','=', line.analytic_account_id.id)
            ]
            where_query = aml_obj._where_calc(domain)
            aml_obj._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            practical_amount = self.env.cr.fetchone()[0] or 0.0
            if practical_amount < 0.0 and line.general_budget_id.budget_type == 'abs':
                practical_amount = -practical_amount

            if acc_reverse_budget_ids:
                budget_domain = domain = [
                ('account_id', 'in', acc_reverse_budget_ids),
                ('date', '>=', date_from), ('date', '<=', date_to),
                ('move_id.state', '=', 'posted'),
                ('analytic_account_id','=', line.analytic_account_id.id)
                ]
                where_query = aml_obj._where_calc(budget_domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(debit)-sum(credit) from " + from_clause + " where " + where_clause

                self.env.cr.execute(select, where_clause_params)
                budget_amount = self.env.cr.fetchone()[0] or 0.0

                practical_amount = practical_amount - budget_amount
            line.practical_amount = practical_amount
            
    def _compute_total_reserve_remaining(self):
        for record in self:
            pr_lines = record.purchase_request_ids.filtered(
                lambda pr: pr.request_state in ['to_approve', 'approved', 'done'])
            pr_reserved_amount = 0.0
            for prs_line in pr_lines:
                if not prs_line.purchase_lines.ids:
                    pr_reserved_amount += prs_line.estimated_cost
                else:
                    for po_line in prs_line.purchase_lines:
                        if po_line.order_id.state in ['draft', 'cancel']:
                            estimated_amount = po_line.product_qty * po_line.price_unit
                            pr_reserved_amount += estimated_amount

            po_lines = record.purchase_request_ids.filtered(
                lambda pr: pr.request_state in ['approved', 'done']
            )
            po_reserved_amount = 0.0
            for pr_line in po_lines:
                for po_line in pr_line.purchase_lines:
                    price_subtotal = 0.0
                    if po_line.order_id.state == 'to approve':
                        price_subtotal = po_line.product_qty * po_line.price_unit
                    elif po_line.order_id.state == 'purchase':
                        quantity_balance = po_line.product_qty - po_line.qty_received
                        price_subtotal = quantity_balance * po_line.price_unit

                    po_reserved_amount += price_subtotal

            acc_reverse_budget_ids = record.general_budget_id.account_ids.filtered(lambda r:r.is_reverse_budget == True).ids
            if acc_reverse_budget_ids:
                residual_amount = record.planned_amount - pr_reserved_amount - po_reserved_amount - record.practical_amount
            else:
                residual_amount = record.planned_amount - pr_reserved_amount - po_reserved_amount + record.practical_amount
            record.pr_reserve_amount = pr_reserved_amount
            record.po_reserve_amount = po_reserved_amount
            record.remaining_amount = residual_amount
