from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models.property import Property
from app.models.user import User
from app.schemas.user_schema import UserSchema
from app.utils.jwt_utils import jwt_user_id
from app.utils.pagination import paginate_query, pagination_meta
from app.utils.validators import sanitize_text

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = jwt_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = jwt_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    schema = UserSchema(partial=True)
    try:
        schema.load(data, instance=user, partial=True)
    except Exception as e:
        return jsonify({"error": "Validation failed", "details": str(e)}), 422
    if "bio" in data:
        user.bio = sanitize_text(user.bio, max_length=500)
    if "name" in data:
        user.name = sanitize_text(user.name, max_length=100)
    db.session.commit()
    return jsonify({"msg": "Profile updated", "user": user.to_dict()})


@bp.route("/browse", methods=["GET"])
@jwt_required()
def browse_users():
    me = jwt_user_id()
    q = User.query.filter(User.id != me)
    name_q = request.args.get("q")
    if name_q:
        q = q.filter(User.name.ilike(f"%{name_q}%"))
    gender = request.args.get("gender")
    if gender:
        q = q.filter_by(gender=gender)
    q = q.order_by(User.created_at.desc())
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        return jsonify({"error": "page and per_page must be integers"}), 400
    items, total, page, per_page = paginate_query(q, page, per_page, max_per_page=50)
    return jsonify(
        {
            "users": [u.to_public_dict() for u in items],
            "meta": pagination_meta(total, page, per_page),
        }
    )


@bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def public_profile(user_id):
    me = jwt_user_id()
    u = User.query.get(user_id)
    if not u:
        return jsonify({"error": "User not found"}), 404
    payload = u.to_public_dict()
    if user_id == me:
        payload = u.to_dict()
    return jsonify({"user": payload})


@bp.route("/favorites", methods=["GET"])
@jwt_required()
def list_favorites():
    user = User.query.get(jwt_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    ids = list(user.favorites or [])
    if request.args.get("expand") == "properties":
        if ids:
            props = Property.query.filter(Property.id.in_(ids)).all()
        else:
            props = []
        return jsonify({"property_ids": ids, "properties": [p.to_dict() for p in props]})
    return jsonify({"property_ids": ids})


@bp.route("/favorites/property/<int:pid>", methods=["POST"])
@jwt_required()
def add_favorite_property(pid):
    user = User.query.get(jwt_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not Property.query.get(pid):
        return jsonify({"error": "Property not found"}), 404
    fav = list(user.favorites or [])
    if pid not in fav:
        fav.append(pid)
        user.favorites = fav
        db.session.commit()
    return jsonify({"msg": "Added to favorites", "property_ids": user.favorites})


@bp.route("/favorites/property/<int:pid>", methods=["DELETE"])
@jwt_required()
def remove_favorite_property(pid):
    user = User.query.get(jwt_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    fav = [x for x in (user.favorites or []) if x != pid]
    user.favorites = fav
    db.session.commit()
    return jsonify({"msg": "Removed from favorites", "property_ids": user.favorites})
