from app import create_app

from app.feeds import init_feeds  # import the init_feeds function

app = create_app()


with app.app_context():
    init_feeds()
