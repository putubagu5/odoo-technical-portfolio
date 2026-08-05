from odoo import api, fields, models, _, tools


class MncSyncLogger(models.Model):
    _name = 'mnc.sync.logger'
    _description = 'MNC - Sync Logger'

    name = fields.Char(String="Nama", required=True)
    # model_id = fields.Many2one('ir.model', String="Model")
    model_name = fields.Char(String="Model", required=True)
    ip_address = fields.Char(string="IP Address")
    #
    step01_activity = fields.Char(string="S01-Activity")
    step01_desc = fields.Char(string="S01-Act-Desc")
    step01_source = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S01-Source")
    step01_target = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S01-Target")
    step01_start_time = fields.Datetime(string="S01-Start-Time")
    step01_end_time = fields.Datetime(string="S01-End-Time")
    step01_caller = fields.Char("S01-Called-from-Function")
    step01_count = fields.Integer(string="S01-Count")
    #
    step02_activity = fields.Char(string="S02-Activity")
    step02_desc = fields.Char(string="S02-Act-Desc")
    step02_source = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S02-Source")
    step02_target = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S02-Target")
    step02_start_time = fields.Datetime(string="S02-Start-Time")
    step02_end_time = fields.Datetime(string="S02-End-Time")
    step02_caller = fields.Char("S02-Called-from-Function")
    step02_count = fields.Integer(string="S02-Count")
    #
    step03_activity = fields.Char(string="S03-Activity")
    step03_desc = fields.Char(string="S03-Act-Desc")
    step03_source = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S03-Source")
    step03_target = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S03-Target")
    step03_start_time = fields.Datetime(string="S03-Start-Time")
    step03_end_time = fields.Datetime(string="S03-End-Time")
    step03_caller = fields.Char("S03-Called-from-Function")
    step03_count = fields.Integer(string="S03-Count")
    #
    step04_activity = fields.Char(string="S04-Activity")
    step04_desc = fields.Char(string="S04-Act-Desc")
    step04_source = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S04-Source")
    step04_target = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="S04-Target")
    step04_start_time = fields.Datetime(string="S04-Start-Time")
    step04_end_time = fields.Datetime(string="S04-End-Time")
    step04_caller = fields.Char("S04-Called-from-Function")
    step04_count = fields.Integer(string="S04-Count")
    #
    curr_steps = fields.Integer(string="Current-Steps")
    total_steps = fields.Integer(string="Total-Steps")
    diff_count = fields.Integer(string="Diff-Count",
                                help="kalau difference = 0 , maka jumlah data sama antara source dan target")
    #
    #
    #
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    source_db = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="Source DB")
    source_table = fields.Char(string="Source Table")
    fetch_cnt = fields.Integer(string="Fetch Count")
    target_db = fields.Selection([
        ('odoo', 'Odoo'),
        ('odoo_stg', 'Odoo Staging'),
        ('ora', 'Oracle'),
        ('ora_stg', 'Oracle Staging'),
    ], string="Target DB")
    target_table = fields.Char(string="Target Table")
    send_cnt = fields.Integer(string="Send Count")
    sent_cnt = fields.Integer(string="Sent Count")
    state = fields.Selection([
        ('fetch', 'Fetch Data from Source'),
        ('send', 'Send data to target'),
        ('sent', 'Data Sent Successfully'),
    ], string='State', default='fetch', readonly=True,
        help='Fetch = Get Data From Source, \n\nSend = Send Data From Source to Target Staging Table, \n\nSent = Data Sent Successfully into Target Staging Table')
    desc = fields.Char(string="Description")
    func_run = fields.Char(string="Function")
    parent_id = fields.Many2one('mnc.sync.logger', string="Parent ID")
