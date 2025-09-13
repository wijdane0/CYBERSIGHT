from datetime import datetime
from app.models import IOC, db
from sqlalchemy.exc import IntegrityError
import base64


def vt_url_id(raw_url: str) -> str:
    """Return VirusTotal GUI identifier for a URL."""
    if not raw_url:
        return ""
    # Base64 URL-safe encode without padding (= removed)
    return base64.urlsafe_b64encode(raw_url.encode()).decode().strip("=")


def normalize_severity(sev=None, vt_score=None, abuse_score=None):
    """
    Normalize severity levels:
      - If sev explicitly provided by feed → trust it (lowercased).
      - Otherwise, derive from VirusTotal & AbuseIPDB scores.
    Rules:
      - unknown → score == 0
      - low     → 1–3 detections
      - medium  → 4–10 detections
      - high    → >10 detections
    """
    if sev:
        return sev.lower()

    score = 0
    if vt_score:
        score += vt_score
    if abuse_score:
        score += abuse_score

    if score == 0:
        return "unknown"
    elif score <= 3:
        return "low"
    elif 4 <= score <= 10:
        return "medium"
    else:
        return "high"


def update_or_create_ioc(type, value, source, description=None, threat_type=None, severity=None, vt_score=None, abuse_score=None):
    """Insert or update an IOC in the database with normalized severity."""
    ioc = IOC.query.filter_by(value=value).first()

    if ioc:
        # Update existing record
        print(f"Updating existing IOC: {value}")
        ioc.last_seen = datetime.utcnow()
        ioc.source = source  # optionally update source
        ioc.description = description or ioc.description
        ioc.threat_type = threat_type or ioc.threat_type
        ioc.virustotal_score = vt_score if vt_score is not None else ioc.virustotal_score
        ioc.abuseipdb_score = abuse_score if abuse_score is not None else ioc.abuseipdb_score
        ioc.severity = normalize_severity(severity, ioc.virustotal_score, ioc.abuseipdb_score)
    else:
        # Insert new record
        print(f"Adding new IOC: {value}")
        ioc = IOC(
            type=type,
            value=value,
            source=source,
            description=description,
            threat_type=threat_type,
            virustotal_score=vt_score,
            abuseipdb_score=abuse_score,
            severity=normalize_severity(severity, vt_score, abuse_score),
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            is_active=True
        )
        db.session.add(ioc)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print(f"[ERROR] Could not save IOC '{value}': {e}")
