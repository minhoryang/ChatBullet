from flask import (
    current_app,
    render_template,
)
from flask.ext.security import (
    login_required,
    logout_user,
    current_user,
)

from .db import (
    Msg,
)


def add_views(app):
    app.route('/')(chat)
    app.route('/<uuid:id>')(message)


@login_required
def chat():
    return render_template("chat.html")


@login_required
def message(id):
    """Issue #2: permalink for message."""

    found = Msg.query.get(id)
    if not found:
        return 'message not found', 404

    # XXX: Issue #11: ACL
    if not current_user.has_role(found):
        logout_user()  # TODO: notify it more gently.
        return current_app.login_manager.unauthorized()

    # TODO: Don't show the changed url to user.
    return render_template("chat.html", message_id=str(id))
