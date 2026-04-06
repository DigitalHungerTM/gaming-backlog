import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

""" TODO

- set up git repo
- set up migrations
- manifest.json to make installable as app (needs to be hosted behind SSL secured domain)
- more queue functionality
- connection to IGDB for cover art (through public API)
- connection to IGDB for game information (through public API)
- connection to ProtonDB for proton information (no public api though)

"""


def create_app():
    app = Flask(__name__)

    load_dotenv() # flask does this too but better to be explicit
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite', # use sqlite database in local file
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    bootstrap = Bootstrap5()
    bootstrap.init_app(app)

    from . import db
    db.init_app(app)

    from . import backlog
    app.register_blueprint(backlog.bp)
    app.add_url_rule('/', endpoint='index')
    app.register_error_handler(404, lambda _: render_template('404.html'))

    return app