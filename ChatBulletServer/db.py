from datetime import datetime
from uuid import uuid4

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.ext.security import (
    Security,
    SQLAlchemyUserDatastore,
    UserMixin,
    RoleMixin,
)
from sqlalchemy.ext.hybrid import hybrid_property

from ._types import (
    UUIDType,
)


admin = Admin()
db = SQLAlchemy()
migrate = Migrate()


# XXX: Issue #9: flask-social flask-security
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return "<{0}>".format(self.name)


users_in_room = db.Table(
        'users_in_room',
        db.Column('user_id', UUIDType(), db.ForeignKey('user.id')),
        db.Column('room_id', UUIDType(), db.ForeignKey('room.id')),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(UUIDType(), primary_key=True, default=uuid4)
    # XXX: Issue #9: flask-social flask-security
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    rooms = db.relationship(
            'Room',
            secondary=users_in_room,
            backref=db.backref('users', lazy='dynamic'),
            cascade='all, delete',
    )

    def __str__(self):
        return "@{0}".format(self.email)


class Room(db.Model):
    __tablename__ = "room"

    id = db.Column(UUIDType(), primary_key=True, default=uuid4)
    name = db.Column(db.String(50), unique=True)
    msgs = db.relationship(
            'Msg',
            backref=db.backref('room'),
            lazy='dynamic',
            cascade='all, delete',
    )
    # TODO: Issue #11: ACL

    def __str__(self):
        return "#{0}".format(self.name)


class Msg(db.Model):
    __tablename__ = "msg"

    # XXX: Issue #2: permalink
    id = db.Column(UUIDType(), primary_key=True, default=uuid4)
    user_id = db.Column(db.ForeignKey('user.id'))
    room_id = db.Column(db.ForeignKey('room.id'))
    contents = db.Column(db.String(), nullable=False)
    sent = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        return "'{0}'".format(self.contents)

    @hybrid_property
    def user(self):
        return User.query.get(self.user_id)


# TODO: flask-admin: primary_key didn't show.
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Msg, db.session))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()
