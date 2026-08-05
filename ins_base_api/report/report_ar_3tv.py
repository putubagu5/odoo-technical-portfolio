from odoo import models, tools, fields, api, _


class ReportAr3tv(models.AbstractModel):
    _name = 'report.ins_base_api.report_ar_3tv_template_view'
    
    @api.model
    def _get_report_values(self, docids, data):
        docs = self.env['account.move'].browse(docids)
        data_dot_matrix = []
        for rec in docs:
            return_dot_matrix = {
                'line1': '',
                'line2': '',
                'line3': '',
                'line4': '',
                'line5': '',
                'line6': '',
                'line7': '',
                'line8': '',
                'line9': '',
                'line10': '',
                'line11': '',
                'line12': '',
                'line13': '',
                'line14': '',
                'line15': '',
                'line16': '',
                'line17': '',
                'line18': '',
                'line19': '',
                'line20': '',
            }
            if rec.partner_id.partner_no:
                return_dot_matrix['line1'] = return_dot_matrix['line1'].rjust(17)
                return_dot_matrix['line1'] = return_dot_matrix['line1'] + rec.partner_id.partner_no
                return_dot_matrix['line1'] = return_dot_matrix['line1'].ljust(63)
            else:
                return_dot_matrix['line1'] = return_dot_matrix['line1'].rjust(63)
            
            if rec.name:
                return_dot_matrix['line1'] = return_dot_matrix['line1'] + rec.name
            
            check_line_3 = False
            if rec.partner_id.name:
                name1 = ''
                name2 = ''
                name_split = rec.partner_id.name.split()
                is_name2 = False
                for text in name_split:
                    if len(name1 + text) < 43 and is_name2 == False:
                        name1 = name1 + text + ' '
                    elif len(name2 + text) < 43:
                        is_name2 = True
                        name2 = name2 + text + ' '
                if name1 != '':
                    return_dot_matrix['line2'] = return_dot_matrix['line2'].rjust(17)
                    return_dot_matrix['line2'] = return_dot_matrix['line2'] + name1
                    return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(63)
                else:
                    return_dot_matrix['line2'] = return_dot_matrix['line2'].rjust(63)
                if name2 != '':
                    return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(17)
                    return_dot_matrix['line3'] = return_dot_matrix['line3'] + name2
                    return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(63)
                    check_line_3 = True
            else:
                return_dot_matrix['line2'] = return_dot_matrix['line2'].rjust(63)
            
            if rec.invoice_date:
                return_dot_matrix['line2'] = return_dot_matrix['line2'] + rec.invoice_date.strftime('%d-%b-%Y')
            
            if check_line_3:
                if rec.partner_id.street and rec.partner_id.street2:
                    street_split = rec.partner_id.street + rec.partner_id.street2
                    street_split = street_split.split()
                    street1 = ''
                    street2 = ''
                    street3 = ''

                    is_street2 = False
                    is_street3 = False
                    for text in street_split:
                        if len(street1 + text) < 43 and is_street2 == False:
                            street1 = street1 + text + ' '
                        elif len(street2 + text) < 43 and is_street3 == False:
                            is_street2 = True
                            street2 = street2 + text + ' '
                        elif len(street3 + text) < 43:
                            is_street3 = True
                            street3 = street3 + text + ' '
                    
                    if street1 != '':
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(17)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'] + street1
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(63)

                    if street2 != '':
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(17)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'] + street2
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(63)
                    if street3 != '':
                        return_dot_matrix['line6'] = return_dot_matrix['line6'].rjust(17)
                        return_dot_matrix['line6'] = return_dot_matrix['line6'] + street3
                        return_dot_matrix['line6'] = return_dot_matrix['line6'].ljust(63)
                elif rec.partner_id.street:
                    street_split = rec.partner_id.street
                    street_split = street_split.split()
                    street1 = ''
                    street2 = ''
                    street3 = ''

                    is_street2 = False
                    is_street3 = False
                    for text in name_split:
                        if len(street1 + text) < 43 and is_street2 == False:
                            street1 = street1 + text + ' '
                        elif len(street2 + text) < 43 and is_street3 == False:
                            is_street2 = True
                            street2 = street2 + text + ' '
                        elif len(street3 + text) < 43:
                            is_street3 = True
                            street3 = street3 + text + ' '
                    
                    if street1 != '':
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(17)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'] + street1
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(63)

                    if street2 != '':
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(17)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'] + street2
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(63)
                    if street3 != '':
                        return_dot_matrix['line6'] = return_dot_matrix['line6'].rjust(17)
                        return_dot_matrix['line6'] = return_dot_matrix['line6'] + street3
                        return_dot_matrix['line6'] = return_dot_matrix['line6'].ljust(63)
                elif rec.partner_id.street2:
                    street_split = rec.partner_id.street2
                    street_split = street_split.split()
                    street1 = ''
                    street2 = ''
                    street3 = ''

                    is_street2 = False
                    is_street3 = False
                    for text in street_split:
                        if len(street1 + text) < 43 and is_street2 == False:
                            street1 = street1 + text + ' '
                        elif len(street2 + text) < 43 and is_street3 == False:
                            is_street2 = True
                            street2 = street2 + text + ' '
                        elif len(street3 + text) < 43:
                            is_street3 = True
                            street3 = street3 + text + ' '
                    
                    if street1 != '':
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(17)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'] + street1
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(63)

                    if street2 != '':
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(17)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'] + street2
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(63)
                    if street3 != '':
                        return_dot_matrix['line6'] = return_dot_matrix['line6'].rjust(17)
                        return_dot_matrix['line6'] = return_dot_matrix['line6'] + street3
                        return_dot_matrix['line6'] = return_dot_matrix['line6'].ljust(63)
                else:
                    return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(63)
            else:
                if rec.partner_id.street and rec.partner_id.street2:
                    street_split = rec.partner_id.street + rec.partner_id.street2
                    street_split = street_split.split()
                    street1 = ''
                    street2 = ''
                    street3 = ''

                    is_street2 = False
                    is_street3 = False
                    for text in street_split:
                        if len(street1 + text) < 43 and is_street2 == False:
                            street1 = street1 + text + ' '
                        elif len(street2 + text) < 43 and is_street3 == False:
                            is_street2 = True
                            street2 = street2 + text + ' '
                        elif len(street3 + text) < 43:
                            is_street3 = True
                            street3 = street3 + text + ' '
                    
                    if street1 != '':
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(17)
                        return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(63)

                    if street2 != '':
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(17)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(63)
                    if street3 != '':
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(17)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(63)
                elif rec.partner_id.street:
                    street_split = rec.partner_id.street
                    street_split = street_split.split()
                    street1 = ''
                    street2 = ''
                    street3 = ''

                    is_street2 = False
                    is_street3 = False
                    for text in street_split:
                        if len(street1 + text) < 43 and is_street2 == False:
                            street1 = street1 + text + ' '
                        elif len(street2 + text) < 43 and is_street3 == False:
                            is_street2 = True
                            street2 = street2 + text + ' '
                        elif len(street3 + text) < 43:
                            is_street3 = True
                            street3 = street3 + text + ' '
                    
                    if street1 != '':
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(17)
                        return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(63)

                    if street2 != '':
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(17)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(63)
                    if street3 != '':
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(17)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(63)
                elif rec.partner_id.street2:
                    street_split = rec.partner_id.street2
                    street_split = street_split.split()
                    street1 = ''
                    street2 = ''
                    street3 = ''

                    is_street2 = False
                    is_street3 = False
                    for text in street_split:
                        if len(street1 + text) < 43 and is_street2 == False:
                            street1 = street1 + text + ' '
                        elif len(street2 + text) < 43 and is_street3 == False:
                            is_street2 = True
                            street2 = street2 + text + ' '
                        elif len(street3 + text) < 43:
                            is_street3 = True
                            street3 = street3 + text + ' '
                    
                    if street1 != '':
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(17)
                        return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(63)

                    if street2 != '':
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(17)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(63)
                    if street3 != '':
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(17)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(63)
                else:
                    return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(63)
                
            if rec.mo_numbers_gen21:
                return_dot_matrix['line3'] = return_dot_matrix['line3'] + rec.mo_numbers_gen21
            
            if return_dot_matrix['line5'] == '':
                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(63)
            
            if rec.channel_name_gen21:
                return_dot_matrix['line5'] = return_dot_matrix['line5'] + rec.channel_name_gen21

            if rec.sales_person_gen21:
                return_dot_matrix['line6'] = return_dot_matrix['line6'].rjust(63)
                return_dot_matrix['line6'] = return_dot_matrix['line6'] + rec.sales_person_gen21
            
            if rec.operating_unit_id.name:
                return_dot_matrix['line7'] = return_dot_matrix['line7'].rjust(63)
                return_dot_matrix['line7'] = return_dot_matrix['line7'] + rec.operating_unit_id.name
            
            if rec.name_region_gen21:
                return_dot_matrix['line8'] = return_dot_matrix['line8'].rjust(17)
                return_dot_matrix['line8'] = return_dot_matrix['line8'] + rec.name_region_gen21
            
            if rec.invoice_line_ids[0].name:
                return_dot_matrix['line9'] = return_dot_matrix['line9'].rjust(6)
                return_dot_matrix['line9'] = return_dot_matrix['line9'] + 'PENAYANGAN PRODUCT ' + rec.invoice_line_ids[0].name
            
            if rec.ccid_gen21:
                return_dot_matrix['line10'] = return_dot_matrix['line10'].rjust(6)
                return_dot_matrix['line10'] = return_dot_matrix['line10'] + 'PERIODE BULAN ' + rec.ccid_gen21
            
            if rec.po_numbers_gen21:
                return_dot_matrix['line11'] = return_dot_matrix['line11'].rjust(6)
                return_dot_matrix['line11'] = return_dot_matrix['line11'] + 'NO PO  : ' + rec.po_numbers_gen21
            
            return_dot_matrix['line12'] = return_dot_matrix['line12'].rjust(39)
            return_dot_matrix['line12'] = return_dot_matrix['line12'] + 'TOTAL GROSS'

            if rec.invoice_line_ids[0].total_gross_gen21:
                txt_gross = "{:,}".format(rec.invoice_line_ids[0].total_gross_gen21)
                len_txt_gross = 39 + (25 - len(txt_gross)) + len("TOTAL GROSS")
                return_dot_matrix['line12'] = return_dot_matrix['line12'].ljust(len_txt_gross)
                return_dot_matrix['line12'] = return_dot_matrix['line12'] + txt_gross.replace('.0', '')
            else:
                return_dot_matrix['line12'] = return_dot_matrix['line12'].ljust(72)
                return_dot_matrix['line12'] = return_dot_matrix['line12'] + str(0)
                
            return_dot_matrix['line13'] = return_dot_matrix['line13'].rjust(39)
            return_dot_matrix['line13'] = return_dot_matrix['line13'] + 'AGENCY DISC'

            if rec.invoice_line_ids[0].agency_discount_gen21:
                agency_discount = rec.invoice_line_ids[0].total_gross_gen21 * (rec.invoice_line_ids[0].agency_discount_gen21 / 100)
                txt_agency = "{:,}".format(agency_discount)
                len_txt_agency = 39 + (25 - len(txt_agency)) + len("AGENCY DISC")
                return_dot_matrix['line13'] = return_dot_matrix['line13'].ljust(len_txt_agency)
                return_dot_matrix['line13'] = return_dot_matrix['line13'] + txt_agency.replace('.0', '')
            else:
                return_dot_matrix['line13'] = return_dot_matrix['line13'].ljust(72)
                return_dot_matrix['line13'] = return_dot_matrix['line13'] + str(0)
            
            return_dot_matrix['line14'] = return_dot_matrix['line14'].rjust(39)
            return_dot_matrix['line14'] = return_dot_matrix['line14'] + 'NETT AMOUNT'
            
            if rec.amount_untaxed:
                txt_amount_untaxed = "{:,}".format(rec.amount_untaxed)
                len_amount_untaxed = 39 + (25 - len(txt_amount_untaxed)) + len("NETT AMOUNT")
                return_dot_matrix['line14'] = return_dot_matrix['line14'].ljust(len_amount_untaxed)
                return_dot_matrix['line14'] = return_dot_matrix['line14'] + txt_amount_untaxed.replace('.0', '')
            else:
                return_dot_matrix['line14'] = return_dot_matrix['line14'].ljust(72)
                return_dot_matrix['line14'] = return_dot_matrix['line14'] + str(0)
            
            return_dot_matrix['line15'] = return_dot_matrix['line15'].rjust(39)
            return_dot_matrix['line15'] = return_dot_matrix['line15'] + 'VAT'
            
            tax = rec.get_tax_info()
            tax_amount = 0
            if tax:
                tax_amount = sum(taxes[1] for taxes in tax)
          
            if tax_amount:
                txt_tax_amount = "{:,}".format(tax_amount)
                len_tax_amount = 39 + (33 - len(txt_tax_amount)) + len("VAT")
                return_dot_matrix['line15'] = return_dot_matrix['line15'].ljust(len_tax_amount)
                return_dot_matrix['line15'] = return_dot_matrix['line15'] + txt_tax_amount.replace('.0', '')
            else:
                return_dot_matrix['line15'] = return_dot_matrix['line15'].ljust(72)
                return_dot_matrix['line15'] = return_dot_matrix['line15'] + str(0)
            
            if rec.invoice_date_due:
                return_dot_matrix['line16'] = return_dot_matrix['line16'].rjust(14)
                return_dot_matrix['line16'] = return_dot_matrix['line16'] + rec.invoice_date_due.strftime('%d-%b-%Y')
                return_dot_matrix['line16'] = return_dot_matrix['line16'].ljust(39)
            else:
                return_dot_matrix['line16'] = return_dot_matrix['line16'].rjust(39)
            
            return_dot_matrix['line16'] = return_dot_matrix['line16'] + 'TOTAL DUE'
            if rec.amount_total:
                txt_amount_total = "{:,}".format(rec.amount_total)
                len_amount_total = 39 + (27 - len(txt_amount_total)) + len("TOTAL DUE")
                return_dot_matrix['line16'] = return_dot_matrix['line16'].ljust(len_amount_total)
                return_dot_matrix['line16'] = return_dot_matrix['line16'] + txt_amount_total.replace('.0', '')
            else:
                return_dot_matrix['line16'] = return_dot_matrix['line16'].ljust(72)
                return_dot_matrix['line16'] = return_dot_matrix['line16'] + str(0)
            
            if rec.amount_due_in_words:
                amount_due_in_words = rec.amount_due_in_words
                amount_due_in_words = amount_due_in_words.split()
                amount_due_in_words1 = ''
                amount_due_in_words2 = ''

                is_amount_due_in_words2 = False
                for text in amount_due_in_words:
                    if len(amount_due_in_words1 + text) < 43 and is_amount_due_in_words2 == False:
                        amount_due_in_words1 = amount_due_in_words1 + text + ' '
                    elif len(amount_due_in_words2 + text) < 43:
                        is_amount_due_in_words2 = True
                        amount_due_in_words2 = amount_due_in_words2 + text + ' '
                
                if amount_due_in_words1 != '':
                    return_dot_matrix['line17'] = return_dot_matrix['line17'].rjust(14)
                    return_dot_matrix['line17'] = return_dot_matrix['line17'] + amount_due_in_words1
                    return_dot_matrix['line17'] = return_dot_matrix['line17'].ljust(73)

                if amount_due_in_words2 != '':
                    return_dot_matrix['line18'] = return_dot_matrix['line18'].rjust(14)
                    return_dot_matrix['line18'] = return_dot_matrix['line18'] + amount_due_in_words2
                    return_dot_matrix['line18'] = return_dot_matrix['line18'].ljust(73)
                
            return_dot_matrix['line19'] = return_dot_matrix['line19'].rjust(6)
            return_dot_matrix['line19'] = return_dot_matrix['line19'] + 'Please remit to    : ' + rec.company_id.name

            partner_remit = self.env['res.partner.remit'].search([('company_id', '=', rec.company_id.id), ('partner_ids', 'in', rec.partner_id.id)])
            txt_remit = ''
            if partner_remit:
                for remit in partner_remit:
                    if remit.bank_ids:
                        for bank in remit.bank_ids:
                            if bank.currency_id.id == rec.currency_id.id:
                                txt_remit += '      - ' + bank.bank_name + ', A/C ' + rec.currency_id.name + ' ' + bank.acc_number + '\n'
            return_dot_matrix['line20'] = txt_remit
            data_dot_matrix.append(return_dot_matrix)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'data_dot_matrix': data_dot_matrix
        }
