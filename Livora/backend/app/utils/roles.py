"""Account roles: tenant (roommate flows), owner (listings), admin."""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required

from app.models.user import User
from app.utils.jwt_utils import jwt_user_id

ROLE_TENANT = "tenant"
ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"


def get_user_role(user: User | None) -> str:
    if not user:
        return ROLE_TENANT
    if getattr(user, "role", None) == ROLE_ADMIN or user.is_admin:
        return ROLE_ADMIN
    r = getattr(user, "role", None) or ROLE_TENANT
    return r if r in (ROLE_TENANT, ROLE_OWNER, ROLE_ADMIN) else ROLE_TENANT


def tenant_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(jwt_user_id())
        if not user or get_user_role(user) != ROLE_TENANT:
            return jsonify({"error": "Tenant account required for this feature"}), 403
        return fn(*args, **kwargs)

    return wrapper


def owner_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(jwt_user_id())
        if not user or get_user_role(user) != ROLE_OWNER:
            return jsonify({"error": "Owner account required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(jwt_user_id())
        if not user or get_user_role(user) != ROLE_ADMIN:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def has_accepted_roommate_match(user_a_id: int, user_b_id: int) -> bool:
    from sqlalchemy import and_

    from app.models.match import Match

    u1, u2 = (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)
    return (
        Match.query.filter(
            and_(Match.user1_id == u1, Match.user2_id == u2, Match.status == "accepted")
        ).first()
        is not None
    )
