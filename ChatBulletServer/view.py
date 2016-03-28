from flask import (
    redirect,
    render_template,
    request,
    url_for,
    session,
)

from .db import (
    User,
    Msg,
    db,
)


def add_views(app):
    app.route('/', methods=["GET", "POST"])(login)
    app.route('/chat/')(chat)
    app.route('/chat/<uuid:id>')(message)


def login():
    # TODO: Issue #9: flask-social flask-security
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get('user', None)
    if user:
        found = User.query.filter(
            User.name == user,
        ).first()
        if found:
            session['user'] = found.id
        else:
            u = User()
            u.name = user
            db.session.add(u)
            db.session.commit()
            session['user'] = u.id
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


def chat():
    return render_template("chat.html")


def message(id):
    """Issue #2: permalink for message."""

    found = Msg.query.get(id)
    if not found:
        return 'message not found', 404

    user_id = session.get('user')
    if not user_id:
        return redirect(url_for('login'))

    # TODO: Issue #11: ACL
    user = User.query.get(user_id)
    if user not in found.room.users:
        return redirect(url_for('login'))

    # TODO: Don't show the changed url to user.
    return render_template("chat.html", message_id=str(id))
