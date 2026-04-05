"""
Region-filtered + distance-ranked listings (aligned with roomate.ipynb refined_housing_engine).

Uses MinMaxScaler + Euclidean distance on [rent, area, bedrooms, bathrooms, furnishing]
with user target built from budget/expenses and cohort medians/modes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler

from app.models.property import Property


def _slug_region(region: Optional[str]) -> str:
    if not region:
        return ""
    return "_".join(str(region).lower().strip().replace("-", " ").split())


def user_region_from_lifestyle(lifestyle: Optional[dict]) -> str:
    if not lifestyle or not isinstance(lifestyle, dict):
        return ""
    q = lifestyle.get("questionnaire")
    if isinstance(q, dict) and q.get("region"):
        return _slug_region(str(q["region"]))
    return ""


def property_matches_region(prop: Property, region_slug: str) -> bool:
    if not region_slug:
        return True
    loc = (prop.location or "").lower()
    meta = prop.housing_meta if isinstance(prop.housing_meta, dict) else {}
    meta_region = str(meta.get("region") or "").lower()
    # Lifestyle questionnaire region slug (e.g. mumbai, bangalore) vs property location + housing_meta.region
    tokens = region_slug.replace("_", " ")
    return tokens in loc or region_slug.replace("_", "") in loc.replace(" ", "") or tokens in meta_region


def _vec_for_property(p: Property) -> List[float]:
    m = p.housing_meta if isinstance(p.housing_meta, dict) else {}
    return [
        float(p.rent),
        float(m.get("area") or 4000),
        float(m.get("bedrooms") or 3),
        float(m.get("bathrooms") or 2),
        float(m.get("furnishing") if m.get("furnishing") is not None else 1.0),
    ]


def rank_properties_for_user(
    user_budget: Optional[int],
    user_expenses_questionnaire: Optional[float],
    candidates: List[Property],
) -> List[Tuple[Property, float]]:
    if not candidates:
        return []

    house_matrix = np.array([_vec_for_property(p) for p in candidates], dtype=np.float64)
    scaler = MinMaxScaler()
    scaled_houses = scaler.fit_transform(house_matrix)

    target_rent = float(user_expenses_questionnaire or user_budget or np.median(house_matrix[:, 0]))
    med_area = float(np.median(house_matrix[:, 1]))
    mode_bed = float(np.median(house_matrix[:, 2]))
    mode_bath = float(np.median(house_matrix[:, 3]))
    user_target = np.array([[target_rent, med_area, mode_bed, mode_bath, 1.0]], dtype=np.float64)
    scaled_target = scaler.transform(user_target)

    distances = euclidean_distances(scaled_target, scaled_houses).flatten()
    scores = 1.0 / (1.0 + distances)

    order = np.argsort(-scores)
    return [(candidates[i], float(scores[i])) for i in order]
