"""
Populate the DB with many varied tenant/owner users and Indian-city listings (dev/demo).

Run: flask seed-diverse
"""
from __future__ import annotations

import itertools
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

from app import db
from app.models.property import Property
from app.models.user import User
from app.utils.roles import ROLE_OWNER, ROLE_TENANT

SEED_PASSWORD = "LivoraSeed2026!"

# (slug, human location snippet for property.location)
INDIAN_CITIES: List[Tuple[str, str]] = [
    ("mumbai", "Bandra West, Mumbai"),
    ("delhi", "South Extension, New Delhi"),
    ("bangalore", "Koramangala, Bengaluru"),
    ("hyderabad", "Hitech City, Hyderabad"),
    ("chennai", "Adyar, Chennai"),
    ("kolkata", "Salt Lake, Kolkata"),
    ("pune", "Kothrud, Pune"),
    ("ahmedabad", "Navrangpura, Ahmedabad"),
    ("jaipur", "C-Scheme, Jaipur"),
    ("indore", "Vijay Nagar, Indore"),
    ("kochi", "Kakkanad, Kochi"),
    ("chandigarh", "Sector 17, Chandigarh"),
]

FIRST_NAMES = [
    "Aarav",
    "Vihaan",
    "Aditya",
    "Ishaan",
    "Kabir",
    "Ananya",
    "Diya",
    "Kavya",
    "Meera",
    "Priya",
    "Rahul",
    "Sneha",
    "Arjun",
    "Neha",
    "Karan",
    "Pooja",
    "Vikram",
    "Shruti",
    "Manish",
    "Riya",
    "Siddharth",
    "Tanvi",
    "Harsh",
    "Divya",
]

DRINKS = ["not at all", "rarely", "socially", "often", "very often"]
SMOKES = ["no", "sometimes", "when drinking", "trying to quit", "yes"]
PETS = ["no", "likes dogs", "likes cats", "has dogs", "has cats"]
DIETS = ["anything", "vegetarian", "vegan", "halal", "strictly other"]
EDU = [
    "high school",
    "working on college/university",
    "graduated from college/university",
    "graduated from masters program",
]
BODY = ["thin", "average", "athletic", "a little extra", "full figured"]
ORI = ["straight", "gay", "bisexual"]
STAT = ["single", "available", "seeing someone"]

PROPERTY_TEMPLATES = [
    "Coliving room in {}",
    "2 BHK shared flat · {}",
    "Furnished single near metro · {}",
    "Student-friendly PG-style · {}",
    "Quiet lane, gated society · {}",
]


def _questionnaire_row(i: int) -> Dict[str, Any]:
    city_slug, _city_label = INDIAN_CITIES[i % len(INDIAN_CITIES)]
    g = "m" if (i // 3) % 2 == 0 else "f"
    age = 20 + (i % 15)
    income = 18000 + (i * 1733) % 120000
    expenses = max(8000, income - 5000 - (i * 401) % 20000)
    return {
        "age": age,
        "income": income,
        "expenses": expenses,
        "social_habit_score": round(0.05 + (i % 19) * 0.05, 2),
        "drinks": DRINKS[i % len(DRINKS)],
        "smokes": SMOKES[i % len(SMOKES)],
        "pets": PETS[i % len(PETS)],
        "diet": DIETS[i % len(DIETS)],
        "education": EDU[i % len(EDU)],
        "body_type": BODY[i % len(BODY)],
        "sex": g,
        "orientation": ORI[i % len(ORI)],
        "status": STAT[i % len(STAT)],
        "region": city_slug,
    }


def _tenant_bio(i: int, city: str) -> str:
    lines = [
        f"Working professional looking for a tidy flatmate in {city}.",
        "Prefer veg kitchen, no smoking indoors.",
        "Night owl but quiet after 11pm.",
        "Weekend travel, weekday WFH.",
        "Pet-friendly if the pet is trained.",
    ]
    return f"{lines[i % len(lines)]} {lines[(i + 2) % len(lines)]}"


def _upsert_user(
    email: str,
    name: str,
    role: str,
    *,
    gender: str | None,
    budget: int | None,
    lifestyle: dict | None,
    bio: str | None = None,
) -> User:
    u = User.query.filter_by(email=email).first()
    if u:
        u.name = name
        u.role = role
        u.is_admin = False
        u.set_password(SEED_PASSWORD)
        if gender is not None:
            u.gender = gender
        if budget is not None:
            u.budget = budget
        if lifestyle is not None:
            u.lifestyle = lifestyle
        if bio is not None:
            u.bio = bio
        return u
    u = User(
        email=email,
        name=name,
        role=role,
        is_admin=False,
        gender=gender,
        budget=budget,
        lifestyle=lifestyle,
        bio=bio,
    )
    u.set_password(SEED_PASSWORD)
    db.session.add(u)
    return u


def run_seed_diverse() -> None:
    """Create/update many tenants, several owners, and listings across Indian cities."""
    n_tenants = 36
    for i in range(n_tenants):
        idx = i + 1
        email = f"seed.t{idx:02d}@livora.local"
        name = FIRST_NAMES[i % len(FIRST_NAMES)] + f" {idx}"
        q = _questionnaire_row(i)
        city_slug, city_human = INDIAN_CITIES[i % len(INDIAN_CITIES)]
        gender = "male" if q["sex"] == "m" else "female"
        budget = int(q["expenses"]) + (i % 5) * 1000
        lifestyle = {
            "questionnaire": q,
            "seed_meta": {"batch": "diverse", "index": idx, "city": city_slug},
        }
        _upsert_user(
            email,
            name,
            ROLE_TENANT,
            gender=gender,
            budget=budget,
            lifestyle=lifestyle,
            bio=_tenant_bio(i, city_human),
        )

    n_owners = 8
    owner_emails = [f"seed.o{k + 1:02d}@livora.local" for k in range(n_owners)]
    for j in range(n_owners):
        email = owner_emails[j]
        name = f"Owner {FIRST_NAMES[(j + 5) % len(FIRST_NAMES)]}"
        _upsert_user(email, name, ROLE_OWNER, gender=None, budget=None, lifestyle=None, bio=None)
    db.session.flush()

    prop_cycle = itertools.cycle(range(len(PROPERTY_TEMPLATES)))
    pid = 0
    for email in owner_emails:
        ow = User.query.filter_by(email=email).first()
        if not ow:
            continue
        base = (ow.id or 0) % len(INDIAN_CITIES)
        for k in range(3):
            ci = (base + k * 3) % len(INDIAN_CITIES)
            city_slug, city_snip = INDIAN_CITIES[ci]
            rent = 8000 + (pid * 733) % 35000
            area = 350 + (pid * 97) % 3200
            beds = 1 + (pid % 3)
            baths = 1 + (pid % 2)
            furn = pid % 3
            tmpl = PROPERTY_TEMPLATES[next(prop_cycle)].format(city_snip.split(",")[0])
            title = f"{tmpl} · #{pid + 1}"
            desc = (
                f"Verified-style listing for coliving in {city_snip}. "
                f"Near metro and markets. Power backup, water 24x7. "
                f"Preference: working professionals. ₹{rent}/month negotiable."
            )
            existing = Property.query.filter_by(owner_id=ow.id, title=title).first()
            if existing:
                existing.description = desc
                existing.rent = rent
                existing.location = f"{city_snip}, India"
                existing.available = True
                existing.housing_meta = {
                    "area": area,
                    "bedrooms": beds,
                    "bathrooms": baths,
                    "furnishing": furn,
                    "region": city_slug,
                }
            else:
                p = Property(
                    owner_id=ow.id,
                    title=title,
                    description=desc,
                    rent=rent,
                    location=f"{city_snip}, India",
                    available=True,
                    housing_meta={
                        "area": area,
                        "bedrooms": beds,
                        "bathrooms": baths,
                        "furnishing": furn,
                        "region": city_slug,
                    },
                )
                db.session.add(p)
            pid += 1

    tenants = User.query.filter(User.email.like("seed.t%")).all()
    for i, u in enumerate(tenants):
        if u.role == ROLE_TENANT:
            u.move_in_date = date.today() + timedelta(days=7 + (i % 60))

    db.session.commit()
