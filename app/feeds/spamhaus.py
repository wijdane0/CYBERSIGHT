import requests
from app import db
from app.models import IOC
from datetime import datetime

def fetch_spamhaus_drop():
    url = "https://www.spamhaus.org/drop/drop.txt"
    response = requests.get(url)

    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.startswith(";"):
                continue
            ip_range = line.split(";")[0].strip()
            if ip_range and not IOC.query.filter_by(value=ip_range).first():
                ioc = IOC(
                    type="ip",
                    value=ip_range,
                    source="Spamhaus DROP",
                    last_seen=datetime.utcnow()
                )
                db.session.add(ioc)
        db.session.commit()
    else:
        print("Failed to fetch from Spamhaus:", response.status_code)
