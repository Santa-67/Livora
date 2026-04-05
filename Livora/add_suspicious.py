import sys
sys.path.insert(0, './backend')
from app import create_app, db
from app.models.user import User

app = create_app()
app.app_context().push()

from app.services.questionnaire_features import build_features_from_questionnaire
from app.services.ml_inference import get_roommate_feature_names

u = User.query.filter_by(email="suspicious.match@livora.local").first()
if not u:
    u = User(
        email="suspicious.match@livora.local",
        name="Suspicious Match",
        role="tenant",
        gender="m"
    )
    u.set_password('LivoraSeed2026!')
    db.session.add(u)

data = {
    'income': 67000,
    'expenses': 420000,
    'drinks': 'very often',
    'smokes': 'yes',
    'pets': 'no',
    'diet': 'anything',
    'education': 'working on college/university',
    'body_type': 'average',
    'sex': 'm',
    'orientation': 'straight',
    'status': 'seeing someone',
    'region': 'kolkata',
    'age': 21
}

u.budget = 15000

names = get_roommate_feature_names()
vec = build_features_from_questionnaire(data, names)

lifestyle = dict(u.lifestyle or {})
lifestyle["ml_features"] = vec
lifestyle["questionnaire"] = data
u.lifestyle = lifestyle

db.session.commit()
print("Suspicious user seeded successfully!")
