"""SocketIO Chat Module."""

from flask import (
    session,
)

from flask_socketio import (
    SocketIO,
    emit,
    disconnect,
    join_room,
    leave_room,
)

from .db import (
    User,
    Room,
    db,
)

socketio = SocketIO()
namespace = '/ws'


def _get_current_user():
    # TODO: Issue #9: Accounts
    # TODO: pull this out to db.user?
    user_id = session.get('user')
    if not user_id:
        return
    return User.query.get(user_id)


@socketio.on('connect', namespace=namespace)
def on_connected():
    """When User Connected, Join the previous rooms."""

    user = _get_current_user()
    if not user:
        disconnect()
        return

    for room in user.rooms:
        _join_room_and_notify(user, room)


@socketio.on('disconnect', namespace=namespace)
def on_disconnected():
    """When User Disconnected, Leave the current rooms."""

    user = _get_current_user()
    if not user:
        return

    for room in user.rooms:
        _leave_room_and_notify(user, room)


@socketio.on('send_message', namespace=namespace)
def on_send_message(message):
    """When User asked to send a message, Relay it to room."""
    # TODO: Check member.
    emit('talked', message, room=message['room'])


@socketio.on('join_req', namespace=namespace)
def on_join_request(message):
    """When User asked to join a room."""

    # Get room name
    room_name = message.get('room')
    if not room_name:
        return

    # Check the room was already existed. If not, create.
    room = Room.query.filter(
        Room.name == room_name,  # TODO
    ).first()
    if not room:
        room = Room()
        room.name = room_name
        db.session.add(room)

    # Affect to DB
    user = _get_current_user()
    user.rooms.append(room)
    db.session.commit()

    _join_room_and_notify(user, room)


def _join_room_and_notify(user, room):
    """Join room and notify the user in that room."""
    emit('system', {
        'message': 'Join #{0}'.format(room.name),
    })
    join_room(room.name)
    emit('system', {
        'message': '@{0} Join'.format(user.name)
    }, room=room.name)
    # TODO: Send room name, Connected User List


@socketio.on('leave_req', namespace=namespace)
def on_leave_request(message):
    """When User asked to leave the room."""

    # Get room name
    room_name = message.get('room')
    if not room_name:
        return

    # Check the room.
    room = Room.query.filter(
        Room.name == room_name,  # TODO
    ).first()
    if not room:
        return

    # Affect to DB
    user = _get_current_user()
    user.rooms.remove(room)

    # If no one in that room, delete it.
    if not room.users.first():
        db.session.delete(room)
    db.session.commit()

    _leave_room_and_notify(user, room)


def _leave_room_and_notify(user, room):
    """Leave room and notify the users in that room."""
    emit('system', {
        'message': 'Leave #{0}'.format(room.name),
    })
    leave_room(room.name)
    emit('system', {
        'message': '@{0} Leaves'.format(user.name)
    }, room=room.name)


@socketio.on('modify_msg_req', namespace=namespace)
def on_modify_msg_request(message):
    pass  # TODO: Issue #4


@socketio.on('delete_msg_req', namespace=namespace)
def on_delete_msg_request(message):
    pass  # TODO: Issue #4

# TODO: Issue #12: Direct Message.
