from flask import Blueprint, jsonify, request

from app import db
from app.models.chat import ChatMessage
from app.models.match import Match
from app.models.property import Property
from app.models.user import User
from app.schemas.property_schema import PropertySchema
from app.utils.jwt_utils import jwt_user_id
from app.utils.pagination import paginate_query, pagination_meta
from app.utils.roles import ROLE_ADMIN, ROLE_OWNER, ROLE_TENANT, admin_required
from app.utils.validators import sanitize_text

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    return jsonify(
        {
            "users": User.query.count(),
            "properties": Property.query.count(),
            "chat_messages": ChatMessage.query.count(),
            "matches": Match.query.count(),
        }
    )


@bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    q = User.query.order_by(User.created_at.desc())
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid pagination"}), 400
    items, total, page, per_page = paginate_query(q, page, per_page, max_per_page=100)
    return jsonify(
        {
            "users": [u.to_dict() for u in items],
            "meta": pagination_meta(total, page, per_page),
        }
    )


@bp.route("/properties", methods=["GET"])
@admin_required
def list_properties():
    q = Property.query.order_by(Property.created_at.desc())
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid pagination"}), 400
    items, total, page, per_page = paginate_query(q, page, per_page, max_per_page=100)
    return jsonify(
        {
            "properties": [p.to_dict() for p in items],
            "meta": pagination_meta(total, page, per_page),
        }
    )


@bp.route("/property/<int:id>/verify", methods=["POST"])
@admin_required
def verify_property(id):
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    prop.is_verified = True
    db.session.commit()
    return jsonify({"msg": "Property verified", "property": prop.to_dict()})


@bp.route("/property/<int:id>/unverify", methods=["POST"])
@admin_required
def unverify_property(id):
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    prop.is_verified = False
    db.session.commit()
    return jsonify({"msg": "Property unverified", "property": prop.to_dict()})


@bp.route("/property/<int:id>/feature", methods=["POST"])
@admin_required
def feature_property(id):
    data = request.get_json(silent=True) or {}
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    prop.is_featured = bool(data.get("featured", True))
    db.session.commit()
    return jsonify({"msg": "Property updated", "property": prop.to_dict()})


@bp.route("/user/<int:id>/verify", methods=["POST"])
@admin_required
def verify_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.is_verified = True
    db.session.commit()
    return jsonify({"msg": "User verified", "user": user.to_dict()})


@bp.route("/user/<int:id>/unverify", methods=["POST"])
@admin_required
def unverify_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.is_verified = False
    db.session.commit()
    return jsonify({"msg": "User unverified", "user": user.to_dict()})


@bp.route("/user/<int:id>/remove", methods=["DELETE"])
@admin_required
def remove_user(id):
    if id == jwt_user_id():
        return jsonify({"error": "Cannot remove yourself"}), 400
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User removed"})


@bp.route("/user/<int:id>", methods=["PATCH"])
@admin_required
def admin_patch_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json(silent=True) or {}
    if "role" in data:
        r = str(data["role"]).strip().lower()
        if r not in (ROLE_TENANT, ROLE_OWNER, ROLE_ADMIN):
            return jsonify({"error": "Invalid role"}), 400
        user.role = r
        user.is_admin = r == ROLE_ADMIN
    if "name" in data and data["name"]:
        user.name = sanitize_text(str(data["name"]), max_length=100)
    if "bio" in data:
        user.bio = sanitize_text(str(data.get("bio") or ""), max_length=500) if data.get("bio") else None
    if "budget" in data:
        try:
            user.budget = int(data["budget"]) if data["budget"] is not None else None
        except (TypeError, ValueError):
            return jsonify({"error": "budget must be integer"}), 400
    if "gender" in data:
        user.gender = data["gender"]
    db.session.commit()
    return jsonify({"msg": "User updated", "user": user.to_dict()})


@bp.route("/property/<int:id>", methods=["DELETE"])
@admin_required
def admin_delete_property(id):
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    db.session.delete(prop)
    db.session.commit()
    return jsonify({"msg": "Property deleted"})


@bp.route("/property/<int:id>", methods=["PATCH"])
@admin_required
def admin_patch_property(id):
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    data = request.get_json(silent=True) or {}
    schema = PropertySchema(partial=True)
    try:
        schema.load(data, instance=prop, partial=True)
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": "Validation failed", "details": str(e)}), 422
    if "title" in data:
        prop.title = sanitize_text(prop.title, max_length=200)
    if "description" in data:
        prop.description = sanitize_text(prop.description, max_length=5000)
    db.session.commit()
    return jsonify({"msg": "Property updated", "property": prop.to_dict()})
