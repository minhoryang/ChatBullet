"""SocketIO Chat Module."""

from datetime import timedelta

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
    Msg,
    db,
)

socketio = SocketIO()
namespace = '/ws'

# TODO: Need to make a template for SocketIO message.
#       Is there any WTF-thingy similar?


def _get_current_user():
    # TODO: Issue #9: Accounts
    # TODO: pull this out to db.user?
    user_id = session.get('user')
    if not user_id:
        return
    return User.query.get(user_id)


def _get_current_room(message):
    current_room_name = message.get('room')
    if not current_room_name:
        return
    found = Room.query.filter(
        Room.name == current_room_name,
    ).first()
    return found


@socketio.on('connect', namespace=namespace)
def on_connected():
    """When User Connected, Join the previous rooms without touching db."""

    user = _get_current_user()
    if not user:
        disconnect()
        return  # TODO: Notify error to user.

    for room in user.rooms:
        _join_room_and_notify(user, room)


@socketio.on('disconnect', namespace=namespace)
def on_disconnected():
    """When User Disconnected, Leave the current rooms without touching db."""

    user = _get_current_user()
    if not user:
        return  # TODO: Notify error to user.

    for room in user.rooms:
        _leave_room_and_notify(user, room)


@socketio.on('send_message', namespace=namespace)
def on_send_message(message):
    """When User asked to send a message, Relay it to room."""
    current_room = _get_current_room(message)
    current_user = _get_current_user()
    if (
        not current_room or
        not current_user or
        current_user not in current_room.users
    ):
        return  # TODO: Notify error to user.

    new_msg = Msg()
    new_msg.user_id = current_user.id
    new_msg.room_id = current_room.id
    new_msg.contents = message['data']
    db.session.add(new_msg)
    db.session.commit()

    message['id'] = str(new_msg.id)

    emit('talked', message, room=current_room.name)


@socketio.on('join_req', namespace=namespace)
def on_join_request(message):
    """When User asked to join a room."""

    # Get room name
    room_name = message.get('room')
    if not room_name:
        return  # TODO: Notify error to user.

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
    if room in user.rooms:
        return  # TODO: Notify error to user.
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
        return  # TODO: Notify error to user.

    # Check the room.
    room = Room.query.filter(
        Room.name == room_name,  # TODO
    ).first()
    if not room:
        return  # TODO: Notify error to user.

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


@socketio.on('lookback_messages', namespace=namespace)
def on_lookback_messages(message):
    """Issue #2, Get messages from that message."""
    from_msg_id = message.get('from_msg_id')
    if not from_msg_id:
        return

    # TODO: Issue #8. Need to show some message near from_msg_id.
    #       Now, I decide to use `timedelta(minutes=10)`.
    # TODO: Now we sent all messages between from_msg_id and latest.
    #       It seems like a time-consuming.
    #       Need to design the preview page of lookback
    from_msg = Msg.query.get(from_msg_id)
    for m in Msg.query.filter(
        Msg.room_id == from_msg.room.id,
        Msg.sent >= from_msg.sent - timedelta(minutes=10),
    ).order_by(
        Msg.sent.asc(),
    ):
        emit(
                'talked',
                {
                    'id': str(m.id),
                    'data': m.contents,
                },
                room=from_msg.room.name,
        )


@socketio.on('modify_msg_req', namespace=namespace)
def on_modify_msg_request(message):
    pass  # TODO: Issue #4


@socketio.on('delete_msg_req', namespace=namespace)
def on_delete_msg_request(message):
    pass  # TODO: Issue #4

# TODO: Issue #12: Direct Message.