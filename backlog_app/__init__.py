import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

from backlog_app import utils

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

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite', # use sqlite database in local file
        IGDB_CLIENT_ID=os.environ.get('IGDB_CLIENT_ID'),
        IGDB_CLIENT_SECRET=os.environ.get('IGDB_CLIENT_SECRET'),
        IGDB_DEBUG=os.environ.get('IGDB_DEBUG') in {'True', 'true'},
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    bootstrap = Bootstrap5()
    bootstrap.init_app(app)

    from . import db
    db.init_app(app)

    from igdb import igdb
    igdb.init_app(app)

    from . import backlog
    app.register_blueprint(backlog.bp)
    app.register_blueprint(utils.bp)
    app.add_url_rule('/', endpoint='index')
    app.register_error_handler(404, lambda _: render_template('404.html'))

    return app