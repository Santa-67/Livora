import sys
sys.path.insert(0, './backend')
from app import create_app
app = create_app()
app.app_context().push()

from app.services.ml_inference import predict_fake_profile, extract_ml_features_from_user

class U: pass

with open('test_output.txt', 'w') as f:
    def test_combination(age, income, expenses):
        u = U()
        u.budget=15000
        u.lifestyle={
            'income': income,
            'expenses': expenses, 
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
            'age': age
        }
        feat = extract_ml_features_from_user(u)
        p, _, _ = predict_fake_profile(feat)
        f.write(f"Age: {age}, Income: {income}, Expenses: {expenses} => Fake Prob: {p:.2%}\n")

    test_combination(21, 10000000, 1)
    test_combination(-50, 1000000000, 0)
    test_combination(150, -50000, -10000)
    test_combination(0, 0, 0)
    test_combination(21, 50000, 420000)
    test_combination(22, 67000, 420000)
    test_combination(100, 1000000, 1)
