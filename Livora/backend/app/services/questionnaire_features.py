"""
Map a simple roommate questionnaire to the flat feature dict expected by joblib models.

Column names must match training (pandas get_dummies on df_final). We set unknown
columns to 0 and fill numerics + category one-hots where names match.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _slug(s: str) -> str:
    return "_".join(str(s).lower().strip().replace("-", " ").split())


# Prefixes commonly produced from OkCupid-style columns after encoding in the notebook
_CATEGORY_PREFIXES = (
    "drinks",
    "smokes",
    "drugs",
    "diet",
    "pets",
    "education",
    "body_type",
    "status",
    "sex",
    "orientation",
    "ethnicity",
    "job",
    "religion",
)


def build_features_from_questionnaire(
    q: Dict[str, Any], feature_names: List[str]
) -> Dict[str, float]:
    vec: Dict[str, float] = {fn: 0.0 for fn in feature_names}

    numeric_keys = (
        "age",
        "income",
        "expenses",
        "income_expense_ratio",
        "social_habit_score",
    )
    for key in numeric_keys:
        if key in feature_names and q.get(key) is not None:
            try:
                vec[key] = float(q[key])
            except (TypeError, ValueError):
                pass

    try:
        inc = float(q.get("income") or 0)
        exp = float(q.get("expenses") or 0)
        if "income_expense_ratio" in feature_names and exp:
            vec["income_expense_ratio"] = inc / max(exp, 1e-6)
    except (TypeError, ValueError):
        pass

    reg = q.get("region")
    region_matched = False
    if reg:
        rs = _slug(reg)
        for fn in feature_names:
            if fn.startswith("region_"):
                suffix = fn[7:]
                if suffix == rs or _slug(suffix.replace("_", " ")) == rs:
                    vec[fn] = 1.0
                    region_matched = True
    if reg and not region_matched and "region_other" in feature_names:
        vec["region_other"] = 1.0

    for cat in _CATEGORY_PREFIXES:
        raw = q.get(cat)
        if raw is None:
            continue
        us = _slug(raw)
        prefix = f"{cat}_"
        for fn in feature_names:
            if not fn.startswith(prefix):
                continue
            col_suffix = fn[len(prefix) :]
            if col_suffix == us:
                vec[fn] = 1.0
                continue
            if _slug(col_suffix.replace("_", " ")) == us:
                vec[fn] = 1.0

    for k, v in q.items():
        if k in vec and isinstance(v, (int, float)):
            try:
                vec[k] = float(v)
            except (TypeError, ValueError):
                pass

    return vec


def questionnaire_field_hints() -> Dict[str, Any]:
    """Default form schema for the Livora UI (values are suggestions, not exhaustive)."""
    return {
        "numeric": [
            {"name": "age", "label": "Age", "min": 18, "max": 80, "step": 1},
            {"name": "income", "label": "Monthly income (₹)", "min": 0, "max": 500000, "step": 500},
            {"name": "expenses", "label": "Monthly expenses (₹)", "min": 0, "max": 500000, "step": 500},
            {
                "name": "social_habit_score",
                "label": "Social habits score (0–1)",
                "min": 0,
                "max": 1,
                "step": 0.05,
            },
        ],
        "select": [
            {
                "name": "drinks",
                "label": "Drinks",
                "options": ["not at all", "rarely", "socially", "often", "very often"],
            },
            {
                "name": "smokes",
                "label": "Smoking",
                "options": ["no", "sometimes", "when drinking", "trying to quit", "yes"],
            },
            {"name": "pets", "label": "Pets", "options": ["no", "likes dogs", "likes cats", "has dogs", "has cats"]},
            {
                "name": "diet",
                "label": "Diet",
                "options": ["anything", "vegetarian", "vegan", "kosher", "halal", "strictly other"],
            },
            {
                "name": "education",
                "label": "Education",
                "options": [
                    "high school",
                    "working on college/university",
                    "graduated from college/university",
                    "graduated from masters program",
                ],
            },
            {
                "name": "body_type",
                "label": "Body type",
                "options": ["thin", "average", "athletic", "a little extra", "full figured"],
            },
            {"name": "sex", "label": "Sex", "options": ["m", "f"]},
            {
                "name": "orientation",
                "label": "Orientation",
                "options": ["straight", "gay", "bisexual"],
            },
            {
                "name": "status",
                "label": "Status",
                "options": ["single", "available", "seeing someone"],
            },
            {
                "name": "region",
                "label": "City / area (India) — listings filter + ML region bucket",
                "options": [
                    "mumbai",
                    "delhi",
                    "bangalore",
                    "hyderabad",
                    "chennai",
                    "kolkata",
                    "pune",
                    "ahmedabad",
                    "jaipur",
                    "indore",
                    "kochi",
                    "chandigarh",
                    "other",
                ],
            },
        ],
    }
