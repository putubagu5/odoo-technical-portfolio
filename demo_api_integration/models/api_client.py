import requests
from odoo import models
class DemoApiClient(models.AbstractModel):
    _name="demo.api.client"
    def get_devices(self):
        r=requests.get("https://jsonplaceholder.typicode.com/users",timeout=10)
        r.raise_for_status()
        return r.json()
