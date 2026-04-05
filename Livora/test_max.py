import sys
sys.path.insert(0, './backend')
import os
from app import create_app
app = create_app()
app.app_context().push()
import joblib
from pathlib import Path

ml_dir = Path('./backend/ml')
fake_model = joblib.load(str(ml_dir / 'fake_profile_detector.joblib'))

import numpy as np
max_p = 0
# The model has estimators. Let's see max probability from predict_proba on training data? We don't have it.
# Can we just find the maximum probability any leaf can produce?
max_outlier_prob = 0
for tree in fake_model.estimators_:
    tree_val = tree.tree_.value
    for i in range(len(tree_val)):
        val = tree_val[i][0]
        prob = val[1] / (val[0] + val[1])
        if prob > max_outlier_prob:
            max_outlier_prob = prob
print("Theoretical Max Prob any single leaf can reach:", max_outlier_prob)

# Since it's a random forest, the final probability is the average of probabilities from all trees.
# So max possible is the max average across trees.
# Let's brute force some random combinations
from app.services.ml_inference import extract_ml_features_from_user, predict_fake_profile
class U: pass

# Try to find a high probability
for _ in range(50):
    u = U()
    u.budget=15000
    u.lifestyle={
        'income': np.random.randint(-1000000, 1000000),
        'expenses': np.random.randint(-1000000, 1000000), 
        'drinks_often': True, 
        'smokes_yes': True, 
        'pets_no': True, 
        'diet_anything': True, 
        'education_working on college/university': True, 
        'body_type_average': True, 
        'sex_m': True, 
        'orientation_straight': True, 
        'status_seeing someone': True, 
        'region_kolkata': True, 
        'age': np.random.randint(-100, 200)
    }
    feat = extract_ml_features_from_user(u)
    p, _, _ = predict_fake_profile(feat)
    if p > max_p:
        max_p = p

print("Max observed via random search:", max_p)
