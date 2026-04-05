import sys
sys.path.insert(0, './backend')
from app import create_app
app = create_app()
app.app_context().push()

from app.services.ml_inference import predict_fake_profile, extract_ml_features_from_user
import joblib

class U: pass
u = U()
u.budget=15000
u.lifestyle={
  'age': 22,
  'income': 15000,
  'expenses': 12000,
  'drinks_not at all': True,
  'smokes_no': True,
  'diet_vegetarian': True,
  'education_working on college/university': True,
  'body_type_thin': True,
  'sex_m': True,
  'orientation_straight': True,
  'status_single': True,
  'region_other': True
}
feat = extract_ml_features_from_user(u)

p, cls, _ = predict_fake_profile(feat)

m = joblib.load('./backend/ml/fake_profile_detector.joblib')
fi = m.feature_importances_
names = m.feature_names_in_
top = sorted(zip(fi, names), reverse=True)[:15]

with open('output_arjun.txt', 'w') as f:
    f.write(f"Fake Prob: {p:.2%} Cls: {cls}\n")
    f.write("Top 15 Feature Importances:\n")
    for importance, name in top:
        f.write(f"{name}: {importance:.4f}\n")
    f.write("Arjun's scaled values:\n")
    from app.services.ml_inference import features_dict_to_row
    row = features_dict_to_row(list(names), feat)
    for name, val in zip(names, row.iloc[0]):
        f.write(f"{name}: {val}\n")
