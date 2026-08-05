from odoo import models, tools, fields, api, _
import datetime


class ReportAr3tvTxtNew(models.AbstractModel):
    _name = 'report.ins_base_api.report_ar_3tv_txt_new_template_view'
    
    def _get_beetween_signature(self, name):
        if len(name) > 39:
            sisa = len(name) - 39
            sisa = sisa / 2
            result = 40 - int(sisa)
            return result
        elif len(name) == 39:
            result = 40
            return result
        else:
            sisa = 39 - len(name)
            sisa = sisa / 2
            result = 40 + int(sisa)
            return result
        
    @api.model
    def _get_report_values(self, docids, data):
        docs = self.env['account.move'].browse(docids)
        data_dot_matrix = []
        number_page = 0
        for rec in docs:
            number_page += 1
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
                'line21': '',
                'line22': '',
                'line23': '',
                'line24': '',
                'ar_receipt_type': 'non_iklan',
                'source_type_gen21': 'manual',
                'manual_desc': '',
                'narration': '',
                'signature_name_margin': '',
                'signature_position_margin': '',
                'signature_position': '',
                'signature_name': '',
                'is_gross': False
            }    
            data_dot_matrix.append(return_dot_matrix)
            if rec.assignee_id_invoice:
                if rec.assignee_id_invoice.job_position:
                    if "&" in rec.assignee_id_invoice.job_position:
                        margin_right = self._get_beetween_signature(rec.assignee_id_invoice.job_position)
                        return_dot_matrix['signature_position_margin'] = return_dot_matrix['signature_position_margin'].rjust(margin_right - 2)
                        return_dot_matrix['signature_position'] = rec.assignee_id_invoice.job_position.replace("&", "And")
                    else:
                        margin_right = self._get_beetween_signature(rec.assignee_id_invoice.job_position)
                        return_dot_matrix['signature_position_margin'] = return_dot_matrix['signature_position_margin'].rjust(margin_right - 2)
                        return_dot_matrix['signature_position'] = rec.assignee_id_invoice.job_position
                
                if rec.assignee_id_invoice.name:
                    if "&" in rec.assignee_id_invoice.name:
                        margin_right = self._get_beetween_signature(rec.assignee_id_invoice.name)
                        return_dot_matrix['signature_name_margin'] = return_dot_matrix['signature_name_margin'].rjust(margin_right)                        
                        return_dot_matrix['signature_name'] = rec.assignee_id_invoice.name.replace("&", "And")
                    else:
                        margin_right = self._get_beetween_signature(rec.assignee_id_invoice.name)
                        return_dot_matrix['signature_name_margin'] = return_dot_matrix['signature_name_margin'].rjust(margin_right)
                        return_dot_matrix['signature_name'] = rec.assignee_id_invoice.name

            return_dot_matrix['line1'] = 'Bill To   : '
            if rec.partner_id.alias_name:
                name_split = rec.partner_id.alias_name.split()
                name1 = ''
                name2 = ''
                is_name2 = False
                
                for text in name_split:
                    if len(name1 + text) < 31 and is_name2 == False:
                        name1 = name1 + text + ' '
                    elif len(name2 + text) < 31:
                        is_name2 = True
                        name2 = name2 + text + ' '
                if name1 != '':
                    if "&" in name1:
                        name1 = name1.replace("&", "And")
                    return_dot_matrix['line1'] = 'Bill To   : ' + name1
                    return_dot_matrix['line1'] = return_dot_matrix['line1'].ljust(44)
                
                if name2 != '':
                    if "&" in name2:
                        name2 = name2.replace("&", "And")
                    return_dot_matrix['line2'] = return_dot_matrix['line2'].rjust(12)
                    return_dot_matrix['line2'] = return_dot_matrix['line2'] + name2
                    return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
            else:
                return_dot_matrix['line1'] = return_dot_matrix['line1'].ljust(44)

            return_dot_matrix['line1'] = return_dot_matrix['line1'] + 'Invoice No   : '
            if rec.name:
                return_dot_matrix['line1'] = return_dot_matrix['line1'] + rec.payment_reference
            
            if rec.sites_id:
                if return_dot_matrix['line2'] != '':
                    return_dot_matrix['line3'] = 'Address   : '
                    if rec.sites_id.site_address:
                        street_split = rec.sites_id.site_address
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        
                        if street1 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                            return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                        else:
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                    else:
                        if rec.partner_id.street and rec.partner_id.street2:
                            street_split = rec.partner_id.street + rec.partner_id.street2
                            street_split = street_split.split()
                            street1 = ''
                            street2 = ''
                            street3 = ''
                            street4 = ''
                            street5 = ''

                            is_street2 = False
                            is_street3 = False
                            is_street4 = False
                            is_street5 = False
                            for text in street_split:
                                if len(street1 + text) < 31 and is_street2 == False:
                                    street1 = street1 + text + ' '
                                elif len(street2 + text) < 31 and is_street3 == False:
                                    is_street2 = True
                                    street2 = street2 + text + ' '
                                elif len(street3 + text) < 31 and is_street4 == False:
                                    is_street3 = True
                                    street3 = street3 + text + ' '
                                elif len(street4 + text) < 31 and is_street5 == False:
                                    is_street4 = True
                                    street4 = street4 + text + ' '
                                elif len(street5 + text) < 31:
                                    is_street5 = True
                                    street5 = street5 + text + ' '
                            
                            if street1 != '':
                                return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            else:
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                            if street2 != '':
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                                return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            else:
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            if street3 != '':
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                                return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            else:
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            if street4 != '':
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                                return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            else:
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            if street5 != '':
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                                return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                            else:
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                        elif rec.partner_id.street:
                            street_split = rec.partner_id.street
                            street_split = street_split.split()
                            street1 = ''
                            street2 = ''
                            street3 = ''
                            street4 = ''
                            street5 = ''

                            is_street2 = False
                            is_street3 = False
                            is_street4 = False
                            is_street5 = False
                            for text in street_split:
                                if len(street1 + text) < 31 and is_street2 == False:
                                    street1 = street1 + text + ' '
                                elif len(street2 + text) < 31 and is_street3 == False:
                                    is_street2 = True
                                    street2 = street2 + text + ' '
                                elif len(street3 + text) < 31 and is_street4 == False:
                                    is_street3 = True
                                    street3 = street3 + text + ' '
                                elif len(street4 + text) < 31 and is_street5 == False:
                                    is_street4 = True
                                    street4 = street4 + text + ' '
                                elif len(street5 + text) < 31:
                                    is_street5 = True
                                    street5 = street5 + text + ' '
                            if street1 != '':
                                return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            else:
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                            if street2 != '':
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                                return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            else:
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            if street3 != '':
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                                return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            else:
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            if street4 != '':
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                                return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            else:
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            if street5 != '':
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                                return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                            else:
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                        elif rec.partner_id.street2:
                            street_split = rec.partner_id.street2
                            street_split = street_split.split()
                            street1 = ''
                            street2 = ''
                            street3 = ''
                            street4 = ''
                            street5 = ''

                            is_street2 = False
                            is_street3 = False
                            is_street4 = False
                            is_street5 = False
                            for text in street_split:
                                if len(street1 + text) < 31 and is_street2 == False:
                                    street1 = street1 + text + ' '
                                elif len(street2 + text) < 31 and is_street3 == False:
                                    is_street2 = True
                                    street2 = street2 + text + ' '
                                elif len(street3 + text) < 31 and is_street4 == False:
                                    is_street3 = True
                                    street3 = street3 + text + ' '
                                elif len(street4 + text) < 31 and is_street5 == False:
                                    is_street4 = True
                                    street4 = street4 + text + ' '
                                elif len(street5 + text) < 31:
                                    is_street5 = True
                                    street5 = street5 + text + ' '
                            
                            if street1 != '':
                                return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            else:
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                            if street2 != '':
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                                return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            else:
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            if street3 != '':
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                                return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            else:
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            if street4 != '':
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                                return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            else:
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            if street5 != '':
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                                return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                            else:
                                return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)     
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                else:
                    return_dot_matrix['line2'] = 'Address   : '
                    if rec.sites_id.site_address:
                        street_split = rec.sites_id.site_address
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                    
                        if street1 != '':
                            return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                        else:
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                    else:
                        if rec.partner_id.street and rec.partner_id.street2:
                            street_split = rec.partner_id.street + rec.partner_id.street2
                            street_split = street_split.split()
                            street1 = ''
                            street2 = ''
                            street3 = ''
                            street4 = ''
                            street5 = ''

                            is_street2 = False
                            is_street3 = False
                            is_street4 = False
                            is_street5 = False
                            for text in street_split:
                                if len(street1 + text) < 31 and is_street2 == False:
                                    street1 = street1 + text + ' '
                                elif len(street2 + text) < 31 and is_street3 == False:
                                    is_street2 = True
                                    street2 = street2 + text + ' '
                                elif len(street3 + text) < 31 and is_street4 == False:
                                    is_street3 = True
                                    street3 = street3 + text + ' '
                                elif len(street4 + text) < 31 and is_street5 == False:
                                    is_street4 = True
                                    street4 = street4 + text + ' '
                                elif len(street5 + text) < 31:
                                    is_street5 = True
                                    street5 = street5 + text + ' '
                            
                            if street1 != '':
                                return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                                return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                            else:
                                return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)

                            if street2 != '':
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                                return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            else:
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            if street3 != '':
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                                return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            else:
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            if street4 != '':
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                                return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            else:
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            if street5 != '':
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                                return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            else:
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        elif rec.partner_id.street:
                            street_split = rec.partner_id.street
                            street_split = street_split.split()
                            street1 = ''
                            street2 = ''
                            street3 = ''
                            street4 = ''
                            street5 = ''

                            is_street2 = False
                            is_street3 = False
                            is_street4 = False
                            is_street5 = False
                            for text in street_split:
                                if len(street1 + text) < 31 and is_street2 == False:
                                    street1 = street1 + text + ' '
                                elif len(street2 + text) < 31 and is_street3 == False:
                                    is_street2 = True
                                    street2 = street2 + text + ' '
                                elif len(street3 + text) < 31 and is_street4 == False:
                                    is_street3 = True
                                    street3 = street3 + text + ' '
                                elif len(street4 + text) < 31 and is_street5 == False:
                                    is_street4 = True
                                    street4 = street4 + text + ' '
                                elif len(street5 + text) < 31:
                                    is_street5 = True
                                    street5 = street5 + text + ' '
                            
                            if street1 != '':
                                return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                                return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                            else:
                                return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                            if street2 != '':
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                                return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            else:
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            if street3 != '':
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                                return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            else:
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            if street4 != '':
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                                return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            else:
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            if street5 != '':
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                                return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            else:
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        elif rec.partner_id.street2:
                            street_split = rec.partner_id.street2
                            street_split = street_split.split()
                            street1 = ''
                            street2 = ''
                            street3 = ''
                            street4 = ''
                            street5 = ''

                            is_street2 = False
                            is_street3 = False
                            is_street4 = False
                            is_street5 = False
                            for text in street_split:
                                if len(street1 + text) < 31 and is_street2 == False:
                                    street1 = street1 + text + ' '
                                elif len(street2 + text) < 31 and is_street3 == False:
                                    is_street2 = True
                                    street2 = street2 + text + ' '
                                elif len(street3 + text) < 31 and is_street4 == False:
                                    is_street3 = True
                                    street3 = street3 + text + ' '
                                elif len(street4 + text) < 31 and is_street5 == False:
                                    is_street4 = True
                                    street4 = street4 + text + ' '
                                elif len(street5 + text) < 31:
                                    is_street5 = True
                                    street5 = street5 + text + ' '
                            
                            if street1 != '':
                                return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                                return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                            else:
                                return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)

                            if street2 != '':
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                                return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            else:
                                return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            if street3 != '':
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                                return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            else:
                                return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            if street4 != '':
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                                return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            else:
                                return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            if street5 != '':
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                                return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                            else:
                                return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
            else:
                if return_dot_matrix['line2'] != '':
                    return_dot_matrix['line3'] = 'Address   : '
                    if rec.partner_id.street and rec.partner_id.street2:
                        street_split = rec.partner_id.street + rec.partner_id.street2
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        
                        if street1 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                            return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                        else:
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                    elif rec.partner_id.street:
                        street_split = rec.partner_id.street
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        if street1 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                            return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                        else:
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                    elif rec.partner_id.street2:
                        street_split = rec.partner_id.street2
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        
                        if street1 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street1
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street2
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street3
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street4
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].rjust(12)
                            return_dot_matrix['line24'] = return_dot_matrix['line24'] + street5
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                        else:
                            return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)     
                    else:
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        return_dot_matrix['line24'] = return_dot_matrix['line24'].ljust(44)
                else:
                    return_dot_matrix['line2'] = 'Address   : '
                    if rec.partner_id.street and rec.partner_id.street2:
                        street_split = rec.partner_id.street + rec.partner_id.street2
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        
                        if street1 != '':
                            return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                        else:
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                    elif rec.partner_id.street:
                        street_split = rec.partner_id.street
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        
                        if street1 != '':
                            return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                        else:
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                        if street2 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                    elif rec.partner_id.street2:
                        street_split = rec.partner_id.street2
                        street_split = street_split.split()
                        street1 = ''
                        street2 = ''
                        street3 = ''
                        street4 = ''
                        street5 = ''

                        is_street2 = False
                        is_street3 = False
                        is_street4 = False
                        is_street5 = False
                        for text in street_split:
                            if len(street1 + text) < 31 and is_street2 == False:
                                street1 = street1 + text + ' '
                            elif len(street2 + text) < 31 and is_street3 == False:
                                is_street2 = True
                                street2 = street2 + text + ' '
                            elif len(street3 + text) < 31 and is_street4 == False:
                                is_street3 = True
                                street3 = street3 + text + ' '
                            elif len(street4 + text) < 31 and is_street5 == False:
                                is_street4 = True
                                street4 = street4 + text + ' '
                            elif len(street5 + text) < 31:
                                is_street5 = True
                                street5 = street5 + text + ' '
                        
                        if street1 != '':
                            return_dot_matrix['line2'] = return_dot_matrix['line2'] + street1
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                        else:
                            return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)

                        if street2 != '':
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].rjust(12)
                            return_dot_matrix['line3'] = return_dot_matrix['line3'] + street2
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        else:
                            return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        if street3 != '':
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].rjust(12)
                            return_dot_matrix['line4'] = return_dot_matrix['line4'] + street3
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        else:
                            return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        if street4 != '':
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].rjust(12)
                            return_dot_matrix['line5'] = return_dot_matrix['line5'] + street4
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        else:
                            return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)
                        if street5 != '':
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].rjust(12)
                            return_dot_matrix['line21'] = return_dot_matrix['line21'] + street5
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                        else:
                            return_dot_matrix['line21'] = return_dot_matrix['line21'].ljust(44)
                    else:
                        return_dot_matrix['line2'] = return_dot_matrix['line2'].ljust(44)
                        return_dot_matrix['line3'] = return_dot_matrix['line3'].ljust(44)
                        return_dot_matrix['line4'] = return_dot_matrix['line4'].ljust(44)
                        return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(44)

            return_dot_matrix['line2'] = return_dot_matrix['line2'] + 'Date         : '
            if rec.invoice_date:
                return_dot_matrix['line2'] = return_dot_matrix['line2'] + rec.invoice_date.strftime('%d-%b-%Y')
            return_dot_matrix['line3'] = return_dot_matrix['line3'] + 'Register No  : '
            if rec.po_numbers_gen21:
                return_dot_matrix['line3'] = return_dot_matrix['line3'] + rec.mo_numbers_gen21
            
            if rec.sales_person_gen21:
                sales_person_gen21 = rec.sales_person_gen21.split()
                sales_person1 = ''
                sales_person2 = ''

                is_sales_person2 = False
                for text in sales_person_gen21:
                    if len(sales_person1 + text) < 17 and is_sales_person2 == False:
                        sales_person1 = sales_person1 + text + ' '
                    elif len(sales_person2 + text) < 17:
                        is_street2 = True
                        sales_person2 = sales_person2 + text + ' '
                return_dot_matrix['line4'] = return_dot_matrix['line4'] + 'AE           : '
                if sales_person1:
                    return_dot_matrix['line4'] = return_dot_matrix['line4'] + sales_person1
                if sales_person2:
                    return_dot_matrix['line5'] = return_dot_matrix['line5'].ljust(59)
                    return_dot_matrix['line5'] = return_dot_matrix['line5'] + sales_person2
            
            return_dot_matrix['line22'] = 'Order No  : '
            if rec.po_numbers_gen21:
                return_dot_matrix['line22'] = 'Order No  : ' + rec.po_numbers_gen21
                return_dot_matrix['line22'] = return_dot_matrix['line22'].ljust(44)
            else:
                return_dot_matrix['line22'] = return_dot_matrix['line22'].ljust(44)
            
            return_dot_matrix['line6'] = 'Advertiser: '
            if rec.advertiser_gen21:
                advertiver_gen21 = rec.advertiser_gen21
                if "&" in advertiver_gen21:
                    advertiver_gen21 = advertiver_gen21.replace("&", "And")
                return_dot_matrix['line6'] = 'Advertiser: ' + advertiver_gen21
                return_dot_matrix['line6'] = return_dot_matrix['line6'].ljust(44)
            else:
                return_dot_matrix['line6'] = return_dot_matrix['line6'].ljust(44)
            
            product_gen21 = ''
            if rec.product_gen21:
                product_gen21 = rec.product_gen21.replace("&", "And")
            
            if rec.ar_receipt_type == 'iklan':
                return_dot_matrix['line7'] = 'BRAND : '
                return_dot_matrix['ar_receipt_type'] = 'iklan'
            else:
                if rec.narration:
                    return_dot_matrix['narration'] = rec.narration.replace("\n", "\n  ")
            
            if rec.source_type_gen21 == 'iklan_bms':
                return_dot_matrix['source_type_gen21'] = 'iklan_bms'
            else:
                return_dot_matrix['manual_desc'] = rec.ref
            
            if rec.invoice_line_ids[0].name:
                return_dot_matrix['line7'] = return_dot_matrix['line7'] + product_gen21
            
            return_dot_matrix['line8'] = return_dot_matrix['line8'].ljust(35)
            return_dot_matrix['line8'] = return_dot_matrix['line8'] + 'Total Gross     :'
            if rec.invoice_line_ids[0].total_gross_gen21:
                # txt_gross = "{:,}".format(rec.invoice_line_ids[0].total_gross_gen21).replace('.0', '')
                txt_gross = "{:,.2f}".format(sum(rec.invoice_line_ids.mapped('total_gross_gen21')))
                rjust_txt = 57 + (17 - len(txt_gross))
                return_dot_matrix['is_gross'] = True
                return_dot_matrix['line8'] = return_dot_matrix['line8'].ljust(rjust_txt) + txt_gross
            else:
                return_dot_matrix['line8'] = return_dot_matrix['line8'].ljust(73) + '0'
            
            return_dot_matrix['line9'] = return_dot_matrix['line9'].ljust(35)
            return_dot_matrix['line9'] = return_dot_matrix['line9'] + 'Agency Disc     :'
            if rec.invoice_line_ids[0].agency_discount_gen21:
                # agency_discount = round(rec.invoice_line_ids[0].total_gross_gen21 * (rec.invoice_line_ids[0].agency_discount_gen21 / 100), 0)
                agency_discount = round(sum(x.total_gross_gen21 * x.agency_discount_gen21 / 100 for x in rec.invoice_line_ids), 0)
                txt_agency = "{:,.2f}".format(agency_discount)
                ljust_txt_agency = 57 + (17 - len(txt_agency))
                return_dot_matrix['line9'] = return_dot_matrix['line9'].ljust(ljust_txt_agency) + txt_agency
            else:
                return_dot_matrix['line9'] = return_dot_matrix['line9'].ljust(73) + '0'
            
            return_dot_matrix['line10'] = return_dot_matrix['line10'].ljust(35)
            return_dot_matrix['line10'] = return_dot_matrix['line10'] + 'NETT Amount     :'
            if rec.amount_untaxed:
                txt_net = "{:,.2f}".format(rec.amount_untaxed)
                ljust_txt_net = 57 + (17 - len(txt_net))
                return_dot_matrix['line10'] = return_dot_matrix['line10'].ljust(ljust_txt_net)+ txt_net
            else:
                return_dot_matrix['line10'] = return_dot_matrix['line10'].ljust(73) + '0'
            
            tax = rec.get_tax_info()
            tax_amount = 0
            if tax:
                tax_amount = sum(-taxes[1] for taxes in tax)

            return_dot_matrix['line11'] = return_dot_matrix['line11'].ljust(35)
            return_dot_matrix['line11'] = return_dot_matrix['line11'] + 'VAT             :'
            if tax_amount:
                txt_tax_amount = "{:,.2f}".format(tax_amount)
                ljust_txt_tax_amount = 57 + (17 - len(txt_tax_amount))
                return_dot_matrix['line11'] = return_dot_matrix['line11'].ljust(ljust_txt_tax_amount) + txt_tax_amount
            else:
                return_dot_matrix['line11'] = return_dot_matrix['line11'].ljust(73) + '0'
            
            return_dot_matrix['line12'] = return_dot_matrix['line12'].ljust(35)
            return_dot_matrix['line12'] = return_dot_matrix['line12'] + 'Total Amount Due:'
            if rec.amount_total:
                txt_amount_total = "{:,.2f}".format(rec.amount_total)
                ljust_txt_amount_total = 57 + (17 - len(txt_amount_total))
                return_dot_matrix['line12'] = return_dot_matrix['line12'].ljust(ljust_txt_amount_total) + txt_amount_total
            else:
                return_dot_matrix['line12'] = return_dot_matrix['line12'].ljust(73) + '0'
            
            return_dot_matrix['line13'] = 'Due Date  : '
            
            if rec.invoice_payment_term_id:
                add_days = rec.invoice_payment_term_id.line_ids[0].days
                date_due = rec.invoice_date + datetime.timedelta(days=add_days)
                return_dot_matrix['line13'] = return_dot_matrix['line13'] + date_due.strftime('%d-%b-%Y')
            else:
                return_dot_matrix['line13'] = return_dot_matrix['line13'] + rec.invoice_date_due.strftime('%d-%b-%Y')
            
            if rec.amount_in_words_gen21:
                amount_in_words = rec.amount_in_words_gen21.split()
                amount_in_words1 = ''
                amount_in_words2 = ''
                amount_in_words3 = ''
                is_amount_in_words2 = False
                is_amount_in_words3 = False
                for text in amount_in_words:
                    if len(amount_in_words1 + text) < 58 and is_amount_in_words2 == False:
                        amount_in_words1 = amount_in_words1 + text + ' '
                    elif len(amount_in_words2 + text) < 58 and is_amount_in_words3 == False:
                        is_amount_in_words2 = True
                        amount_in_words2 = amount_in_words2 + text + ' '
                    elif len(amount_in_words3 + text) < 58:
                        is_amount_in_words3 = True
                        amount_in_words3 = amount_in_words3 + text + ' '
                
                if amount_in_words1 != '':
                    return_dot_matrix['line14'] = '## ' + return_dot_matrix['line14'] + amount_in_words1

                if amount_in_words2 != '' and amount_in_words3 == '':
                    return_dot_matrix['line15'] = return_dot_matrix['line15'] + amount_in_words2 + ' ##'
                elif amount_in_words2 != '' and amount_in_words3 != '':
                    return_dot_matrix['line15'] = return_dot_matrix['line15'] + amount_in_words2 + ' '
                else:
                    return_dot_matrix['line14'] = return_dot_matrix['line14'] + ' ##'
                
                if amount_in_words3 != '':
                    return_dot_matrix['line23'] = return_dot_matrix['line23'] + amount_in_words3 + ' ##'
            
            return_dot_matrix['line16'] = return_dot_matrix['line16'] + 'Please remit to    : ' + rec.company_id.name
            partner_remit = self.env['res.partner.remit'].search([('company_id', '=', rec.company_id.id), ('partner_ids', 'in', [rec.partner_id.id])])
            txt_remit = ''
            if partner_remit:
                for remit in partner_remit:
                    if remit.partner_ids:
                        for partner_remit in remit.partner_ids:
                            if partner_remit.id == rec.partner_id.id:
                                if remit.bank_ids:
                                    for bank in remit.bank_ids:
                                        if bank.currency_id.id == rec.currency_id.id:
                                            check_text_bank = '  - ' + bank.bank_name + ', A/C ' + rec.currency_id.name + ' ' + bank.acc_number
                                            if check_text_bank not in txt_remit:
                                                txt_remit += '  - ' + bank.bank_name + ', A/C ' + rec.currency_id.name + ' ' + bank.acc_number + '\n'
            return_dot_matrix['line17'] = txt_remit
            return_dot_matrix['line18'] = return_dot_matrix['line18'].ljust(56) + '-------------------'
            return_dot_matrix['line19'] = return_dot_matrix['line19'].ljust(56) + '-------------------'
            return_dot_matrix['line20'] = str(number_page)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'data_dot_matrix': data_dot_matrix
        }
