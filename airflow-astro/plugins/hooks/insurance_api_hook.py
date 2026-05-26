# plugins/hooks/insurance_api_hook.py
from airflow.hooks.base import BaseHook
import requests

class InsuranceAPIHook(BaseHook):
    """Reusable hook to connect to insurance data APIs."""
    
    def __init__(self, api_conn_id='insurance_api'):
        super().__init__()
        self.api_conn_id = api_conn_id

    def get_conn(self):
        conn = self.get_connection(self.api_conn_id)
        self.base_url = conn.host
        self.headers = {'Authorization': f'Bearer {conn.password}'}
        return self

    def get_claims(self, start_date, end_date):
        response = requests.get(
            f"{self.base_url}/claims",
            params={'start': start_date, 'end': end_date},
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()