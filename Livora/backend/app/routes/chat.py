from flask import Blueprint, jsonify, request
from sqlalchemy import and_, or_

from app import db, socketio
from app.models.chat import ChatMessage
from app.models.match import Match
from app.models.user import User
from app.socket_events import emit_to_user
from app.utils.jwt_utils import jwt_user_id
from app.utils.roles import ROLE_ADMIN, ROLE_TENANT, get_user_role, has_accepted_roommate_match
from flask_jwt_extended import jwt_required

bp = Blueprint("chat", __name__, url_prefix="/chat")


def _can_use_roommate_chat(user: User | None) -> bool:
    if not user:
        return False
    return get_user_role(user) in (ROLE_TENANT, ROLE_ADMIN)


@bp.route("/with/<int:user_id>", methods=["GET"])
@jwt_required()
def get_chat(user_id):
    current_id = jwt_user_id()
    me_user = User.query.get(current_id)
    if not me_user or not _can_use_roommate_chat(me_user):
        return jsonify({"error": "Chat is available for tenant accounts only"}), 403
    if not has_accepted_roommate_match(current_id, user_id):
        return jsonify(
            {"error": "You can only open chat after the other user accepts your roommate request."}
        ), 403
    messages = (
        ChatMessage.query.filter(
            or_(
                and_(
                    ChatMessage.sender_id == current_id,
                    ChatMessage.receiver_id == user_id,
                ),
                and_(
                    ChatMessage.sender_id == user_id,
                    ChatMessage.receiver_id == current_id,
                ),
            )
        )
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )
    return jsonify({"messages": [m.to_dict() for m in messages]})


@bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    current_id = jwt_user_id()
    me_user = User.query.get(current_id)
    if not me_user or not _can_use_roommate_chat(me_user):
        return jsonify({"error": "Chat is available for tenant accounts only"}), 403
    data = request.get_json()
    receiver_id = data.get("receiver_id")
    message = data.get("message")
    is_anonymous = data.get("is_anonymous", False)
    if not receiver_id or not message:
        return jsonify({"error": "Missing fields"}), 400
    try:
        receiver_id = int(receiver_id)
    except (TypeError, ValueError):
        return jsonify({"error": "receiver_id must be an integer"}), 400
    if not User.query.get(receiver_id):
        return jsonify({"error": "Receiver not found"}), 404
    recv = User.query.get(receiver_id)
    if not recv or get_user_role(recv) != ROLE_TENANT:
        return jsonify({"error": "You can only message tenant accounts"}), 403
    if not has_accepted_roommate_match(current_id, receiver_id):
        return jsonify(
            {"error": "Messaging is enabled only after your roommate request is accepted."}
        ), 403
    msg = ChatMessage(
        sender_id=current_id,
        receiver_id=receiver_id,
        message=message,
        is_anonymous=is_anonymous,
    )
    db.session.add(msg)
    db.session.commit()
    payload = {"message": msg.to_dict()}
    try:
        emit_to_user(socketio, receiver_id, "new_message", payload)
    except Exception:  # noqa: BLE001
        pass
    return jsonify({"msg": "Message sent", "message": msg.to_dict()})


def _other_in_match(m: Match, me: int) -> int:
    return m.user2_id if m.user1_id == me else m.user1_id


@bp.route("/inbox", methods=["GET"])
@jwt_required()
def inbox():
    """Accepted roommate partners (with or without messages) + latest message preview."""
    me = jwt_user_id()
    me_user = User.query.get(me)
    if not me_user or not _can_use_roommate_chat(me_user):
        return jsonify({"error": "Inbox is available for tenant accounts only"}), 403

    msgs = (
        ChatMessage.query.filter(
            or_(ChatMessage.sender_id == me, ChatMessage.receiver_id == me)
        )
        .order_by(ChatMessage.timestamp.desc())
        .limit(300)
        .all()
    )
    by_peer: dict[int, dict] = {}
    for m in msgs:
        other = m.receiver_id if m.sender_id == me else m.sender_id
        if other not in by_peer:
            peer_u = User.query.get(other)
            by_peer[other] = {
                "peer_id": other,
                "peer_name": peer_u.name if peer_u else f"User #{other}",
                "last_message": m.to_dict(),
            }

    matches = Match.query.filter(
        Match.status == "accepted",
        or_(Match.user1_id == me, Match.user2_id == me),
    ).all()
    for row in matches:
        oid = _other_in_match(row, me)
        peer_u = User.query.get(oid)
        if oid not in by_peer:
            by_peer[oid] = {
                "peer_id": oid,
                "peer_name": peer_u.name if peer_u else f"User #{oid}",
                "last_message": None,
            }
        elif peer_u and by_peer[oid].get("peer_name", "").startswith("User #"):
            by_peer[oid]["peer_name"] = peer_u.name

    convs = list(by_peer.values())
    convs.sort(
        key=lambda c: (c["last_message"] or {}).get("timestamp") or "",
        reverse=True,
    )
    return jsonify({"conversations": convs})


@bp.route("/read", methods=["POST"])
@jwt_required()
def mark_conversation_read():
    current_id = jwt_user_id()
    data = request.get_json(silent=True) or {}
    peer_id = data.get("user_id")
    if peer_id is None:
        return jsonify({"error": "user_id required"}), 400
    try:
        peer_id = int(peer_id)
    except (TypeError, ValueError):
        return jsonify({"error": "user_id must be an integer"}), 400
    updated = (
        ChatMessage.query.filter(
            and_(
                ChatMessage.sender_id == peer_id,
                ChatMessage.receiver_id == current_id,
                ChatMessage.is_read.is_(False),
            )
        )
        .update({ChatMessage.is_read: True}, synchronize_session=False)
    )
    db.session.commit()
    return jsonify({"marked_read": updated})
