from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    from app.utils import vt_url_id
    app.jinja_env.globals.update(vt_url_id=vt_url_id)
    # ---- Import your fetch jobs correctly ----
    from app.feeds.urlhaus import fetch_urlhaus_feeds
    from app.feeds.spamhaus import fetch_spamhaus_drop
    from app.feeds.alienvault import fetch_otx_iocs

    scheduler = BackgroundScheduler(daemon=True)

    # ---- Each job wrapped in the app context ----
    def run_urlhaus():
        with app.app_context():
            print("Running URLHaus Fetch Job")

            fetch_urlhaus_feeds()

    def run_spamhaus():
        with app.app_context():
            fetch_spamhaus_drop()

    def run_otx():
        with app.app_context():
            fetch_otx_iocs()

    scheduler.add_job(run_urlhaus, 'interval', hours=24, id='urlhaus_job')
    scheduler.add_job(run_spamhaus, 'interval', hours=24, id='spamhaus_job')
    scheduler.add_job(run_otx, 'interval', hours=24, id='otx_job') 
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    return app
