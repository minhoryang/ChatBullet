from flask import (
    redirect,
    render_template,
    request,
    url_for,
    session,
)

from .db import (
    User,
    db,
)


def add_views(app):
    app.route('/', methods=["GET", "POST"])(login)
    app.route('/chat')(chat)


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
    # TODO: Issue #2: permalink
    return render_template("chat.html")
