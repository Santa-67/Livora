from flask import Blueprint, jsonify, request

from app import db
from app.models.user import User
from app.services import ml_inference
from app.utils.roles import tenant_required
from app.services.questionnaire_features import (
    build_features_from_questionnaire,
    questionnaire_field_hints,
)
from app.utils.jwt_utils import jwt_user_id

bp = Blueprint("ml", __name__, url_prefix="/ml")


@bp.route("/health-models", methods=["GET"])
def health_models():
    """Which joblib files are loaded successfully (no auth)."""
    names = ml_inference.get_roommate_feature_names()
    out = ml_inference.roommate_models_available()
    out["roommate_feature_count"] = len(names) if names else 0
    out["fake_suspicious_threshold"] = ml_inference.FAKE_SUSPICIOUS_THRESHOLD
    return jsonify(out)


@bp.route("/questionnaire-schema", methods=["GET"])
def questionnaire_schema():
    """Form hints for the Livora UI (no auth)."""
    return jsonify(questionnaire_field_hints())


@bp.route("/apply-questionnaire", methods=["POST"])
@tenant_required
def apply_questionnaire():
    """
    Build ml_features from questionnaire answers using trained model column names,
    merge into user.lifestyle, persist. Required for ML compatibility + fake check.
    """
    user = User.query.get(jwt_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body required"}), 400

    names = ml_inference.get_roommate_feature_names()
    if not names:
        return jsonify(
            {
                "error": "Roommate model not loaded. Copy roommate_compatibility_model.joblib into backend/ml/",
            }
        ), 503

    vec = build_features_from_questionnaire(data, names)
    lifestyle = dict(user.lifestyle or {})
    lifestyle["ml_features"] = vec
    lifestyle["questionnaire"] = {k: data.get(k) for k in data if k in data}
    user.lifestyle = lifestyle
    if data.get("income") is not None:
        try:
            user.budget = int(float(data["income"]))
        except (TypeError, ValueError):
            pass
    db.session.commit()

    nonzero = sum(1 for v in vec.values() if float(v) != 0.0)
    return jsonify(
        {
            "msg": "Lifestyle vector saved for ML matching",
            "features_total": len(vec),
            "features_nonzero": nonzero,
        }
    )


@bp.route("/fake-profile", methods=["POST"])
@tenant_required
def fake_profile_check():
    """
    Body: optional flat feature dict (same columns as notebook get_dummies output).
    If omitted, uses current user's lifestyle.ml_features + lifestyle keys.
    """
    data = request.get_json(silent=True) or {}
    features = data.get("features")
    if features is None:
        user = User.query.get(jwt_user_id())
        if not user:
            return jsonify({"error": "User not found"}), 404
        features = ml_inference.extract_ml_features_from_user(user)
    if not isinstance(features, dict):
        return jsonify({"error": "features must be a JSON object"}), 400

    p_fake, cls, err = ml_inference.predict_fake_profile(features)
    if err:
        return jsonify({"error": err, "features_received": len(features)}), 503

    return jsonify(
        {
            "fake_probability": p_fake,
            "predicted_class": cls,
            "is_suspicious": (p_fake or 0) >= ml_inference.FAKE_SUSPICIOUS_THRESHOLD,
            "suspicious_threshold": ml_inference.FAKE_SUSPICIOUS_THRESHOLD,
        }
    )


@bp.route("/roommate-features", methods=["POST"])
@tenant_required
def roommate_from_features():
    """
    Score compatibility between two feature vectors (for testing / custom clients).
    Body: {"features_a": {...}, "features_b": {...}}
    """
    data = request.get_json(silent=True) or {}
    fa = data.get("features_a")
    fb = data.get("features_b")
    if not isinstance(fa, dict) or not isinstance(fb, dict):
        return jsonify({"error": "features_a and features_b objects required"}), 400

    score, ca, cb, err = ml_inference.compatibility_from_feature_dicts(fa, fb, q_overlap=None)
    if err:
        return jsonify({"error": err}), 503
    return jsonify(
        {
            "compatibility_score": round(score or 0.0, 4),
            "cluster_a": ca,
            "cluster_b": cb,
        }
    )


@bp.route("/my-cluster", methods=["GET"])
@tenant_required
def my_cluster():
    """Predict lifestyle cluster for the logged-in user from stored ml_features."""
    user = User.query.get(jwt_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    features = ml_inference.extract_ml_features_from_user(user)
    cluster, proba, err = ml_inference.predict_roommate_cluster(features)
    if err:
        return jsonify({"error": err, "hint": "Populate user.lifestyle.ml_features with notebook columns"}), 503
    out = {"cluster": cluster, "feature_count": len(features)}
    if proba is not None:
        out["cluster_probabilities"] = [round(float(x), 4) for x in proba.tolist()]
    return jsonify(out)
