# AI-based roommate matching logic
from __future__ import annotations

from typing import Any, Optional

from app.services import ml_inference


def calculate_compatibility(user1, user2):
    """Backward-compatible: returns score only."""
    result = compatibility_with_source(user1, user2)
    return result["score"]


def compatibility_with_source(user1, user2):
    """
    Returns dict: score (0-1), source 'ml' | 'heuristic',
    optional cluster_a/cluster_b when ML used.
    """
    f1 = ml_inference.extract_ml_features_from_user(user1)
    f2 = ml_inference.extract_ml_features_from_user(user2)
    if len(f1) >= 3 and len(f2) >= 3:
        q_overlap = _questionnaire_overlap_ratio(user1, user2)
        score, c1, c2, err = ml_inference.compatibility_from_feature_dicts(f1, f2, q_overlap)
        if err is None and score is not None and c1 is not None and c2 is not None:
            return {
                "score": round(score, 3),
                "source": "ml",
                "cluster_a": c1,
                "cluster_b": c2,
            }

    score = _heuristic_score(user1, user2)
    return {"score": score, "source": "heuristic"}


def _heuristic_score(user1, user2):
    s = 0.0
    total = 0.0

    if user1.budget and user2.budget:
        diff = abs(user1.budget - user2.budget)
        s += max(0, 0.2 - (diff / 10000))
    total += 0.2

    if user1.gender and user2.gender and user1.gender == user2.gender:
        s += 0.1
    total += 0.1

    if user1.move_in_date and user2.move_in_date:
        days = abs((user1.move_in_date - user2.move_in_date).days)
        s += max(0, 0.1 - (days / 60))
    total += 0.1

    l1 = user1.lifestyle or {}
    l2 = user2.lifestyle or {}
    keys = set(l1.keys()) | set(l2.keys())
    keys.discard("ml_features")
    keys.discard("questionnaire")
    if keys:
        matches = sum(1 for k in keys if l1.get(k) == l2.get(k))
        s += 0.6 * (matches / len(keys))
    total += 0.6

    if total <= 0:
        return 0.5
    return round(s / total, 3)


def _qval_equal(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) < 1e-6
    return str(a).strip().lower() == str(b).strip().lower()


def _questionnaire_overlap_ratio(user1, user2) -> Optional[float]:
    """How many saved questionnaire answers match (same keys on both users)."""
    l1 = user1.lifestyle if isinstance(user1.lifestyle, dict) else {}
    l2 = user2.lifestyle if isinstance(user2.lifestyle, dict) else {}
    q1 = l1.get("questionnaire")
    q2 = l2.get("questionnaire")
    if not isinstance(q1, dict) or not isinstance(q2, dict):
        return None
    keys = set(q1.keys()) & set(q2.keys())
    if len(keys) < 4:
        return None
    matches = sum(1 for k in keys if _qval_equal(q1.get(k), q2.get(k)))
    return matches / len(keys)


