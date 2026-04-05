"""Real-time chat: clients connect with JWT in Socket.IO auth payload."""

import jwt as pyjwt
from flask import current_app, request
from flask_socketio import join_room

USER_ROOM_PREFIX = "user_"


def register_socketio_handlers(socketio):
    @socketio.on("connect")
    def on_connect(auth):
        token = None
        if isinstance(auth, dict):
            token = auth.get("token")
        if not token:
            current_app.logger.debug("Socket connect rejected: no token")
            return False

        try:
            secret = current_app.config["JWT_SECRET_KEY"]
            algo = current_app.config.get("JWT_ALGORITHM", "HS256")
            payload = pyjwt.decode(token, secret, algorithms=[algo])
            uid = int(payload["sub"])
        except Exception:  # noqa: BLE001
            current_app.logger.debug("Socket connect rejected: invalid token")
            return False

        room = f"{USER_ROOM_PREFIX}{uid}"
        join_room(room)
        current_app.logger.debug("Socket user %s joined %s", uid, room)

    @socketio.on("disconnect")
    def on_disconnect():
        current_app.logger.debug("Socket disconnect sid=%s", request.sid)


def emit_to_user(socketio, user_id: int, event: str, payload: dict):
    socketio.emit(event, payload, room=f"{USER_ROOM_PREFIX}{user_id}")
