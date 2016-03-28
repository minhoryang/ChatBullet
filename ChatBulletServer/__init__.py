from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from .chat import (
    socketio,
)
from .db import (
    admin,
    db,
    migrate,
)
from .view import add_views


def create_app_and_socket(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    admin.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    socketio.init_app(app)
    add_views(app)

    return app, socketio
