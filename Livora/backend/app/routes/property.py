from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from app.models.property import Property
from app.models.user import User
from app.schemas.property_schema import PropertySchema
from app.services import listing_recommendation, ml_inference
from app.utils.jwt_utils import jwt_user_id
from app.utils.pagination import paginate_query, pagination_meta
from app.utils.roles import ROLE_ADMIN, ROLE_OWNER, get_user_role, tenant_required
from app.utils.validators import sanitize_text

bp = Blueprint("property", __name__, url_prefix="/property")


@bp.route("/recommended", methods=["GET"])
@tenant_required
def list_recommended():
    """Tenant-only: filter by Lifestyle ML region + rank like roomate.ipynb refined_housing_engine."""
    me = jwt_user_id()
    user = User.query.get(me)
    if not user:
        return jsonify({"error": "User not found"}), 404

    feats = ml_inference.extract_ml_features_from_user(user)
    p_fake, _, err = ml_inference.predict_fake_profile(feats)
    if err is None and p_fake is not None and p_fake >= ml_inference.FAKE_SUSPICIOUS_THRESHOLD:
        return jsonify(
            {
                "error": "Listing access restricted for high-risk profiles.",
                "properties": [],
                "meta": {"page": 1, "pages": 0, "total": 0},
            }
        ), 403

    region_slug = listing_recommendation.user_region_from_lifestyle(user.lifestyle)
    all_available = Property.query.filter_by(available=True).all()
    filtered = [p for p in all_available if listing_recommendation.property_matches_region(p, region_slug)]
    q = user.lifestyle or {}
    nested = q.get("questionnaire") if isinstance(q, dict) else {}
    exp = nested.get("expenses") if isinstance(nested, dict) else None
    try:
        exp_f = float(exp) if exp is not None else None
    except (TypeError, ValueError):
        exp_f = None

    ranked = listing_recommendation.rank_properties_for_user(user.budget, exp_f, filtered)

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        return jsonify({"error": "page and per_page must be integers"}), 400
    start = (page - 1) * per_page
    slice_ = ranked[start : start + per_page]
    total = len(ranked)
    pages = max(1, (total + per_page - 1) // per_page) if total else 0

    out = []
    for prop, score in slice_:
        d = prop.to_dict()
        d["recommendation_score"] = round(score, 4)
        out.append(d)

    return jsonify(
        {
            "properties": out,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "region_filter": region_slug or None,
            },
        }
    )


@bp.route("/", methods=["GET"])
def list_properties():
    args = request.args
    query = Property.query
    if "location" in args:
        query = query.filter(Property.location.ilike(f"%{args['location']}%"))
    if "rent_max" in args:
        try:
            query = query.filter(Property.rent <= int(args["rent_max"]))
        except (TypeError, ValueError):
            return jsonify({"error": "rent_max must be an integer"}), 400
    if "rent_min" in args:
        try:
            query = query.filter(Property.rent >= int(args["rent_min"]))
        except (TypeError, ValueError):
            return jsonify({"error": "rent_min must be an integer"}), 400
    if "gender_preference" in args:
        query = query.filter_by(gender_preference=args["gender_preference"])
    if "available" in args:
        query = query.filter_by(available=args.get("available", "true").lower() == "true")
    if "owner_id" in args:
        try:
            query = query.filter_by(owner_id=int(args["owner_id"]))
        except (TypeError, ValueError):
            return jsonify({"error": "owner_id must be an integer"}), 400
    if "verified_only" in args and args.get("verified_only", "").lower() in ("1", "true", "yes"):
        query = query.filter_by(is_verified=True)
    query = query.order_by(Property.created_at.desc())
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
    except (TypeError, ValueError):
        return jsonify({"error": "page and per_page must be integers"}), 400
    items, total, page, per_page = paginate_query(query, page, per_page)
    return jsonify(
        {
            "properties": [p.to_dict() for p in items],
            "meta": pagination_meta(total, page, per_page),
        }
    )


@bp.route("/mine", methods=["GET"])
@jwt_required()
def my_properties():
    uid = jwt_user_id()
    props = (
        Property.query.filter_by(owner_id=uid)
        .order_by(Property.created_at.desc())
        .all()
    )
    return jsonify({"properties": [p.to_dict() for p in props]})


@bp.route("/", methods=["POST"])
@jwt_required()
def add_property():
    user_id = jwt_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if get_user_role(user) not in (ROLE_ADMIN, ROLE_OWNER):
        return jsonify({"error": "Only owner accounts can create listings"}), 403
    data = request.get_json()
    schema = PropertySchema()
    try:
        prop = schema.load(data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": "Validation failed", "details": str(e)}), 422
    prop.owner_id = user.id
    prop.title = sanitize_text(prop.title, max_length=200)
    prop.description = sanitize_text(prop.description, max_length=5000)
    prop.is_verified = False
    prop.is_featured = False
    if prop.images is None:
        prop.images = []
    if prop.videos is None:
        prop.videos = []
    if prop.amenities is None:
        prop.amenities = []
    if prop.schedule_slots is None:
        prop.schedule_slots = []
    if prop.housing_meta is None:
        prop.housing_meta = {}
    db.session.add(prop)
    db.session.commit()
    return jsonify({"msg": "Property created", "property": prop.to_dict()}), 201


@bp.route("/<int:id>", methods=["GET"])
def get_property(id):
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    return jsonify({"property": prop.to_dict()})


@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_property(id):
    user_id = jwt_user_id()
    user = User.query.get(user_id)
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    if prop.owner_id != user_id and get_user_role(user) != ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json() or {}
    safe = {k: v for k, v in data.items() if k not in ("is_featured", "is_verified")}
    schema = PropertySchema(partial=True)
    try:
        schema.load(safe, instance=prop, partial=True)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": "Validation failed", "details": str(e)}), 422
    if "title" in safe:
        prop.title = sanitize_text(prop.title, max_length=200)
    if "description" in safe:
        prop.description = sanitize_text(prop.description, max_length=5000)
    db.session.commit()
    return jsonify({"msg": "Property updated", "property": prop.to_dict()})


@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_property(id):
    user_id = jwt_user_id()
    user = User.query.get(user_id)
    prop = Property.query.get(id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404
    if prop.owner_id != user_id and get_user_role(user) != ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(prop)
    db.session.commit()
    return jsonify({"msg": "Property deleted"})
