import json

def main():
    path = 'c:/Users/SANTOSH/OneDrive/Desktop/CollegProj/roomate.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
            
        src = "".join(cell['source'])
        
        # Replace hardcoded colab paths
        src = src.replace('/content/', 'c:/Users/SANTOSH/OneDrive/Desktop/CollegProj/')
        
        # 1. Patch Expenses generation
        if "base_expenses =" in src and "0.8" in src:
            new_src = src.replace(
                "base_expenses = (df_encoded['income'] * 0.8) + np.random.normal(loc=0, scale=0.3, size=len(df_encoded))",
                "base_expenses = (df_encoded['income'] * 0.4) + np.random.normal(loc=0, scale=1.5, size=len(df_encoded))\n# Added higher variance to allow expenses > income"
            )
            # Find the MinMaxScaler range for expenses
            new_src = new_src.replace(
                "scaler = MinMaxScaler(feature_range=(25000, 60000))",
                "scaler = MinMaxScaler(feature_range=(15000, 85000))"
            )
            src = new_src
            
        # 2. Dump numeric scaler
        if "numerical_cols = ['age', 'income', 'expenses']" in src and "df_final[existing_num_cols] = scaler.fit_transform" in src:
            if "joblib.dump(scaler," not in src:
                src += "\nimport joblib\njoblib.dump(scaler, 'numeric_scaler.joblib')\nprint('Saved numeric_scaler.joblib')"
                
        # 3. Dump feature scaler
        if "scaler_fe = StandardScaler()" in src and "df_fe[features_to_standardize] = scaler_fe.fit_transform" in src:
            if "joblib.dump(scaler_fe," not in src:
                src += "\nimport joblib\njoblib.dump(scaler_fe, 'feature_scaler.joblib')\nprint('Saved feature_scaler.joblib')"
                
        cell['source'] = [line + '\n' if not line.endswith('\n') else line for line in src.split('\n') if line]

    with open('c:/Users/SANTOSH/OneDrive/Desktop/CollegProj/roomate_patched.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)

if __name__ == '__main__':
    main()
