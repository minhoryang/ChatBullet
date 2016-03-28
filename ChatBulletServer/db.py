from datetime import datetime
from uuid import uuid4

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from ._types import (
    UUIDType,
)


admin = Admin()
db = SQLAlchemy()
migrate = Migrate()


users_in_room = db.Table(
        'users_in_room',
        db.Column('user_id', UUIDType(), db.ForeignKey('user.id')),
        db.Column('room_id', UUIDType(), db.ForeignKey('room.id')),
)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(UUIDType(), primary_key=True, default=uuid4)
    name = db.Column(db.String(50), unique=True)
    # TODO: Issue #9: flask-social flask-security
    rooms = db.relationship(
            'Room',
            secondary=users_in_room,
            backref=db.backref('users', lazy='dynamic'),
    )

    def __str__(self):
        return self.name


class Room(db.Model):
    __tablename__ = "room"

    id = db.Column(UUIDType(), primary_key=True, default=uuid4)
    name = db.Column(db.String(50), unique=True)
    msgs = db.relationship(
            'Msg',
            backref=db.backref('room'),
            lazy='dynamic',
    )
    # TODO: Issue #11: ACL

    def __str__(self):
        return self.name


class Msg(db.Model):
    __tablename__ = "msg"

    # TODO: Issue #2: permalink
    id = db.Column(UUIDType(), primary_key=True, default=uuid4)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref="parents")
    room_id = db.Column(db.ForeignKey('room.id'), nullable=False)
    contents = db.Column(db.String(), nullable=False)
    sent = db.Column(db.DateTime, default=datetime.now)
    # TODO: Issue #4: Modifiable, Deletable

    def __str__(self):
        return self.contents


# TODO: flask-admin: primary_key didn't show.
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Msg, db.session))
