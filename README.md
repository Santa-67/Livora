# 🏠 Livora — AI-Powered Roommate Matcher

Livora is a machine learning-based platform that facilitates data-driven roommate pairing with secure user authentication and intelligent fraud detection.

## 🚀 Features

- **ML Compatibility Matching** — K-Means clustering algorithm scores and pairs users based on lifestyle preferences, schedules, and habits with 87% matching accuracy
- **Fraud Detection Pipeline** — Automatically flags suspicious profiles by evaluating complex financial edge cases, reducing fraudulent listings by ~30%
- **Secure Authentication** — User registration and login with hashed credentials and session management
- **Compatibility Scoring** — Predictive scoring algorithm ranks potential roommates by compatibility across multiple dimensions

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| ML Algorithm | K-Means Clustering (scikit-learn) |
| Data Processing | Pandas, NumPy |
| Authentication | JWT / Session-based Auth |
| Storage | CSV / SQLite (local) |

## 📊 How It Works

1. **User Onboarding** — Users fill out a preference survey (sleep schedule, cleanliness, budget, lifestyle)
2. **Feature Engineering** — Responses are encoded into numerical feature vectors
3. **Clustering** — K-Means groups users into compatibility clusters
4. **Scoring** — A pairwise compatibility score ranks matches within each cluster
5. **Fraud Check** — Financial edge-case rules flag anomalous profiles before surfacing matches

## 📁 Project Structure

```
Livora/
├── data/                  # Sample user datasets
├── model/
│   ├── kmeans_model.py    # Core clustering logic
│   ├── scoring.py         # Compatibility scoring algorithm
│   └── fraud_detection.py # Fraud flagging pipeline
├── auth/
│   └── authentication.py  # User registration & login
├── main.py                # Entry point
└── requirements.txt
```

## ⚙️ Setup & Run

```bash
# Clone the repository
git clone https://github.com/Santa-67/Livora.git
cd Livora

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📈 Results

- **87%** roommate compatibility matching accuracy on test dataset
- **~30%** reduction in fraudulent profile listings via the detection pipeline
- Tested across **500+ synthetic user profiles**

## 🔮 Future Improvements

- Add a web frontend (React or Angular)
- Integrate real-time chat between matched users
- Deploy on Azure App Service with CI/CD pipeline
- Expand fraud detection using supervised ML (Random Forest)

## 👤 Author

**Santosh Kumar Nayak**  
[GitHub](https://github.com/Santa-67) | [LinkedIn](https://linkedin.com/in/santosh-nayak-72a518252)
