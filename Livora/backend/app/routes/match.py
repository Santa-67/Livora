from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from app import db
from app.models.match import Match
from app.models.user import User
from app.services import ml_inference
from app.services.ai_matcher import compatibility_with_source
from app.utils.jwt_utils import jwt_user_id
from app.utils.roles import ROLE_TENANT, get_user_role, has_accepted_roommate_match, tenant_required

bp = Blueprint("match", __name__, url_prefix="/match")


def _match_for_user(match: Match, me: int):
    other = match.user2_id if match.user1_id == me else match.user1_id
    return other


@bp.route("/ai", methods=["POST"])
@tenant_required
def ai_match():
    me = jwt_user_id()
    user = User.query.get(me)
    if not user:
        return jsonify({"error": "User not found"}), 404
    candidates = User.query.filter(User.id != me, User.role == ROLE_TENANT).all()
    matches = []
    for candidate in candidates:
        meta = compatibility_with_source(user, candidate)
        matches.append(
            {
                "user": candidate.to_dict(),
                "compatibility_score": meta["score"],
                "scoring_method": meta["source"],
                "clusters": {
                    "you": meta.get("cluster_a"),
                    "them": meta.get("cluster_b"),
                }
                if meta["source"] == "ml"
                else None,
                "trust_scan": ml_inference.trust_scan_for_user(candidate),
            }
        )
    matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return jsonify({"matches": matches[:10]})


@bp.route("/requests", methods=["GET"])
@tenant_required
def match_requests():
    """Pending roommate requests you sent vs received."""
    me = jwt_user_id()
    pending = Match.query.filter(
        Match.status == "pending",
        or_(Match.user1_id == me, Match.user2_id == me),
    ).all()
    incoming = []
    outgoing = []
    for m in pending:
        other_id = _match_for_user(m, me)
        other = User.query.get(other_id)
        row = {**m.to_dict(), "other_user": other.to_public_dict() if other else None}
        if m.initiator_id == me:
            outgoing.append(row)
        else:
            incoming.append(row)
    return jsonify({"incoming": incoming, "outgoing": outgoing})


@bp.route("/my", methods=["GET"])
@tenant_required
def list_my_matches():
    me = jwt_user_id()
    rows = Match.query.filter(or_(Match.user1_id == me, Match.user2_id == me)).order_by(
        Match.matched_on.desc()
    ).all()
    out = []
    for m in rows:
        d = m.to_dict()
        d["other_user_id"] = _match_for_user(m, me)
        out.append(d)
    return jsonify({"matches": out})


@bp.route("/", methods=["POST"])
@tenant_required
def create_match():
    """Send a roommate request (pending until the other user accepts)."""
    me = jwt_user_id()
    data = request.get_json(silent=True) or {}
    other_id = data.get("user2_id")
    if other_id is None:
        return jsonify({"error": "user2_id required"}), 400
    try:
        other_id = int(other_id)
    except (TypeError, ValueError):
        return jsonify({"error": "user2_id must be an integer"}), 400
    if other_id == me:
        return jsonify({"error": "Cannot match with yourself"}), 400
    other = User.query.get(other_id)
    if not other:
        return jsonify({"error": "User not found"}), 404
    if other.role != ROLE_TENANT:
        return jsonify({"error": "You can only send requests to tenant accounts"}), 403

    existing = Match.query.filter(
        or_(
            (Match.user1_id == me) & (Match.user2_id == other_id),
            (Match.user1_id == other_id) & (Match.user2_id == me),
        )
    ).first()
    if existing:
        if existing.status == "rejected":
            db.session.delete(existing)
            db.session.commit()
        else:
            return jsonify({"msg": "Match already exists", "match": existing.to_dict()}), 200

    u1, u2 = (me, other_id) if me < other_id else (other_id, me)
    score = compatibility_with_source(User.query.get(me), other)["score"]
    m = Match(
        user1_id=u1,
        user2_id=u2,
        compatibility_score=float(score),
        status="pending",
        initiator_id=me,
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"msg": "Request sent", "match": m.to_dict()}), 201


@bp.route("/<int:match_id>", methods=["PATCH"])
@tenant_required
def update_match_status(match_id):
    me = jwt_user_id()
    m = Match.query.get(match_id)
    if not m:
        return jsonify({"error": "Match not found"}), 404
    if me not in (m.user1_id, m.user2_id):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("pending", "accepted", "rejected"):
        return jsonify({"error": "status must be pending, accepted, or rejected"}), 400
    m.status = status
    db.session.commit()
    return jsonify({"msg": "Match updated", "match": m.to_dict()})


@bp.route("/<int:match_id>", methods=["DELETE"])
@tenant_required
def delete_match(match_id):
    me = jwt_user_id()
    m = Match.query.get(match_id)
    if not m:
        return jsonify({"error": "Match not found"}), 404
    if me not in (m.user1_id, m.user2_id):
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(m)
    db.session.commit()
    return jsonify({"msg": "Match removed"})


@bp.route("/can-chat/<int:user_id>", methods=["GET"])
@jwt_required()
def can_chat_with(user_id):
    me = jwt_user_id()
    me_user = User.query.get(me)
    if not me_user or get_user_role(me_user) != ROLE_TENANT:
        return jsonify({"can_chat": False, "reason": "tenant_only"})
    if not User.query.get(user_id):
        return jsonify({"error": "User not found"}), 404
    ok = has_accepted_roommate_match(me, user_id)
    return jsonify({"can_chat": ok})
