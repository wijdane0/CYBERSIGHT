from flask import Blueprint, render_template, request, jsonify, Response
from app.models import IOC
from datetime import datetime
import csv
import io
from sqlalchemy import func
import os

bp = Blueprint('main', __name__)

@bp.route('/iocs')
def iocs_list():
    page = request.args.get('page', 1, type=int)
    ioc_type = request.args.get('type', 'all').lower()
    severity = request.args.get('severity', 'all')
    source = request.args.get('source', '')
    query = request.args.get('q', '')

    iocs_query = IOC.query
    HASH_TYPES = ['filehash-md5', 'filehash-sha1', 'filehash-sha256', 'hash']

    # TYPE filter
    if ioc_type not in ['all', '', None]:
        if ioc_type == 'ip':
            iocs_query = iocs_query.filter(func.lower(IOC.type).in_(['ip', 'ipv4']))
        elif ioc_type == 'hash':
            iocs_query = iocs_query.filter(func.lower(IOC.type).in_([t.lower() for t in HASH_TYPES]))
        else:
            iocs_query = iocs_query.filter(func.lower(IOC.type) == ioc_type)

    # SEVERITY filter
    if severity not in ['all', '', None]:
        iocs_query = iocs_query.filter(func.lower(IOC.severity) == severity.lower())

    # SOURCE filter
    if source and source.strip().lower() not in ['', 'all sources', 'all']:
        iocs_query = iocs_query.filter(func.lower(IOC.source).like(f"%{source.lower()}%"))

    # SEARCH filter
    if query and query.strip() != '':
        iocs_query = iocs_query.filter(IOC.value.ilike(f"%{query}%"))

    iocs = iocs_query.order_by(IOC.last_seen.desc()).paginate(page=page, per_page=20)

    # --- Dropdown options ---

    # Types
    raw_types = set(t[0].lower() for t in IOC.query.with_entities(IOC.type).distinct() if t[0])
    allowed_types = []
    if 'ip' in raw_types or 'ipv4' in raw_types:
        allowed_types.append('ip')
    if any(t in raw_types for t in [h.lower() for h in HASH_TYPES]):
        allowed_types.append('hash')
    if 'domain' in raw_types:
        allowed_types.append('domain')
    if 'url' in raw_types:
        allowed_types.append('url')
    ioc_types = ['all'] + allowed_types

    # Severities (force consistent set)
    severities = ['all', 'low', 'medium', 'high', 'unknown']

    # Sources (remove "manual" and empties)
    real_sources = [s[0] for s in IOC.query.with_entities(IOC.source).distinct() if s[0] and s[0].lower() != 'manual']
    sources = sorted(set(real_sources))

    last_ioc = IOC.query.order_by(IOC.last_seen.desc()).first()
    last_updated = last_ioc.last_seen.strftime('%Y-%m-%d %H:%M:%S') if last_ioc else ''
    window = 3
    start_page = max(1, iocs.page - window)
    end_page = min(iocs.pages, iocs.page + window)

    return render_template(
        'iocs.html',
        iocs=iocs,
        ioc_type=ioc_type,
        severity=severity,
        source=source,
        query=query,
        ioc_types=ioc_types,
        severities=severities,
        sources=sources,
        last_updated=last_updated,
        start_page=start_page,
        end_page=end_page
    )

@bp.route('/')
def index():
    total_iocs = IOC.query.count()
    ip_count = IOC.query.filter(func.lower(IOC.type).in_(['ip', 'ipv4'])).count()
    hash_types = ['filehash-md5', 'filehash-sha1', 'filehash-sha256', 'hash']
    hash_count = IOC.query.filter(func.lower(IOC.type).in_([h.lower() for h in hash_types])).count()
    domain_count = IOC.query.filter(func.lower(IOC.type) == 'domain').count()
    url_count = IOC.query.filter(func.lower(IOC.type) == 'url').count()

    last_ioc = IOC.query.order_by(IOC.last_seen.desc()).first()
    last_updated = last_ioc.last_seen.strftime('%Y-%m-%d %H:%M:%S') if last_ioc and last_ioc.last_seen else ''

    latest_iocs = IOC.query.order_by(IOC.last_seen.desc()).limit(10).all()
    for ioc in latest_iocs:
        print("DEBUG DASHBOARD IOC:", ioc.id, ioc.type, ioc.value)

    return render_template(
        'index.html',
        total_iocs=total_iocs,
        ip_count=ip_count,
        hash_count=hash_count,
        domain_count=domain_count,
        url_count=url_count,
        latest_iocs=latest_iocs,
        last_updated=last_updated
    )
