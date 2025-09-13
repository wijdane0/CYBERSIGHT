import requests
from flask import current_app as app
from app.utils import update_or_create_ioc

def fetch_otx_iocs():
    url = "https://otx.alienvault.com/api/v1/indicators/export"
    headers = {
        "X-OTX-API-KEY": "15ce1b13c15190a8be1ef1b6ce5b033d1321b4a9c406adf85b9bd2217dc34f96",
        "User-Agent": "threat-intel-dashboard/1.0"
    }
    params = {
        "type": "general",  # Could be 'IPv4', 'domain', etc.
        "limit": 100  # Limit for testing
    }

    with app.app_context():
        try:
            print("[AlienVault] Fetching IOCs from OTX...")
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"[AlienVault] Error: Status code {response.status_code}")
                print("[AlienVault] Response text:", response.text)
                return

            data = response.json()
            for item in data.get('results', []):
                ioc_type = item.get('type', '').lower()
                ioc_value = item.get('indicator')
                threat_type = item.get('title') or 'unknown'

                if ioc_value:
                    update_or_create_ioc(
                        type=ioc_type,
                        value=ioc_value,
                        source='AlienVault OTX',
                        description=item.get('description') or '',
                        threat_type=threat_type,
                        severity='medium'
                    )

        except Exception as e:
            print("[AlienVault] Exception:", e)
