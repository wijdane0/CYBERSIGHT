from .urlhaus import fetch_urlhaus_feeds
from .alienvault import fetch_otx_iocs
from .spamhaus import fetch_spamhaus_drop

def init_feeds():
    fetch_urlhaus_feeds()
    fetch_otx_iocs()
    fetch_spamhaus_drop()
