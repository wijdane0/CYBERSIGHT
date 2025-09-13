# app/models.py
from datetime import datetime
from app import db

class IOC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(256), unique=True, nullable=False)
    source = db.Column(db.String(50), nullable=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    threat_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    severity = db.Column(db.String(20))
    virustotal_score = db.Column(db.Integer)
    abuseipdb_score = db.Column(db.Integer)
    enriched = db.Column(db.Boolean, default=False)
