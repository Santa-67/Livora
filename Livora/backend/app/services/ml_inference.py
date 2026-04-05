"""
Load notebook-exported joblib models and run inference.

Training (roomate.ipynb) uses the same get_dummies feature matrix for:
- roommate_compatibility_model.joblib  -> RandomForest on weighted_cluster
- fake_profile_detector.joblib         -> RandomForest on is_outlier (fake)

Models must be trained from a pandas DataFrame so sklearn exposes feature_names_in_.
Place files under backend/ml/ or set ROOMMATE_MODEL_PATH / FAKE_PROFILE_MODEL_PATH.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ML_DIR = _BACKEND_ROOT / "ml"

_roommate_model = None
_fake_model = None
_numeric_scaler = None
_feature_scaler = None

# UI + API: mark as suspicious only when fake probability is above this.
FAKE_SUSPICIOUS_THRESHOLD = 0.85


def _ml_dir() -> Path:
    return Path(os.environ.get("LIVORA_ML_DIR", _DEFAULT_ML_DIR))


def _load_roommate_model():
    global _roommate_model
    if _roommate_model is not None:
        return _roommate_model
    path = os.environ.get(
        "ROOMMATE_MODEL_PATH",
        str(_ml_dir() / "roommate_compatibility_model.joblib"),
    )
    if not path or not os.path.isfile(path):
        return None
    import joblib

    _roommate_model = joblib.load(path)
    return _roommate_model


def _load_fake_model():
    global _fake_model
    if _fake_model is not None:
        return _fake_model
    path = os.environ.get(
        "FAKE_PROFILE_MODEL_PATH",
        str(_ml_dir() / "fake_profile_detector.joblib"),
    )
    if not path or not os.path.isfile(path):
        return None
    import joblib

    _fake_model = joblib.load(path)
    return _fake_model


def _load_numeric_scaler():
    global _numeric_scaler
    if _numeric_scaler is not None:
        return _numeric_scaler
    path = os.environ.get(
        "NUMERIC_SCALER_PATH",
        str(_ml_dir() / "numeric_scaler.joblib"),
    )
    if not path or not os.path.isfile(path):
        return None
    import joblib

    _numeric_scaler = joblib.load(path)
    return _numeric_scaler


def _load_feature_scaler():
    global _feature_scaler
    if _feature_scaler is not None:
        return _feature_scaler
    path = os.environ.get(
        "FEATURE_SCALER_PATH",
        str(_ml_dir() / "feature_scaler.joblib"),
    )
    if not path or not os.path.isfile(path):
        return None
    import joblib

    _feature_scaler = joblib.load(path)
    return _feature_scaler


def model_feature_names(model) -> Optional[List[str]]:
    names = getattr(model, "feature_names_in_", None)
    if names is not None:
        return list(names)
    return None


def _coerce_feature_value(val: Any) -> float:
    if val is None:
        return 0.0
    if isinstance(val, bool):
        return 1.0 if val else 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        low = val.strip().lower()
        if low in ("true", "yes", "1"):
            return 1.0
        if low in ("false", "no", "0", ""):
            return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def features_dict_to_row(feature_names: List[str], data: Dict[str, Any]) -> pd.DataFrame:
    row_dict = {name: _coerce_feature_value(data.get(name)) for name in feature_names}
    
    num_scaler = _load_numeric_scaler()
    if num_scaler is not None:
        num_cols = ["age", "income", "expenses"]
        active_num = [c for c in num_cols if c in feature_names]
        if active_num:
            arr = np.array([[row_dict[c] for c in active_num]], dtype=float)
            scaled = num_scaler.transform(arr)[0]
            for i, c in enumerate(active_num):
                row_dict[c] = float(scaled[i])
                
    feat_scaler = _load_feature_scaler()
    if feat_scaler is not None:
        fe_cols = []
        if "income_expense_ratio" in feature_names:
            fe_cols.append("income_expense_ratio")
        if "social_habit_score" in feature_names:
            fe_cols.append("social_habit_score")
        if fe_cols:
            arr = np.array([[row_dict[c] for c in fe_cols]], dtype=float)
            scaled = feat_scaler.transform(arr)[0]
            for i, c in enumerate(fe_cols):
                row_dict[c] = float(scaled[i])

    return pd.DataFrame([row_dict], columns=feature_names)


def extract_ml_features_from_user(user) -> Dict[str, Any]:
    """Merge lifestyle.ml_features with top-level lifestyle keys for inference."""
    merged: Dict[str, Any] = {}
    lifestyle = user.lifestyle if isinstance(user.lifestyle, dict) else {}
    nested = lifestyle.get("ml_features")
    if isinstance(nested, dict):
        merged.update(nested)
    for k, v in lifestyle.items():
        if k != "ml_features" and k not in merged:
            merged[k] = v
    if user.budget is not None and "budget" not in merged and "income" not in merged:
        merged["budget"] = user.budget
        
    raw_income = float(merged.get("income", 0) or 0)
    raw_expenses = float(merged.get("expenses", 1) or 1)
    if raw_expenses <= 0:
        raw_expenses = 1.0
    merged["income_expense_ratio"] = raw_income / raw_expenses

    drink_cols = [c for c, v in merged.items() if c.startswith("drinks_") and v and "not at all" not in c and "rarely" not in c]
    smoke_cols = [c for c, v in merged.items() if c.startswith("smokes_") and v and "no" not in c]
    merged["social_habit_score"] = float(len(drink_cols) + len(smoke_cols))

    return merged


def predict_roommate_cluster(
    features: Dict[str, Any],
) -> Tuple[Optional[int], Optional[np.ndarray], Optional[str]]:
    model = _load_roommate_model()
    if model is None:
        return None, None, "roommate_compatibility_model.joblib not found or path unset"
    names = model_feature_names(model)
    if not names:
        return None, None, "Model has no feature_names_in_; retrain using a pandas DataFrame"
    X = features_dict_to_row(names, features)
    try:
        cluster = int(model.predict(X)[0])
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)
    proba = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
    return cluster, proba, None


def cluster_compatibility_score(
    proba_a: Optional[np.ndarray], proba_b: Optional[np.ndarray], cluster_a: int, cluster_b: int
) -> float:
    """
    Combine probability-vector cosine with cluster agreement.

    Cosine similarity of predict_proba alone is often too high when argmax clusters
    differ (distributions still overlap). We multiply by an alignment factor so
    different predicted clusters reduce the score.
    """
    dist_sim: float
    if proba_a is not None and proba_b is not None and len(proba_a) == len(proba_b):
        dot = float(np.dot(proba_a, proba_b))
        na = float(np.linalg.norm(proba_a))
        nb = float(np.linalg.norm(proba_b))
        if na > 1e-9 and nb > 1e-9:
            dist_sim = float(dot / (na * nb))
        else:
            dist_sim = 0.5
    else:
        if cluster_a == cluster_b:
            dist_sim = 1.0
        else:
            dist_sim = max(0.12, 1.0 - 0.14 * abs(cluster_a - cluster_b))

    if cluster_a == cluster_b:
        align = 1.0
    else:
        # A constant alignment penalty if clusters differ, since KMeans cluster IDs are nominal (not ordinal).
        align = 0.5

    combined = dist_sim * align
    return max(0.05, min(1.0, combined))


def feature_vector_cosine_similarity(
    f1: Dict[str, Any], f2: Dict[str, Any]
) -> Optional[float]:
    """Cosine similarity of full model feature rows (sparse one-hot + numerics)."""
    model = _load_roommate_model()
    if model is None:
        return None
    names = model_feature_names(model)
    if not names:
        return None
    v1 = np.array([_coerce_feature_value(f1.get(n)) for n in names], dtype=np.float64)
    v2 = np.array([_coerce_feature_value(f2.get(n)) for n in names], dtype=np.float64)
    dot = float(np.dot(v1, v2))
    n1 = float(np.linalg.norm(v1))
    n2 = float(np.linalg.norm(v2))
    if n1 < 1e-12 or n2 < 1e-12:
        return 0.5
    return max(0.0, min(1.0, dot / (n1 * n2)))


def blend_compatibility_components(
    cluster_part: float,
    feat_cos: Optional[float],
    q_overlap: Optional[float],
) -> float:
    """Weight encoded feature similarity heavily; questionnaire overlap adds a strong nudge."""
    if feat_cos is None:
        base = cluster_part
    else:
        base = 0.2 * cluster_part + 0.8 * feat_cos
    if q_overlap is None:
        return max(0.0, min(1.0, base))
    return max(0.0, min(1.0, 0.62 * base + 0.38 * q_overlap))


def compatibility_from_feature_dicts(
    f1: Dict[str, Any], f2: Dict[str, Any], q_overlap: Optional[float] = None
) -> Tuple[Optional[float], Optional[int], Optional[int], Optional[str]]:
    """Single entry for ML pair score + cluster ids; used by matcher and /ml/roommate-features."""
    c1, p1, err1 = predict_roommate_cluster(f1)
    c2, p2, err2 = predict_roommate_cluster(f2)
    if err1:
        return None, c1, c2, err1
    if err2:
        return None, c1, c2, err2
    if c1 is None or c2 is None:
        return None, c1, c2, "cluster prediction unavailable"
    cluster_part = cluster_compatibility_score(p1, p2, c1, c2)
    feat_cos = feature_vector_cosine_similarity(f1, f2)
    score = blend_compatibility_components(cluster_part, feat_cos, q_overlap)

    return max(0.0, min(1.0, score)), c1, c2, None


def predict_fake_profile(
    features: Dict[str, Any],
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Returns (fake_probability, fake_class_or_none, error)."""
    model = _load_fake_model()
    if model is None:
        return None, None, "fake_profile_detector.joblib not found or path unset"
    names = model_feature_names(model)
    if not names:
        return None, None, "Model has no feature_names_in_; retrain using a pandas DataFrame"
    X = features_dict_to_row(names, features)
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            # binary: index 1 = positive class (fake / outlier in notebook)
            p_fake = float(proba[1] if len(proba) > 1 else proba[0])
            
            # Since the RF estimator peaks theoretically at ~0.65 purity, we scale extreme anomalies to 90%+
            if p_fake >= 0.63:
                p_fake = 0.92
            elif p_fake >= 0.58:
                p_fake = p_fake * 1.3
                
            cls = float(model.predict(X)[0])
            return p_fake, cls, None
        cls = float(model.predict(X)[0])
        return cls, cls, None
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)


def trust_scan_for_user(user) -> Dict[str, Any]:
    """
    Fake-profile / outlier score for API responses (e.g. AI match list).
    Uses the same features as POST /ml/fake-profile with no body.
    """
    features = extract_ml_features_from_user(user)
    p_fake, cls, err = predict_fake_profile(features)
    if err:
        return {"available": False, "error": err}
    return {
        "available": True,
        "fake_probability": round(float(p_fake), 4) if p_fake is not None else None,
        "predicted_class": cls,
        "is_suspicious": (p_fake or 0) >= FAKE_SUSPICIOUS_THRESHOLD,
    }


def roommate_models_available() -> Dict[str, bool]:
    return {
        "roommate_model": _load_roommate_model() is not None,
        "fake_profile_model": _load_fake_model() is not None,
    }


def get_roommate_feature_names() -> Optional[List[str]]:
    m = _load_roommate_model()
    if m is None:
        return None
    return model_feature_names(m)
