import requests
from datetime import datetime
from flask import current_app
from ..models import db, IOC
def fetch_urlhaus_feeds():
    """Fetch malware URLs from URLhaus"""
    import requests
    from flask import current_app as app
    from app.utils import update_or_create_ioc

    url = "https://urlhaus.abuse.ch/downloads/text_online/"

    with app.app_context():
        try:
            print("1. Downloading feed...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            lines = [line.strip() for line in response.text.split('\n') if line.strip() and not line.startswith('#')]
            print(f"2. Raw lines: {len(lines)}\n")

            count = 0
            for i, line in enumerate(lines[:100], start=1):  # Limit for testing
                print(f"Processing line {i}: {line}...")

                update_or_create_ioc(
                    type='url',
                    value=line,
                    source='urlhaus',
                    description='URL from URLhaus feed',
                    threat_type='malware',
                    severity='high'
                )
                count += 1

            print(f"\nFINAL RESULT: Processed {count} lines, stored {count} IOCs")

        except Exception as e:
            print("Error fetching URLhaus feed:", e)
