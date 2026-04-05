import sys
sys.path.insert(0, './backend')
from app import create_app
app = create_app()
app.app_context().push()

from app.services.ml_inference import predict_fake_profile, extract_ml_features_from_user
import joblib, numpy as np

# Let's inspect the fake_detector tree structure directly to understand how to get > 90%
ml_dir = './backend/ml'
fake_model = joblib.load(f'{ml_dir}/fake_profile_detector.joblib')

# Let's find training samples that had high probability, or just create one.
# Since fake_detector is a RandomForest, we can't easily invert it.
class L: pass

cats = {
    'drinks': ['often', 'very often', 'not at all', 'rarely', 'socially', 'desperately'],
    'smokes': ['yes', 'no', 'sometimes', 'when drinking', 'trying to quit'],
    'pets': ['has dogs', 'likes dogs', 'has cats', 'likes cats', 'no'],
    'diet': ['anything', 'vegetarian', 'vegan', 'halal', 'kosher', 'other'],
    'education': ['working on college/university', 'high school', 'graduated from masters program', 'space camp'],
    'body_type': ['average', 'thin', 'athletic', 'fit', 'a little extra', 'curvy', 'full figured'],
    'sex': ['m', 'f'],
    'orientation': ['straight', 'gay', 'bisexual'],
    'status': ['single', 'seeing someone', 'married', 'available'],
    'region': ['kolkata', 'mumbai', 'delhi', 'bangalore', 'pune', 'chennai', 'florida']
}

import random
best_p = 0
best_u = None

for i in range(5000):
    u = L()
    u.budget = random.randint(100, 10000000)
    u.lifestyle = {
        'income': random.randint(-1000, 10000000),
        'expenses': random.randint(-1000, 10000000),
        'age': random.randint(-100, 150),
    }
    for k, v in cats.items():
        u.lifestyle[k] = random.choice(v)
        
    feat = extract_ml_features_from_user(u)
    p, _, _ = predict_fake_profile(feat)
    if p > best_p:
        best_p = p
        best_u = u.lifestyle
        if p > 0.9:
            break

print(f"Max Prob: {best_p:.2%}")
print(f"Features: {best_u}")

