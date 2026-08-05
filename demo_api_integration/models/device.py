from odoo import models, fields, api
import logging
import requests

_logger = logging.getLogger(__name__)

@api.multi
def action_load_mfa_devices(self):
    """
    Load registered MFA devices for the current customer from Musashi API:
    POST /MFA/Device/List
    and POST /MFA/Device/History
    """
    self.ensure_one()
    _logger.info('Loading MFA devices for vb.customer id=%s', self.id)

    # 1️. Retrieve Musashi API configuration
    url_rec = self.env['vb.config'].search([
        ('code_type', '=', 'App'),
        ('code', '=', 'MFAInfo')
    ])
    if not url_rec:
        raise Warning(_('MFA API configuration not found (code_type=App, code=MFAInfo).'))

    # 2️. Build API base URL
    base_url = str(url_rec.parm1) + '/' + str(url_rec.parm5)
    list_url = base_url + '/MFA/Device/List'
    history_url = base_url + '/MFA/Device/History'

    # 3️. Build common request payload
    payload = {
        "request": {
            "data": {
                "user_id": str(self.id)
            }
        }
    }

    headers = {'Content-type': 'application/json'}
    devices = []
    history_devices = []

    # 4️. Call Device/List API
    try:
        _logger.info("MFA DEVICE LIST REQUEST -> URL: %s, Payload: %s", list_url, payload)
        response = requests.post(list_url, data=dumps(payload), headers=headers, timeout=15)

        if not response or response.status_code != 200:
            raise Warning(_('Failed to connect to Musashi MFA API. Please try again later.'))

        res_json = response.json()
        info_id = res_json.get('response', {}).get('infoID', '')
        info_msg = res_json.get('response', {}).get('infoMsg', '')
        data_list = res_json.get('response', {}).get('data', [])

        if info_id == 'MFA000' and isinstance(data_list, list):
            devices = data_list
        else:
            _logger.warning("MFA DEVICE LIST returned non-success infoID=%s, msg=%s", info_id, info_msg)

    except Exception as e:
        _logger.exception("MFA DEVICE LIST EXCEPTION for customer_id=%s: %s", self.id, e)

    # 5️. Call Device/History API
    try:
        _logger.info("MFA DEVICE HISTORY REQUEST -> URL: %s, Payload: %s", history_url, payload)
        response_hist = requests.post(history_url, data=dumps(payload), headers=headers, timeout=15)

        if response_hist and response_hist.status_code == 200:
            try:
                res_json_hist = response_hist.json()
            except Exception:
                res_json_hist = {}
                _logger.warning("MFA DEVICE HISTORY returned non-JSON response")

            info_id_hist = res_json_hist.get('response', {}).get('infoID', '')
            info_msg_hist = res_json_hist.get('response', {}).get('infoMsg', '')
            data_hist = res_json_hist.get('response', {}).get('data', [])

            if info_id_hist == 'MFA000' and isinstance(data_hist, list):
                # Add "source" tag so we know it's from history
                for h in data_hist:
                    h['source'] = 'History'
                history_devices = data_hist
            else:
                _logger.warning("MFA DEVICE HISTORY returned non-success infoID=%s, msg=%s", info_id_hist, info_msg_hist)
        else:
            _logger.warning("MFA DEVICE HISTORY no valid HTTP response")
    except Exception as e:
        _logger.warning("Failed to call MFA DEVICE HISTORY for customer_id=%s: %s", self.id, e)

    # 6️. Merge both device lists
    all_devices = devices + history_devices
    seen_ids = set()
    unique_devices = []
    for d in all_devices:
        dev_id = d.get('device_id')
        if dev_id not in seen_ids:
            seen_ids.add(dev_id)
            unique_devices.append(d)
    devices = unique_devices[:10]

    # 7. Fallback dummy device (for UAT / dev)
    if not devices:
        devices = [{
            'device_name': 'iPhone 15 Pro',
            'device_type': 'iOS',
            'device_id': 'ABC123',
            'registration_date': '2025-01-01 10:00:00',
            'last_authenticated': '2025-02-01 08:15:00',
            'status': 'Active',
            'is_primary': True,
            'source': 'Dummy',
        }]

    # 8. Replace existing temporary records
    self.env['mfa.device.temp'].search([('customer_id', '=', self.id)]).unlink()

    for d in devices:
        vals = {
            'customer_id': self.id,
            'device_name': d.get('device_name'),
            'device_type': d.get('device_type'),
            'device_id': d.get('device_id'),
            'registration_date': d.get('registration_date'),
            'last_authenticated': d.get('last_authenticated'),
            'status': d.get('status'),
            'is_primary': d.get('is_primary', False),
            'source': d.get('source', 'Current'),
        }
        self.env['mfa.device.temp'].create(vals)

    _logger.info("MFA devices loaded for customer_id=%s -> %s devices", self.id, len(devices))

    # 9. Return full form refresh
    return {'type': 'ir.actions.client', 'tag': 'reload'}