import re
import urllib.parse
from odoo import api, fields, models


class PurchaseOrderCache(models.Model):
    _name = 'purchase.order.cache'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Purchase Order Cache'

    name = fields.Char('Name', copy=False)

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ inherit function to trigger cache creation and process url """
        res = super(PurchaseOrderCache, self).message_new(msg_dict, custom_values)

        # get all information from msg_dict
        body = msg_dict.get('body')
        body = urllib.parse.unquote(body)  # remember to unquote
        # target is the source (email sender). This function will always get
        # email from the users
        mail_to = msg_dict.get('from')

        # EXTRACT MAIL to use in fail email
        # special cases, parse mail. This is because the 'from' data in msg_dict
        # contains "User - <user@email.com>". To process, search for mail pattern
        mail_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        mail_res = re.search(mail_pattern, mail_to)
        if mail_res:  # considering the help from email client, assume all valid
            mail_to = mail_res.group(0)

        # EXTRACT URL from body, url is placed between {{}}
        url = ''
        url_pattern = r"\{\{(.*?)\}\}"
        url_res = re.search(url_pattern, body)
        if url_res:
            url = url_res.group(1)

        # parse body to get note, all data between [] are note
        note = ''
        note_pattern = r"\[\[(.*?)\]\]"
        note_res = re.search(note_pattern, body)
        if note_res:
            note = note_res.group(1)

        # EXTRACT FORWARD TO from body, all data between || are forward to
        mail_forward = ''
        forward_pattern = r"\|\|(.*?)\|\|"
        forward_res = re.search(forward_pattern, body)
        if forward_res:
            mail_forward = forward_res.group(1)

        if mail_forward:  # recheck the email validity
            forward_res = re.search(mail_pattern, mail_forward)
            if forward_res:
                mail_forward = forward_res.group(0)

        # proceed to process
        context = {
            'mail_to': mail_to,
            'mail_forward': mail_forward,
        }
        self.env['purchase.order'].with_context(context)._process_url(url, note)
        return res

    @api.model
    def _purge_records(self):
        """ function to purge all records """
        sql = """DELETE FROM purchase_order_cache"""
        self.env.cr.execute(sql)
        return
