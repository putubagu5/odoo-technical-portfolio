from odoo import models, fields, api
import logging
import requests

_logger = logging.getLogger(__name__)


class VBCustomer(models.Model):
    _inherit = "vb.customer"

    # Stored Boolean field (computed + inverse)
    mfa_exclusion = fields.Boolean(
        string="Exclude from MFA",
        compute="_compute_mfa_exclusion",
        inverse="_inverse_mfa_exclusion",
        store=True,
    )

    # ------------------------------------------
    # COMPUTE
    # ------------------------------------------
    @api.depends('user_id')
    def _compute_mfa_exclusion(self):
        """
        Compute stored field based on API value.
        Called whenever record loads or dependency changes.
        """
        for rec in self:
            try:
                rec.mfa_exclusion = rec._musashi_get_exclusion_status()
            except Exception as e:
                _logger.error("Error computing MFA exclusion for %s: %s", rec.id, e)
                rec.mfa_exclusion = False

    # ------------------------------------------
    # INVERSE
    # ------------------------------------------
    def _inverse_mfa_exclusion(self):
        """
        Trigger API call whenever user toggles Yes/No.
        """
        for rec in self:
            try:
                if rec.mfa_exclusion:
                    rec._musashi_add_exclusion()
                else:
                    rec._musashi_remove_exclusion()
            except Exception as e:
                _logger.error("Error updating Musashi MFA exclusion for %s: %s", rec.id, e)

    # ------------------------------------------
    # API URL BUILDER (uses vb.config standard)
    # ------------------------------------------
    def _build_musashi_url(self, endpoint):
        """
        Builds URL like:
        parm1/parm5/MFA/Exclude/List
        following your vb.config standard
        """
        self.ensure_one()
        url_rec = self.env['vb.config'].sudo().search([], limit=1)
        if not url_rec:
            raise ValueError("vb.config missing")

        base_url = f"{url_rec.parm1}/{url_rec.parm5}{endpoint}"
        return base_url

    # ------------------------------------------
    # API: CHECK STATUS
    # ------------------------------------------
    def _musashi_get_exclusion_status(self):
        self.ensure_one()
        endpoint = "/MFA/Exclude/List"
        url = self._build_musashi_url(endpoint)

        res = requests.get(url, timeout=10).json()
        exclusions = res["response"]["data"].get("exclusions", [])

        # Check if this user_id exists in exclusion list
        return any(str(x.get("user_id")) == str(self.user_id) for x in exclusions)

    # ------------------------------------------
    # API: ADD USER TO EXCLUSION
    # ------------------------------------------
    def _musashi_add_exclusion(self):
        self.ensure_one()
        endpoint = "/MFA/Exclude/Add"
        url = self._build_musashi_url(endpoint)

        payload = {"user_id": self.user_id}
        requests.post(url, json=payload, timeout=10)

    # ------------------------------------------
    # API: REMOVE USER FROM EXCLUSION
    # ------------------------------------------
    def _musashi_remove_exclusion(self):
        self.ensure_one()
        endpoint = "/MFA/Exclude/Remove"
        url = self._build_musashi_url(endpoint)

        payload = {"user_id": self.user_id}
        requests.post(url, json=payload, timeout=10)
