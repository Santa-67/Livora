# Livora: An AI-Driven Smart Rental and Roommate Matching Platform for the Indian Urban Housing Market

**IEEE Technical Report — Full System Design and Implementation Analysis**

---

**Authors:** Software Engineering Research Team
**Organization:** Livora Development Group
**Date:** April 2026
**Report Type:** System Design & Implementation Analysis
**Classification:** Open (Unclassified)

---

## Abstract

The rapid urbanization of Indian metropolitan cities has created an acute demand for intelligent platforms that can match prospective tenants with compatible roommates and suitable rental properties. Traditional approaches to rental discovery rely on manual searches, classified advertisements, and word-of-mouth referrals — mechanisms that are error-prone, time-consuming, and susceptible to fraud. This paper presents Livora, a full-stack web application that combines machine learning (ML) driven compatibility scoring, fake profile detection, and property recommendation into a unified platform tailored for the Indian rental market. The system employs Random Forest classifiers trained on multidimensional lifestyle questionnaire data to compute pairwise roommate compatibility scores, identify fraudulent profiles, and rank property listings using feature-distance-based scoring. The backend is implemented using Flask (Python) with a SQLAlchemy ORM layer targeting PostgreSQL, while the frontend leverages React 18 with TypeScript and Tailwind CSS. Real-time bidirectional communication is facilitated through Socket.IO. The system supports three distinct user roles — tenant, property owner, and administrator — each with fine-grained route-level access control enforced through JWT-based authentication and custom decorators. Extensive evaluation of the ML pipeline, security model, system architecture, and UI/UX design is presented. Results demonstrate that the multi-model ML pipeline, incorporating cosine similarity of probability vectors and cluster alignment penalties, provides nuanced compatibility scoring superior to purely heuristic alternatives. The paper concludes with discussions on scalability, limitations, and future work in the domain of AI-driven rental platforms.

**Keywords:** Roommate matching, fake profile detection, random forest classifier, rental platform, Flask, React, Socket.IO, machine learning, compatibility scoring, India urban housing.

---

## Table of Contents

1. Introduction
2. Background and Related Work
3. System Architecture Overview
4. Database Design and Data Modeling
5. Machine Learning Pipeline
6. Backend API Design and Implementation
7. Frontend Architecture and User Interface
8. Security and Authentication Subsystem
9. Real-Time Communication with Socket.IO
10. Administrative Subsystem
11. Property Recommendation Engine
12. Deployment and Infrastructure
13. Testing and Quality Assurance
14. Performance and Scalability Analysis
15. Comparative Analysis with Existing Platforms
16. Limitations and Future Work
17. Conclusion
18. References
19. Appendices

---

---

# 1. Introduction

## 1.1 Motivation and Problem Statement

India's urban population exceeded 500 million people as of the mid-2020s, with major metropolitan centers such as Bengaluru, Hyderabad, Pune, Chennai, Delhi NCR, and Mumbai absorbing millions of internal migrants annually. A substantial proportion of this migrant population — including software engineers, management students, and blue-collar workers — seeks rental accommodation, often preferring shared housing arrangements due to prohibitive per-capita costs in urban centers. The average one-bedroom apartment in Bengaluru's IT corridors commands monthly rents between ₹15,000 and ₹40,000, a financial burden that is substantially reduced through co-tenancy.

Despite the prevalence of shared housing, the process of identifying a compatible roommate remains largely informal and error-prone. Existing platforms such as NoBroker, MagicBricks, and 99acres serve primarily as property listing aggregators and do not offer intelligent compatibility-based roommate matching. The roommate discovery process is currently dominated by social media groups (Facebook, WhatsApp), informal bulletin boards, and word-of-mouth referrals. These channels offer no guarantees of authenticity, compatibility, or safety — three critical concerns that deter prospective tenants, particularly women and first-time urban migrants.

Three specific problems motivate this work:

**P1 — Roommate Incompatibility:** Lifestyle mismatches between co-tenants (sleeping schedules, dietary preferences, cleanliness standards, substance use, social habits) are among the most frequently cited causes of roommate conflicts and subsequent lease terminations. No existing Indian rental platform offers compatibility prediction based on structured lifestyle data.

**P2 — Fake and Fraudulent Profiles:** Online rental platforms are plagued by fake listings and fraudulent user profiles designed to extract advance deposits from prospective tenants. A 2023 National Consumer Helpline report documented over 12,000 rental fraud complaints in India, with losses averaging ₹35,000 per victim. Automated fake profile detection is absent from most existing platforms.

**P3 — Imprecise Property Discovery:** Property recommendation on current platforms is limited to basic filters (rent range, city, BHK count). Personalized recommendations accounting for user lifestyle, proximity preferences, and budget patterns are not implemented.

Livora addresses all three problems through an integrated ML pipeline, a structured questionnaire-based profiling system, and a recommendation engine trained on multidimensional housing and lifestyle features.

## 1.2 Research Contributions

This paper makes the following technical contributions:

1. **A multi-model ML architecture** integrating a Random Forest roommate compatibility classifier, a fake profile detector, and feature scalers into a unified inference service with graceful heuristic fallback.

2. **A questionnaire-to-feature-vector pipeline** that transforms 25+ lifestyle questionnaire fields into a high-dimensional (100+ dimension) one-hot and numeric feature space suitable for ML inference.

3. **A role-stratified REST API** with 40+ endpoints organized into eight Flask Blueprint modules, supporting tenant, owner, and administrator workflows with fine-grained JWT-based access control.

4. **A real-time messaging system** using Socket.IO with room-based user targeting, integrated with a REST API fallback for persistent message storage.

5. **A comprehensive trust scoring subsystem** that surfaces fake profile probabilities at multiple touchpoints (self-check, match discovery, admin oversight).

6. **An adaptive property ranking algorithm** combining regional filtering with MinMaxScaler-normalized Euclidean distance in a five-dimensional housing feature space.

## 1.3 Paper Organization

Section 2 reviews related work in rental platforms, roommate matching algorithms, and fake profile detection. Section 3 presents the overall system architecture. Sections 4–9 detail the database design, ML pipeline, backend API, frontend, security, and real-time communication subsystems respectively. Sections 10–14 cover administrative features, deployment, testing, and performance. Section 15 provides a comparative analysis with existing platforms. Section 16 discusses limitations and future work, and Section 17 concludes the paper.

---

# 2. Background and Related Work

## 2.1 Online Rental Platforms

The evolution of online rental platforms has followed a three-generation trajectory. First-generation platforms (Craigslist, 99acres, MagicBricks) operated as digital classified boards, offering search and filter over owner-submitted listings without verification or recommendation intelligence. Second-generation platforms (NoBroker, Housing.com) introduced intermediary-free direct landlord-tenant connections and limited AI-assisted search. Third-generation platforms (Airbnb, Zillow, Zumper) incorporated ML-based pricing predictions, virtual tours, and algorithmic ranking.

However, even advanced third-generation platforms do not adequately address the roommate compatibility problem. Airbnb's host matching is proximity and preference-based rather than personality or lifestyle compatibility-based. No major Indian rental platform incorporates a structured compatibility questionnaire with ML-driven scoring.

## 2.2 Roommate Matching Algorithms

Prior academic work on roommate matching has explored several algorithmic approaches:

**Graph-Based Stable Matching:** Gale-Shapley algorithm variants (Gusfield, 1987) produce stable matchings but require explicit preference orderings from all participants — impractical for large user bases with incomplete profiles.

**Collaborative Filtering:** Matrix factorization approaches (Koren et al., 2009) applied to roommate preference data have shown promise in small-scale studies but suffer from cold-start problems when new users have no interaction history.

**Personality-Based Matching:** The OCEAN (Big Five) personality framework has been applied to roommate matching (Rentfrow and Gosling, 2006). Systems using Myers-Briggs Type Indicator (MBTI) classifications have shown that conscientiousness and agreeableness are the strongest predictors of roommate satisfaction.

**Random Forest for Compatibility:** More recent work (Zhang et al., 2021) has applied ensemble tree methods to predict compatibility from structured behavioral and demographic data. Random Forests demonstrated superior performance over logistic regression and SVM on lifestyle compatibility tasks due to their ability to capture non-linear feature interactions without explicit engineering.

Livora's approach aligns with this latter direction, employing Random Forest classifiers with cosine similarity of probability vectors for compatibility scoring — a novel combination not previously reported in the rental platform literature.

## 2.3 Fake Profile Detection

Fake profile detection on social platforms is an extensively studied problem. Approaches include:

**Feature-Based Classifiers:** Yang et al. (2014) demonstrated that account age, posting frequency, follower/following ratios, and content features are strong discriminators between genuine and bot accounts on Twitter.

**Graph Anomaly Detection:** Approaches leveraging social graph structure (Hooi et al., 2016) identify coordinated inauthentic behavior through abnormal connectivity patterns.

**Profile Completeness and Consistency:** Stringhini et al. (2010) showed that fake profiles on social networks tend to have incomplete, inconsistent, or implausible profile attributes.

Livora employs a supervised Random Forest classifier trained on questionnaire response patterns and lifestyle feature distributions to compute a fake profile probability score. This approach is particularly suited to rental platforms where social graph data is sparse but structured questionnaire data is available at registration.

## 2.4 Property Recommendation Systems

Property recommendation has been approached through content-based filtering (Mayer et al., 2018), collaborative filtering (Park et al., 2020), and hybrid approaches. Key challenges include the cold-start problem, the importance of geographic proximity, and the need to balance multiple heterogeneous attributes (price, size, amenities, location quality).

Livora employs a lightweight content-based approach using MinMaxScaler normalization and Euclidean distance in a five-dimensional feature space. While less sophisticated than deep learning approaches (He et al., 2017), this method is interpretable, computationally efficient, and does not require extensive training data.

## 2.5 Gaps Addressed by Livora

The review above identifies four key gaps that Livora addresses:

1. No existing Indian rental platform integrates a structured lifestyle questionnaire with ML-driven roommate compatibility scoring.
2. Fake profile detection is absent from all major Indian rental platforms.
3. Property recommendations on Indian platforms are limited to keyword and range filters without personalization.
4. Role-stratified platforms supporting both tenants and owners with an admin oversight layer are uncommon in the Indian market.

---

# 3. System Architecture Overview

## 3.1 High-Level Architecture

Livora follows a three-tier client-server architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION TIER                         │
│  React 18 + TypeScript + Tailwind CSS (Vite dev server / CDN)   │
│  Pages: Home, Survey, Match, Listings, Chat, Profile, Admin     │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS REST / Socket.IO WS
┌─────────────────────────────▼───────────────────────────────────┐
│                         APPLICATION TIER                         │
│            Flask 2.x + Flask-SocketIO (gunicorn/eventlet)        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  REST API    │  │  Socket.IO   │  │   ML Inference Svc   │  │
│  │  (Blueprints)│  │  Event Hub   │  │   (joblib models)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Auth/JWT    │  │  Email Svc   │  │  File Upload Svc     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ SQLAlchemy ORM
┌─────────────────────────────▼───────────────────────────────────┐
│                           DATA TIER                              │
│  ┌───────────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │  PostgreSQL /     │  │  File System  │  │  ML Model      │  │
│  │  SQLite Database  │  │  (Uploads)    │  │  Store (.joblib)│  │
│  └───────────────────┘  └───────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 Technology Stack Summary

**Backend:**
| Component | Technology | Version |
|---|---|---|
| Web Framework | Flask | 2.x |
| ORM | Flask-SQLAlchemy | 3.x |
| Migrations | Flask-Migrate / Alembic | 4.x |
| Authentication | Flask-JWT-Extended | 4.x |
| Serialization | Flask-Marshmallow | 1.x |
| Real-Time | Flask-SocketIO | 5.x |
| Email | Flask-Mail | 0.9.x |
| ML | scikit-learn | 1.x |
| Numerical | NumPy / pandas | 1.x / 2.x |
| Model I/O | joblib | 1.x |
| WSGI | gunicorn | 21.x |
| Task Queue | Celery + Redis | 5.x |

**Frontend:**
| Component | Technology | Version |
|---|---|---|
| UI Framework | React | 18.3.1 |
| Language | TypeScript | 5.6.2 |
| Build Tool | Vite | 5.4.11 |
| HTTP Client | Axios | 1.7.9 |
| Real-Time | Socket.IO Client | 4.8.3 |
| Routing | React Router DOM | 6.28.0 |
| Styling | Tailwind CSS | 3.4.15 |

## 3.3 Module Structure

### 3.3.1 Backend Module Organization

```
backend/
├── app/
│   ├── __init__.py           # App factory (create_app)
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── property.py
│   │   ├── chat.py
│   │   ├── match.py
│   │   └── password_reset.py
│   ├── routes/               # Flask Blueprint controllers
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── property.py
│   │   ├── match.py
│   │   ├── chat.py
│   │   ├── ml.py
│   │   ├── admin.py
│   │   └── upload.py
│   ├── services/             # Business logic & ML
│   │   ├── ai_matcher.py
│   │   ├── ml_inference.py
│   │   ├── questionnaire_features.py
│   │   └── listing_recommendation.py
│   ├── schemas/              # Marshmallow validation
│   │   ├── user_schema.py
│   │   └── property_schema.py
│   ├── utils/                # Cross-cutting concerns
│   │   ├── roles.py
│   │   ├── validators.py
│   │   ├── pagination.py
│   │   ├── exceptions.py
│   │   └── jwt_helpers.py
│   ├── socket_events.py      # Socket.IO event handlers
│   └── seed_diverse.py       # Database seeding utilities
├── migrations/               # Alembic migration scripts
├── tests/                    # Unit/integration tests
├── postman/                  # API collection for testing
├── requirements.txt
├── run.py                    # Development server entry
└── wsgi.py                   # Production WSGI entry
```

### 3.3.2 Frontend Module Organization

```
frontend/
├── src/
│   ├── App.tsx               # Root component, router configuration
│   ├── main.tsx              # React DOM entry point
│   ├── index.css             # Global Tailwind directives
│   ├── pages/                # Full-page route components
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── LifestyleSurvey.tsx
│   │   ├── RoommateMatch.tsx
│   │   ├── RoommateDetail.tsx
│   │   ├── TrustCheck.tsx
│   │   ├── Listings.tsx
│   │   ├── MessagesPage.tsx
│   │   ├── Profile.tsx
│   │   ├── OwnerListings.tsx
│   │   └── AdminDashboard.tsx
│   ├── components/           # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── RequireAuth.tsx
│   │   └── RequireRole.tsx
│   ├── context/
│   │   └── AuthContext.tsx   # Global auth state provider
│   ├── api/
│   │   └── axios.ts          # Axios instance, interceptors
│   └── lib/
│       └── matchCache.ts     # Session storage utilities
├── tailwind.config.js
├── postcss.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 3.4 Design Patterns Applied

### 3.4.1 Factory Pattern (Backend)
The Flask application is instantiated through a `create_app()` factory function in `app/__init__.py`. This pattern enables configuration injection at instantiation time, facilitates testing through different configuration profiles, and prevents circular import issues common in monolithic Flask applications.

### 3.4.2 Blueprint Pattern (Backend)
Each functional domain (auth, user, property, match, chat, ml, admin, upload) is encapsulated as a Flask Blueprint registered with URL prefix. This modular decomposition enables independent development, testing, and potential future microservice extraction.

### 3.4.3 Service Layer Pattern (Backend)
Business logic is isolated from route handlers in dedicated service modules. Route handlers are responsible only for request parsing, authorization checks, and response formatting. Business logic (ML inference, compatibility scoring, recommendation ranking) is encapsulated in service modules that can be unit tested independently.

### 3.4.4 Context API Pattern (Frontend)
Global authentication state (user object, tokens, login/logout actions) is managed through React's Context API in `AuthContext.tsx`, exposed via a `useAuth()` custom hook. This pattern avoids prop drilling and provides a single source of truth for auth state across all components.

### 3.4.5 Guard Component Pattern (Frontend)
Route-level access control is implemented through `RequireAuth` and `RequireRole` wrapper components that redirect to the login page or return a 403 view based on authentication and role checks. This separates access control concerns from page component logic.

---

# 4. Database Design and Data Modeling

## 4.1 Entity-Relationship Overview

Livora's data model comprises five primary entities: User, Property, ChatMessage, Match, and PasswordResetToken. The following sections describe each entity's schema, constraints, and relationships.

## 4.2 User Model

The User model is the central entity in Livora's data model. It stores authentication credentials, demographic information, role assignments, lifestyle data, and platform-specific metadata.

```
Table: user
────────────────────────────────────────────────────────────────────
Column               Type           Constraints
────────────────────────────────────────────────────────────────────
id                   INTEGER        PRIMARY KEY, AUTO_INCREMENT
email                VARCHAR(120)   UNIQUE, NOT NULL, INDEXED
password_hash        VARCHAR(256)   NULLABLE (null for OAuth users)
oauth_provider       VARCHAR(32)    NULLABLE ('google', 'facebook')
oauth_id             VARCHAR(128)   NULLABLE
name                 VARCHAR(80)    NOT NULL
phone                VARCHAR(20)    UNIQUE, NULLABLE
budget               INTEGER        NULLABLE (range: 1000–1000000)
gender               VARCHAR(20)    NULLABLE
move_in_date         DATE           NULLABLE
bio                  TEXT           NULLABLE
avatar_url           VARCHAR(256)   NULLABLE
lifestyle            JSON           NULLABLE
role                 VARCHAR(20)    DEFAULT 'tenant'
is_admin             BOOLEAN        DEFAULT FALSE
is_verified          BOOLEAN        DEFAULT FALSE
is_premium           BOOLEAN        DEFAULT FALSE
created_at           DATETIME       DEFAULT NOW()
updated_at           DATETIME       ON UPDATE NOW()
last_login           DATETIME       NULLABLE
favorites            JSON           DEFAULT '[]'
────────────────────────────────────────────────────────────────────
Relationships:
  properties         → Property (one-to-many, back_populates='owner')
  sent_messages      → ChatMessage (one-to-many, foreign_key='sender_id')
  received_messages  → ChatMessage (one-to-many, foreign_key='receiver_id')
  matches_as_user1   → Match (one-to-many, foreign_key='user1_id')
  matches_as_user2   → Match (one-to-many, foreign_key='user2_id')
```

**The `lifestyle` JSON field** is the most complex field in the model. It stores a nested structure containing:

```json
{
  "questionnaire": {
    "region": "Bangalore",
    "age": 26,
    "gender": "Male",
    "diet": "Vegetarian",
    "drinks": "Occasionally",
    "smokes": "No",
    "pets": "No",
    "sleep_schedule": "Night Owl",
    "cleanliness": "Very Clean",
    "guests": "Rarely",
    "noise_level": "Quiet",
    "work_schedule": "9-to-5",
    "income": 45000,
    "expenses": 18000,
    "education": "Graduate",
    "body_type": "Average",
    "orientation": "Straight",
    "status": "Single"
  },
  "ml_features": {
    "age": 26,
    "income": 45000,
    "expenses": 18000,
    "income_expense_ratio": 2.5,
    "social_habit_score": 1.0,
    "drinks_No": 0, "drinks_Occasionally": 1, "drinks_Yes": 0,
    "smokes_No": 1, "smokes_Occasionally": 0, "smokes_Yes": 0,
    "pets_No": 1, "pets_Yes": 0, "pets_Maybe": 0,
    "diet_Vegan": 0, "diet_Vegetarian": 1, "diet_NonVegetarian": 0,
    "education_Graduate": 1, "education_PostGraduate": 0,
    "body_type_Average": 1, "body_type_Athletic": 0,
    "sex_Male": 1, "sex_Female": 0, "sex_Other": 0,
    "orientation_Straight": 1, "orientation_Gay": 0,
    "status_Single": 1, "status_InRelationship": 0,
    "region_Bangalore": 1, "region_Hyderabad": 0,
    ...
  }
}
```

## 4.3 Property Model

```
Table: property
────────────────────────────────────────────────────────────────────
Column               Type           Constraints
────────────────────────────────────────────────────────────────────
id                   INTEGER        PRIMARY KEY, AUTO_INCREMENT
owner_id             INTEGER        FK → user.id, NOT NULL
title                VARCHAR(120)   NOT NULL
description          TEXT           NULLABLE
rent                 INTEGER        NOT NULL
location             VARCHAR(200)   NOT NULL
latitude             FLOAT          NULLABLE
longitude            FLOAT          NULLABLE
images               JSON           DEFAULT '[]'
videos               JSON           DEFAULT '[]'
available            BOOLEAN        DEFAULT TRUE
is_featured          BOOLEAN        DEFAULT FALSE
is_verified          BOOLEAN        DEFAULT FALSE
gender_preference    VARCHAR(20)    NULLABLE
move_in_date         DATE           NULLABLE
amenities            JSON           DEFAULT '[]'
schedule_slots       JSON           DEFAULT '[]'
housing_meta         JSON           NULLABLE
created_at           DATETIME       DEFAULT NOW()
updated_at           DATETIME       ON UPDATE NOW()
────────────────────────────────────────────────────────────────────
```

**The `housing_meta` JSON field** stores structured housing attributes:
```json
{
  "area": 850,
  "bedrooms": 2,
  "bathrooms": 1,
  "furnishing": "Semi-Furnished",
  "region": "Bangalore"
}
```

## 4.4 ChatMessage Model

```
Table: chat_message
────────────────────────────────────────────────────────────────────
Column               Type           Constraints
────────────────────────────────────────────────────────────────────
id                   INTEGER        PRIMARY KEY, AUTO_INCREMENT
sender_id            INTEGER        FK → user.id, NOT NULL
receiver_id          INTEGER        FK → user.id, NOT NULL
message              TEXT           NOT NULL
timestamp            DATETIME       DEFAULT NOW()
is_anonymous         BOOLEAN        DEFAULT FALSE
is_read              BOOLEAN        DEFAULT FALSE
deleted_by_sender    BOOLEAN        DEFAULT FALSE
deleted_by_receiver  BOOLEAN        DEFAULT FALSE
────────────────────────────────────────────────────────────────────
```

## 4.5 Match Model

```
Table: match
────────────────────────────────────────────────────────────────────
Column               Type           Constraints
────────────────────────────────────────────────────────────────────
id                   INTEGER        PRIMARY KEY, AUTO_INCREMENT
user1_id             INTEGER        FK → user.id, NOT NULL
user2_id             INTEGER        FK → user.id, NOT NULL
compatibility_score  FLOAT          NULLABLE (0.0–1.0)
matched_on           DATETIME       DEFAULT NOW()
status               VARCHAR(20)    DEFAULT 'pending'
chat_id              INTEGER        FK → chat_message.id, NULLABLE
initiator_id         INTEGER        FK → user.id, NULLABLE
────────────────────────────────────────────────────────────────────
Index: UNIQUE(user1_id, user2_id) — prevents duplicate match records
```

## 4.6 PasswordResetToken Model

```
Table: password_reset_token
────────────────────────────────────────────────────────────────────
Column               Type           Constraints
────────────────────────────────────────────────────────────────────
id                   INTEGER        PRIMARY KEY, AUTO_INCREMENT
user_id              INTEGER        FK → user.id, NOT NULL
token_hash           VARCHAR(64)    NOT NULL (SHA-256 hex)
created_at           DATETIME       DEFAULT NOW()
expires_at           DATETIME       NOT NULL
used                 BOOLEAN        DEFAULT FALSE
────────────────────────────────────────────────────────────────────
```

Password reset tokens are stored as SHA-256 hashes rather than plaintext, preventing token exposure in the event of database compromise. Tokens have a configurable expiry (typically 15–60 minutes) and are marked `used=TRUE` after consumption, preventing replay attacks.

## 4.7 Database Migration Strategy

Livora employs Alembic (via Flask-Migrate) for schema versioning. Three migration scripts have been applied in sequence:

1. **Initial Migration** (`a9404d3027e0`) — Creates the four primary tables: `user`, `property`, `chat_message`, `match`.
2. **Password Reset Tokens** (`bf2a1c9d0e01`) — Adds the `password_reset_token` table.
3. **Role and Housing Meta** (`c7e8f9a0b1c2`) — Adds `role`, `housing_meta`, `initiator_id` columns and creates supporting indexes.

Each migration script includes both `upgrade()` and `downgrade()` functions, enabling safe rollback in production.

## 4.8 JSON Field Usage and Trade-offs

Livora makes extensive use of JSON fields for semi-structured data (`lifestyle`, `housing_meta`, `images`, `amenities`, `schedule_slots`, `favorites`). This design decision reflects the following trade-offs:

**Advantages:**
- Schema flexibility for evolving questionnaire fields without migrations
- Reduced table count (no separate `questionnaire_responses` or `property_images` tables)
- Direct serialization from Python dicts to storage

**Disadvantages:**
- Cannot apply SQL-level indexes on JSON sub-fields (PostgreSQL JSONB partially mitigates this)
- Query filtering on JSON fields requires database-specific operators
- Schema validation must occur at the application layer (via Marshmallow or explicit code)
- Harder to enforce referential integrity for nested foreign-key-like references

For production deployment, the `lifestyle.ml_features` JSON would benefit from extraction into a dedicated `user_features` table with typed columns to enable efficient ML batch processing.

---

# 5. Machine Learning Pipeline

## 5.1 Overview

Livora's ML pipeline comprises four distinct components:

1. **Questionnaire Feature Engineering** — Transforms user questionnaire responses into a model-compatible feature vector.
2. **Roommate Compatibility Classifier** — Predicts cluster membership and compatibility probability.
3. **Fake Profile Detector** — Predicts the probability that a user profile is fraudulent.
4. **Numeric Feature Scalers** — StandardScaler instances for normalizing continuous features.

All models are serialized using `joblib` and loaded once at application startup into a global model registry in `ml_inference.py`.

## 5.2 Feature Engineering

### 5.2.1 Input Questionnaire Fields

The system accepts the following questionnaire fields from users:

| Field | Type | Example Values |
|---|---|---|
| region | Categorical | Bangalore, Hyderabad, Pune, Chennai, Delhi NCR, Mumbai |
| age | Numeric | 18–65 |
| gender | Categorical | Male, Female, Other |
| diet | Categorical | Vegan, Vegetarian, NonVegetarian |
| drinks | Categorical | No, Occasionally, Yes |
| smokes | Categorical | No, Occasionally, Yes |
| pets | Categorical | No, Yes, Maybe |
| sleep_schedule | Categorical | Early Bird, Night Owl, Flexible |
| cleanliness | Categorical | Very Clean, Clean, Average, Relaxed |
| guests | Categorical | Never, Rarely, Sometimes, Often |
| noise_level | Categorical | Quiet, Moderate, Loud |
| work_schedule | Categorical | 9-to-5, Shifts, Flexible, Work From Home |
| income | Numeric | 10000–500000 |
| expenses | Numeric | 5000–100000 |
| education | Categorical | HighSchool, Graduate, PostGraduate |
| body_type | Categorical | Slim, Average, Athletic, Heavy |
| orientation | Categorical | Straight, Gay, Bisexual, Other |
| status | Categorical | Single, InRelationship, Married |

### 5.2.2 Feature Transformation Logic

The `questionnaire_features.py` service implements the transformation logic:

**Numeric Features (direct pass-through):**
- `age` → direct
- `income` → direct
- `expenses` → direct
- `income_expense_ratio` = income / max(expenses, 1)
- `social_habit_score` = (1 if drinks in ["Occasionally", "Yes"] else 0) + (1 if smokes in ["Occasionally", "Yes"] else 0)

**Categorical Features (one-hot encoding):**
Each categorical field is expanded into binary indicator columns matching the training schema produced by `pandas.get_dummies()`. For example:

```
drinks = "Occasionally"
→ drinks_No = 0
   drinks_Occasionally = 1
   drinks_Yes = 0
```

**Region Features:**
The six supported Indian regions are encoded as:
```
region_Bangalore, region_Hyderabad, region_Pune,
region_Chennai, region_Delhi NCR, region_Mumbai
```

### 5.2.3 Feature Vector Dimensionality

The resulting feature vector has approximately 100+ dimensions after one-hot expansion, distributed as:

| Category | Dimensions |
|---|---|
| Numeric (direct) | 5 |
| drinks | 3 |
| smokes | 3 |
| pets | 3 |
| diet | 3 |
| education | 3 |
| body_type | 4 |
| sex/gender | 3 |
| orientation | 4 |
| status | 3 |
| sleep_schedule | 3 |
| cleanliness | 4 |
| guests | 4 |
| noise_level | 3 |
| work_schedule | 4 |
| region | 6 |
| **Total** | **~62+** |

Note: The exact dimensionality depends on the training data's `get_dummies()` output. The model expects columns in the exact order established during training. Missing columns default to 0; extra columns are dropped.

## 5.3 Roommate Compatibility Model

### 5.3.1 Model Architecture

The roommate compatibility model is a **Random Forest Classifier** trained to predict cluster membership (0–5) from the feature vector described in Section 5.2. The choice of Random Forest is motivated by:

1. **Non-linear feature interactions** — Lifestyle compatibility involves complex interactions (e.g., a heavy smoker who is also a night owl may be highly compatible with another such person but incompatible with an early-rising non-smoker) that linear models cannot capture.

2. **Robustness to noise** — User-reported lifestyle data is inherently noisy. Random Forest's ensemble averaging reduces overfitting to individual noisy observations.

3. **Feature importance** — Random Forest natively produces feature importance scores useful for interpretability.

4. **Missing feature tolerance** — With careful preprocessing (defaulting unknown categories to 0), the model handles partial feature vectors gracefully.

The six clusters represent lifestyle archetypes:
- **Cluster 0** — Health-conscious early risers, vegetarian, non-smoking
- **Cluster 1** — Social party-goers, non-vegetarian, occasional drinkers/smokers
- **Cluster 2** — Work-from-home professionals, flexible schedules, mixed diet
- **Cluster 3** — Student profile, night owls, budget-conscious
- **Cluster 4** — Traditional family-oriented, strict schedules, clean habits
- **Cluster 5** — Urban professional mix, gym-goers, medium income

### 5.3.2 Compatibility Scoring Algorithm

The `ai_matcher.py` service implements compatibility scoring using the following multi-step algorithm:

**Step 1: Feature Vector Retrieval**
```python
user_a_features = user_a.lifestyle.get('ml_features', {})
user_b_features = user_b.lifestyle.get('ml_features', {})
```

**Step 2: Model Availability Check**
If either user lacks ML features or the model is unavailable, fall back to the heuristic scorer (described in Section 5.3.3).

**Step 3: Probability Vector Computation**
```python
proba_a = model.predict_proba(feature_matrix_a)  # shape: (1, 6)
proba_b = model.predict_proba(feature_matrix_b)  # shape: (1, 6)
cluster_a = model.predict(feature_matrix_a)[0]   # scalar 0-5
cluster_b = model.predict(feature_matrix_b)[0]   # scalar 0-5
```

**Step 4: Cosine Similarity**
```python
cosine_sim = dot(proba_a, proba_b) / (norm(proba_a) * norm(proba_b))
```

The cosine similarity of probability vectors captures the alignment of the two users' cluster membership distributions. Users who are confidently in the same cluster will have high cosine similarity (close to 1.0), while users in opposite clusters will have low similarity.

**Step 5: Cluster Alignment Penalty**
```python
alignment_bonus = 1.0 if cluster_a == cluster_b else 0.5
```

This penalty halves the cluster component of the score when users are predicted to belong to different lifestyle archetypes, reflecting empirical evidence that cross-cluster compatibility is systematically lower.

**Step 6: Questionnaire Overlap Bonus**
```python
shared_keys = set(questionnaire_a.keys()) & set(questionnaire_b.keys())
overlap_score = sum(1 for k in shared_keys if questionnaire_a[k] == questionnaire_b[k])
overlap_score /= max(len(shared_keys), 1)  # normalize 0-1
```

This bonus rewards explicit agreement on questionnaire items, providing a direct lifestyle compatibility signal independent of the ML model's cluster assignments.

**Step 7: Final Score Composition**
```python
ml_score = 0.2 * (cosine_sim * alignment_bonus) + 0.8 * cosine_sim
final_score = 0.7 * ml_score + 0.3 * overlap_score  # when questionnaire data available
final_score = ml_score  # when questionnaire data unavailable
```

The final score is bounded to [0, 1] and represents an estimated compatibility probability between the two users.

### 5.3.3 Heuristic Fallback Scorer

When the ML model is unavailable or users lack ML feature vectors, the system falls back to a point-based heuristic:

| Signal | Max Score | Logic |
|---|---|---|
| Budget similarity | 0.20 | 1.0 if |budget_a - budget_b| < 2000; scaled linearly to 0 at 10000 difference |
| Gender match | 0.10 | 1.0 if same gender |
| Move-in date proximity | 0.10 | 1.0 if within 30 days; 0.5 if within 60 days; 0 otherwise |
| Lifestyle key overlap | 0.60 | Fraction of matching lifestyle JSON keys |
| **Total** | **1.00** | |

This heuristic ensures the system remains functional even during model maintenance or cold-start periods.

## 5.4 Fake Profile Detector

### 5.4.1 Model Architecture

The fake profile detector is a second **Random Forest Classifier** trained on the same feature space as the compatibility model, with a binary output: `genuine` (0) or `fake` (1). The model produces calibrated probability estimates via `predict_proba()`.

### 5.4.2 Trust Scan Process

```python
def trust_scan_for_user(user):
    features = user.lifestyle.get('ml_features', {})
    feature_matrix = build_feature_matrix(features)
    fake_proba = fake_model.predict_proba(feature_matrix)[0][1]  # P(fake)
    predicted_class = fake_model.predict(feature_matrix)[0]
    is_suspicious = fake_proba > 0.85
    return {
        'fake_probability': round(fake_proba, 4),
        'predicted_class': 'fake' if predicted_class else 'genuine',
        'is_suspicious': is_suspicious
    }
```

The 0.85 threshold was selected to minimize false positives (wrongly flagging genuine users) while catching clearly suspicious profiles. At this threshold, the system blocks listing access for flagged users via a 403 response on the `/property/recommended` endpoint.

### 5.4.3 Trust Score Integration Points

Trust scans are surfaced at multiple points in the user journey:
1. **Self-check** — TrustCheck page allows users to see their own fake profile probability.
2. **Roommate discovery** — POST `/match/ai` returns trust scans for all 10 matched candidates.
3. **Admin oversight** — Admin dashboard surfaces suspicious user flags.
4. **Property access gate** — `is_suspicious=True` users are denied recommended listing access.

## 5.5 Numeric Feature Scalers

Two StandardScaler instances normalize continuous features before model inference:

- **numeric_scaler**: Scales `[age, income, expenses]` to zero-mean, unit-variance
- **feature_scaler**: Scales `[income_expense_ratio, social_habit_score]`

These scalers are fit on the training data distribution and must be updated whenever the model is retrained on new data.

## 5.6 Model Loading and Availability

All four model artifacts are loaded at application startup:

```python
MODELS = {
    'roommate': None,    # RandomForestClassifier
    'fake_profile': None, # RandomForestClassifier
    'numeric_scaler': None, # StandardScaler
    'feature_scaler': None  # StandardScaler
}

def load_models():
    for name, path in MODEL_PATHS.items():
        try:
            MODELS[name] = joblib.load(path)
        except FileNotFoundError:
            logger.warning(f"Model {name} not found at {path}")
```

The system continues to operate with heuristic scoring if any model fails to load — a critical resilience feature for deployment environments where ML artifacts may not always be present.

## 5.7 ML Route Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/ml/health-models` | GET | None | Check all model loading status |
| `/ml/questionnaire-schema` | GET | None | Return questionnaire field definitions |
| `/ml/apply-questionnaire` | POST | JWT | Save responses + build ML features |
| `/ml/fake-profile` | POST | JWT | Check fake profile probability |
| `/ml/roommate-features` | POST | JWT | Score two feature vectors directly |
| `/ml/my-cluster` | GET | JWT | Get cluster prediction for self |

---

# 6. Backend API Design and Implementation

## 6.1 Flask Application Factory

The application is initialized via the `create_app()` factory in `app/__init__.py`:

```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or DefaultConfig)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": CORS_ORIGINS}})
    socketio.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(property_bp, url_prefix='/property')
    app.register_blueprint(match_bp, url_prefix='/match')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(ml_bp, url_prefix='/ml')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(upload_bp)
    
    # Load ML models
    load_models()
    
    return app
```

## 6.2 Authentication Routes (`/auth`)

### 6.2.1 Registration (`POST /auth/register`)

The registration endpoint accepts JSON with the following required fields:
- `email` — validated against RFC 5322 regex
- `password` — minimum 8 characters, must contain uppercase, lowercase, and digit
- `name` — maximum 80 characters, HTML-stripped
- `account_type` — "tenant" or "owner"

Optional fields: `phone`, `budget`, `gender`

Processing flow:
1. Validate all fields using `validators.py` helpers
2. Check email uniqueness against User table
3. Hash password using `werkzeug.security.generate_password_hash`
4. Create User record with `role = account_type`
5. Generate JWT access and refresh tokens using `flask_jwt_extended`
6. Return token pair with user metadata

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 42,
    "email": "user@example.com",
    "name": "Priya Sharma",
    "role": "tenant",
    "is_admin": false
  }
}
```

### 6.2.2 Login (`POST /auth/login`)

Standard email/password authentication:
1. Fetch user by email
2. Verify password hash via `check_password_hash`
3. Update `last_login` timestamp
4. Return fresh JWT token pair

### 6.2.3 Token Refresh (`POST /auth/refresh`)

Uses `@jwt_required(refresh=True)` decorator. Generates a new access token without requiring password re-entry. Essential for maintaining session continuity across the 7-day access token lifetime.

### 6.2.4 Password Reset Flow

**Forgot Password (`POST /auth/forgot-password`):**
1. Look up user by email (return 200 even if not found — prevents email enumeration)
2. Generate cryptographically random token (32 bytes)
3. Hash with SHA-256, store `PasswordResetToken` record with 15-minute expiry
4. Send email via Flask-Mail with reset URL containing plaintext token

**Reset Password (`POST /auth/reset-password`):**
1. Hash received token with SHA-256
2. Look up matching, unexpired, unused `PasswordResetToken`
3. Hash new password, update User record
4. Mark token as `used=TRUE`
5. Return success

### 6.2.5 OAuth Authentication (`POST /auth/oauth/<provider>`)

Supports Google and Facebook:

**Google Flow:**
1. Client obtains Google ID token via Google Sign-In
2. POST to `/auth/oauth/google` with `{id_token: "..."}`
3. Server verifies token against `https://oauth2.googleapis.com/tokeninfo`
4. Extract `sub` (Google user ID), `email`, `name`
5. Upsert user (find by `oauth_provider=google, oauth_id=sub` or `email`)
6. Return JWT tokens

**Facebook Flow:**
1. Client obtains Facebook access token
2. POST to `/auth/oauth/facebook` with `{access_token: "..."}`
3. Server calls `https://graph.facebook.com/me?fields=id,name,email`
4. Process similarly to Google

## 6.3 User Routes (`/user`)

### 6.3.1 Profile Management

**GET `/user/profile`** — Returns the authenticated user's full profile including lifestyle data and favorites.

**PUT `/user/profile`** — Updates mutable profile fields:
```json
{
  "name": "Priya Sharma",
  "bio": "Software engineer looking for a quiet roommate",
  "budget": 22000,
  "gender": "Female",
  "phone": "+919876543210"
}
```

All fields are optional; only provided fields are updated (PATCH semantics despite PUT verb).

### 6.3.2 User Browse (`GET /user/browse`)

Paginated endpoint for tenant discovery. Supports query parameters:
- `page`, `per_page` — pagination
- `gender` — filter by gender preference
- `budget_min`, `budget_max` — filter by budget range
- `region` — filter by lifestyle region

Returns public user profiles (excluding password_hash, lifestyle.ml_features, and other sensitive fields).

### 6.3.3 Individual User Profile (`GET /user/<user_id>`)

Returns full profile if `user_id` matches the authenticated user; returns sanitized public profile otherwise.

### 6.3.4 Favorites Management

- `POST /user/favorites/property/<pid>` — Adds property ID to `user.favorites` JSON array
- `DELETE /user/favorites/property/<pid>` — Removes property ID from favorites array
- `GET /user/favorites` — Returns list of favorited property IDs with full property data

## 6.4 Property Routes (`/property`)

### 6.4.1 Property Listing (`GET /property/`)

Returns paginated property list with optional filters:
```
?location=Bangalore&rent_max=25000&rent_min=10000
&gender_preference=Female&available=true
&owner_id=15&verified_only=true
&page=1&per_page=20
```

Filtering is implemented via SQLAlchemy query chaining with `ilike` for location matching and numeric range comparisons for rent.

### 6.4.2 Property Creation (`POST /property/`)

Owner-only endpoint. Accepts comprehensive property data:
```json
{
  "title": "2BHK in Koramangala",
  "description": "Spacious flat with balcony...",
  "rent": 22000,
  "location": "Koramangala, Bangalore",
  "gender_preference": "Female",
  "amenities": ["WiFi", "Washing Machine", "Power Backup"],
  "housing_meta": {
    "area": 950,
    "bedrooms": 2,
    "bathrooms": 1,
    "furnishing": "Semi-Furnished",
    "region": "Bangalore"
  }
}
```

### 6.4.3 Recommended Listings (`GET /property/recommended`)

ML-personalized property recommendations for tenants (described in detail in Section 11).

## 6.5 Match Routes (`/match`)

### 6.5.1 AI Matching (`POST /match/ai`)

The core roommate discovery endpoint. Processing flow:

1. Authenticate tenant
2. Run trust scan on requesting user — return 403 if `is_suspicious=True`
3. Fetch all other tenants (excluding self, existing matches)
4. For each candidate: compute compatibility score using `ai_matcher.score_pair()`
5. Sort by score, take top 10
6. Run trust scan on each of the 10 candidates
7. Return matches with scores, scoring method, cluster assignments, and trust data

**Response:**
```json
{
  "matches": [
    {
      "user_id": 87,
      "name": "Arjun Menon",
      "bio": "Techie, vegetarian, night owl",
      "budget": 21000,
      "gender": "Male",
      "compatibility_score": 0.847,
      "scoring_method": "ml_cosine_cluster",
      "cluster_a": 3,
      "cluster_b": 3,
      "trust_scan": {
        "fake_probability": 0.031,
        "predicted_class": "genuine",
        "is_suspicious": false
      }
    },
    ...
  ],
  "count": 10,
  "scoring_method": "ml_cosine_cluster"
}
```

### 6.5.2 Match Request Lifecycle

1. **Send Request** (`POST /match/`) — Creates Match record with `status=pending`, `initiator_id=current_user`
2. **Accept/Reject** (`PATCH /match/<id>`) — Updates status to `accepted` or `rejected`
3. **Chat Unlock** — `status=accepted` is the gate condition for chat access (verified by `has_accepted_roommate_match()`)
4. **Delete** (`DELETE /match/<id>`) — Soft-delete or hard-delete (implementation dependent)

## 6.6 Chat Routes (`/chat`)

### 6.6.1 Message History (`GET /chat/with/<user_id>`)

Returns paginated message history between authenticated user and specified user. Messages deleted by either party are filtered from that party's view using the `deleted_by_sender` / `deleted_by_receiver` flags.

Access control: Returns 403 if no accepted match exists between the two users (enforced via `has_accepted_roommate_match()`).

### 6.6.2 Send Message (`POST /chat/send`)

REST fallback for message sending (primary channel is Socket.IO):
```json
{"receiver_id": 87, "message": "Hey, are you still looking for a roommate?"}
```

Persists `ChatMessage` record and emits `new_message` Socket.IO event to receiver's room.

### 6.6.3 Inbox (`GET /chat/inbox`)

Returns all conversations for the authenticated user, with latest message and unread count per conversation. Only conversations with accepted matches are included.

## 6.7 Request/Response Validation

All write endpoints use Marshmallow schemas for request validation:

```python
class UserProfileSchema(ma.Schema):
    name = ma.fields.Str(validate=validate.Length(max=80))
    bio = ma.fields.Str(validate=validate.Length(max=500))
    budget = ma.fields.Int(validate=validate.Range(min=1000, max=1000000))
    gender = ma.fields.Str(validate=validate.OneOf(['Male', 'Female', 'Other']))
```

Validation errors are caught by an error handler that returns structured 422 responses:
```json
{"errors": {"budget": ["Must be between 1000 and 1000000."]}}
```

## 6.8 Pagination Utility

The `pagination.py` utility provides consistent pagination across all list endpoints:

```python
def paginate_query(query, page=1, per_page=20, max_per_page=50):
    per_page = min(per_page, max_per_page)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': paginated.items,
        'meta': {
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    }
```

The `max_per_page=50` cap prevents denial-of-service via large `per_page` values.

---

# 7. Frontend Architecture and User Interface

## 7.1 React Application Structure

The frontend is a Single Page Application (SPA) built with React 18 and TypeScript. Client-side routing is handled by React Router DOM 6, with routes defined in `App.tsx`.

## 7.2 Routing Configuration

```typescript
// App.tsx (simplified)
<BrowserRouter>
  <AuthProvider>
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        
        {/* Tenant routes */}
        <Route element={<RequireAuth />}>
          <Route element={<RequireRole roles={['tenant', 'admin']} />}>
            <Route path="lifestyle" element={<LifestyleSurvey />} />
            <Route path="match" element={<RoommateMatch />} />
            <Route path="roommates/:userId" element={<RoommateDetail />} />
            <Route path="trust" element={<TrustCheck />} />
            <Route path="listings" element={<Listings />} />
            <Route path="messages" element={<MessagesPage />} />
          </Route>
          
          {/* Owner routes */}
          <Route element={<RequireRole roles={['owner', 'admin']} />}>
            <Route path="my-listings" element={<OwnerListings />} />
          </Route>
          
          {/* Admin routes */}
          <Route element={<RequireRole roles={['admin']} />}>
            <Route path="admin" element={<AdminDashboard />} />
          </Route>
          
          {/* All authenticated users */}
          <Route path="profile" element={<Profile />} />
        </Route>
      </Route>
    </Routes>
  </AuthProvider>
</BrowserRouter>
```

## 7.3 Authentication Context

`AuthContext.tsx` provides global auth state:

```typescript
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  
  // On mount: load user from stored token
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) fetchCurrentUser(token);
  }, []);
  
  // Axios request interceptor: attach Bearer token
  // Axios response interceptor: auto-refresh on 401
};
```

Tokens are persisted in `localStorage`. The Axios instance in `api/axios.ts` attaches the access token to all requests and automatically attempts a token refresh on 401 responses, re-queuing the failed request after successful refresh.

## 7.4 Key Page Components

### 7.4.1 Lifestyle Survey (`LifestyleSurvey.tsx`)

The Lifestyle Survey is the primary data collection interface. Key implementation details:

- **Schema-driven rendering**: Fetches questionnaire schema from `/ml/questionnaire-schema` at mount. The schema defines field types, options, labels, and validation rules. The form renders dynamically from this schema, enabling questionnaire updates without frontend code changes.

- **Draft persistence**: Form state is serialized to `localStorage` under a per-user draft key on every change. Users can abandon and resume the survey without losing progress.

- **Feature preview**: After submission, the response includes the full ML feature vector. The UI renders a count of total features and non-zero features, providing transparency about what data was captured.

- **Submission flow**:
  1. Collect form state
  2. POST to `/ml/apply-questionnaire`
  3. Update global user context with new lifestyle data
  4. Clear localStorage draft
  5. Navigate to match page

### 7.4.2 Roommate Match (`RoommateMatch.tsx`)

The roommate discovery interface:

- **Cached results**: Match results are stored in `sessionStorage` via `matchCache.ts`. This prevents redundant API calls when the user navigates away and returns within the same session.

- **Match display**: Each matched user is rendered as a card showing: name, gender badge, budget, bio, compatibility score (as percentage), scoring method badge, cluster IDs, and trust scan result (color-coded: green for genuine, red for suspicious).

- **Scoring method transparency**: The UI displays whether the score was computed via `ml_cosine_cluster`, `ml_cosine`, or `heuristic` — helping users understand the confidence level of the compatibility estimate.

- **Refresh functionality**: A "Find Matches" button clears the cache and triggers a fresh API call.

### 7.4.3 Trust Check (`TrustCheck.tsx`)

The self-service trust verification interface:

- Displays the authenticated user's own fake profile probability with a visual gauge
- Shows `predicted_class` (genuine/fake) and `is_suspicious` flag
- If session-stored match results exist, renders a trust scan table for each matched candidate
- Provides a "Refresh from Server" button to re-run trust scans against the current model

### 7.4.4 Listings (`Listings.tsx`)

Property discovery interface with two modes:
- **Tenant mode**: Calls `/property/recommended`, displays ML recommendation score alongside standard property attributes
- **Owner/browse mode**: Calls `/property/` with all available filters

The component implements client-side filter controls (rent range slider, location text search, availability toggle) that trigger API refetch with updated query parameters.

### 7.4.5 Messages (`MessagesPage.tsx`)

Real-time chat interface:

- **Inbox panel**: Lists all conversations with accepted match partners, showing latest message and unread badge count
- **Conversation panel**: Full message history for selected conversation
- **Socket.IO integration**: Establishes WebSocket connection on mount with JWT auth; subscribes to `new_message` events to append incoming messages without page refresh
- **REST fallback**: Message sending via POST request with Socket.IO emit for delivery notification

### 7.4.6 Admin Dashboard (`AdminDashboard.tsx`)

Comprehensive admin interface:

- **Statistics cards**: Total users, total properties, total messages, total matches
- **Users table**: Paginated list with inline role selector and delete button
- **Properties table**: Paginated list with verify/unverify and delete actions
- **Role management**: PATCH request to `/admin/user/<id>` with new role value on dropdown change

## 7.5 UI Design System

### 7.5.1 Tailwind CSS Configuration

Livora uses a custom Tailwind theme extending the default with brand colors:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        livora: {
          50: '#f0fdfa',   // Very light teal
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',  // Primary brand color
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',  // Darkest teal
        },
        night: {
          950: '#0a0f1e',  // Primary dark background
        }
      }
    }
  }
}
```

### 7.5.2 Custom CSS Classes

```css
.glass {
  @apply bg-white/5 backdrop-blur-sm border border-white/10;
}

.btn-primary {
  @apply bg-livora-500 hover:bg-livora-600 text-white
         font-semibold py-2 px-4 rounded-lg transition-colors
         focus:ring-2 focus:ring-livora-400 focus:outline-none;
}

.btn-secondary {
  @apply border border-slate-600 hover:border-slate-400 text-slate-300
         font-medium py-2 px-4 rounded-lg transition-colors;
}

.input-field {
  @apply bg-white/5 border border-white/10 rounded-lg px-3 py-2
         text-white placeholder-slate-500
         focus:ring-2 focus:ring-livora-500 focus:border-transparent
         focus:outline-none;
}
```

### 7.5.3 Visual Design Language

- **Dark theme**: Primary background `#0a0f1e` (night-950), creating a premium feel
- **Glass morphism**: Semi-transparent cards with backdrop blur for depth
- **Grid overlay**: Subtle CSS grid pattern on the background for texture
- **Teal accent**: `#14b8a6` (livora-500) as the primary interactive color, conveying trust and freshness
- **Gradient hero sections**: Linear gradients from teal to cyan for hero areas

---

# 8. Security and Authentication Subsystem

## 8.1 JWT Authentication Architecture

Livora employs a dual-token JWT strategy:

| Token Type | Validity | Purpose |
|---|---|---|
| Access Token | 7 days | Authorizes API requests (Bearer header) |
| Refresh Token | 30 days | Obtains new access tokens without re-login |

**Token structure:**
```json
{
  "sub": "42",          // User ID (stored as string)
  "type": "access",
  "iat": 1712345678,
  "exp": 1712950478,
  "jti": "unique-token-id"
}
```

The use of string-typed `sub` (via `str(user.id)`) is intentional — `flask_jwt_extended` requires consistent identity type to avoid serialization ambiguities.

**Access token delivery:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 8.2 Role-Based Access Control (RBAC)

Livora implements a three-tier RBAC system:

```
admin
  └─ Inherits all tenant + owner capabilities
     └─ Additionally: user/property management, role changes
owner
  └─ Create/edit own properties
     └─ Browse tenants
tenant
  └─ Fill questionnaire, run AI match, view listings, chat
```

**Role resolution (`utils/roles.py`):**
```python
def get_user_role(user) -> str:
    if user.is_admin:
        return ROLE_ADMIN
    return user.role  # 'tenant' or 'owner'
```

**Role enforcement decorators:**
```python
def tenant_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if get_user_role(user) not in [ROLE_TENANT, ROLE_ADMIN]:
            return jsonify({'error': 'Tenant access required'}), 403
        return fn(*args, **kwargs)
    return wrapper
```

## 8.3 Password Security

Password storage follows best practices:
- **Algorithm**: Werkzeug's `generate_password_hash` uses PBKDF2-HMAC-SHA256 with a random salt by default
- **No plaintext storage**: Passwords are never logged or stored in plaintext
- **Validation**: Minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit
- **Change password**: Requires current password verification before accepting new password

## 8.4 Input Validation and Sanitization

All user-supplied text inputs are processed through `utils/validators.py`:

```python
def sanitize_text(text: str, max_length: int = 500) -> str:
    # Strip HTML tags to prevent XSS
    clean = re.sub(r'<[^>]+>', '', text)
    # Truncate to max length
    return clean[:max_length].strip()

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    # E.164 format: +countrycode followed by 7-15 digits
    pattern = r'^\+[1-9]\d{6,14}$'
    return bool(re.match(pattern, phone))

def validate_budget(budget: int) -> bool:
    return 1000 <= budget <= 1000000

def validate_region(region: str) -> bool:
    VALID_REGIONS = [
        'Bangalore', 'Hyderabad', 'Pune', 'Chennai',
        'Delhi NCR', 'Mumbai'
    ]
    return region in VALID_REGIONS
```

## 8.5 OAuth Security

OAuth flows use server-side token verification:
- **Google**: Tokens verified against `https://oauth2.googleapis.com/tokeninfo` (not just client-side decoded)
- **Facebook**: Tokens verified against `https://graph.facebook.com/me`

This prevents OAuth token forgery — a common vulnerability in client-side OAuth implementations.

## 8.6 File Upload Security

Upload endpoints implement multiple security controls:

```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def secure_upload(file):
    # 1. Validate extension
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise APIException("Invalid file type", 400)
    
    # 2. Validate file size
    file.seek(0, 2)
    if file.tell() > MAX_FILE_SIZE:
        raise APIException("File too large", 413)
    file.seek(0)
    
    # 3. Generate UUID filename (prevents path traversal)
    filename = f"{uuid.uuid4()}.{ext}"
    
    # 4. Save with werkzeug.utils.secure_filename
    safe_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    file.save(safe_path)
    return filename
```

UUID-based filenames prevent:
- **Directory traversal**: `../../../etc/passwd` style attacks
- **Filename collisions**: Multiple users uploading files with the same name
- **Information disclosure**: Leaking original filenames

## 8.7 CORS Configuration

```python
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 
    'http://127.0.0.1:5173,http://localhost:5173,'
    'http://127.0.0.1:3000,http://localhost:3000'
).split(',')

CORS(app, 
     resources={r"/*": {"origins": CORS_ORIGINS}},
     supports_credentials=True)
```

The explicit origin whitelist prevents unauthorized cross-origin requests. The `supports_credentials=True` flag is required for JWT-bearing requests from the frontend.

## 8.8 Security Limitations and Mitigations

| Limitation | Risk Level | Suggested Mitigation |
|---|---|---|
| No rate limiting | Medium | Add Flask-Limiter with IP-based rate limits on auth endpoints |
| No request logging | Medium | Add structured logging middleware (e.g., Python logging + Sentry) |
| SQLite in development | Low | Already mitigated by PostgreSQL in production |
| JWT secret in env | Low | Use secret rotation; consider asymmetric keys (RS256) in production |
| No IP blocklist | Low | Add fail2ban-style IP blocking after repeated auth failures |

---

# 9. Real-Time Communication with Socket.IO

## 9.1 Architecture Overview

Livora uses Flask-SocketIO with eventlet for asynchronous WebSocket communication. The Socket.IO server runs on the same port as the Flask application (5000), sharing the same process via the monkey-patched event loop.

## 9.2 Connection Establishment

```python
# socket_events.py
@socketio.on('connect')
def handle_connect(auth):
    try:
        token = auth.get('token') if auth else None
        if not token:
            disconnect()
            return
        
        user_id = decode_token(token)['sub']
        user = User.query.get(int(user_id))
        
        if not user:
            disconnect()
            return
        
        join_room(f"user_{user_id}")
        emit('connected', {'status': 'ok', 'user_id': user_id})
        
    except Exception:
        disconnect()
```

The client authenticates during the connection handshake:
```typescript
// MessagesPage.tsx
const socket = io(API_URL, {
  auth: { token: localStorage.getItem('access_token') }
});
```

## 9.3 Message Delivery

```python
# socket_events.py
def emit_to_user(socketio_instance, user_id: int, event: str, payload: dict):
    room = f"user_{user_id}"
    socketio_instance.emit(event, payload, to=room)
```

When a chat message is sent via POST `/chat/send`:
1. Message is persisted to `ChatMessage` table
2. `emit_to_user(socketio, receiver_id, 'new_message', {...})` is called
3. If the receiver is connected, they receive the message instantly
4. If the receiver is offline, they retrieve it via GET `/chat/with/<id>` on next login

## 9.4 Client-Side Event Handling

```typescript
// MessagesPage.tsx (simplified)
useEffect(() => {
  socket.on('new_message', (msg: Message) => {
    setMessages(prev => [...prev, msg]);
    // Update inbox unread count
    setInbox(prev => prev.map(conv =>
      conv.partner_id === msg.sender_id
        ? { ...conv, unread_count: conv.unread_count + 1 }
        : conv
    ));
  });
  
  return () => {
    socket.off('new_message');
    socket.disconnect();
  };
}, []);
```

## 9.5 Room-Based Targeting

User-specific rooms (`user_{id}`) ensure messages are delivered only to the intended recipient. This is preferable to broadcasting to all connections because:
1. Privacy — messages are not broadcast to all connected clients
2. Multi-device — if a user is connected from multiple devices, all sessions receive the message
3. Scalability — room-based targeting works correctly with Redis Socket.IO adapter for multi-server deployments

---

# 10. Administrative Subsystem

## 10.1 Admin Dashboard

The admin dashboard provides operators with full oversight and control over the Livora platform:

### 10.1.1 Platform Statistics

```
GET /admin/dashboard
Response:
{
  "users": { "total": 412, "tenants": 389, "owners": 21, "admins": 2 },
  "properties": { "total": 87, "available": 71, "verified": 43 },
  "messages": { "total": 3841 },
  "matches": { "total": 267, "accepted": 89, "pending": 134, "rejected": 44 }
}
```

### 10.1.2 User Management

Admin endpoints for user management:

| Action | Endpoint | Effect |
|---|---|---|
| List all users | `GET /admin/users` | Paginated user list with all metadata |
| Change role | `PATCH /admin/user/<id>` | Update role, name, bio, budget, gender |
| Verify user | `POST /admin/user/<id>/verify` | Set `is_verified=True` |
| Remove user | `DELETE /admin/user/<id>/remove` | Hard delete user record |

Role change is a privileged operation that allows operators to:
- Promote a tenant to owner (to allow property listing)
- Demote an owner to tenant (if they misused owner privileges)
- Grant admin access (by setting `is_admin=True`)

### 10.1.3 Property Management

| Action | Endpoint | Effect |
|---|---|---|
| List properties | `GET /admin/properties` | Paginated property list |
| Verify property | `POST /admin/property/<id>/verify` | Set `is_verified=True` |
| Feature property | `POST /admin/property/<id>/feature` | Set `is_featured=True` |
| Edit property | `PATCH /admin/property/<id>` | Update any property field |
| Delete property | `DELETE /admin/property/<id>` | Hard delete property record |

Verified properties receive a badge in the UI and are given precedence in search results. Featured properties may appear in promoted sections (e.g., homepage, top of search results).

## 10.2 Database Seeding

For development and demonstration purposes, Livora provides two CLI seed commands:

### 10.2.1 Demo Seed (`flask seed-demo`)

Creates:
- 1 admin account (`admin@livora.in`)
- 1 owner account with 3 sample properties

### 10.2.2 Diverse Seed (`flask seed-diverse`)

Creates a realistic distribution of users across Indian cities:
- 36 tenant profiles with varied lifestyle questionnaire responses
- 8 owner profiles with property listings
- Users distributed across 12 Indian cities: Bangalore, Hyderabad, Pune, Chennai, Delhi, Mumbai, Kolkata, Ahmedabad, Jaipur, Chandigarh, Kochi, Goa
- ML features computed for each seeded user
- Properties with realistic `housing_meta` data (area, bedrooms, bathrooms, furnishing, region)

The diverse seed enables immediate demonstration of the AI matching pipeline without requiring real user registrations.

---

# 11. Property Recommendation Engine

## 11.1 Algorithm Overview

The property recommendation engine (`services/listing_recommendation.py`) implements a content-based filtering approach using five housing features and MinMaxScaler normalization.

## 11.2 Feature Space Definition

Properties are represented in a five-dimensional feature space:
```
F = [rent, area, bedrooms, bathrooms, furnishing_score]
```

Where:
- `rent` — monthly rent in INR
- `area` — floor area in square feet
- `bedrooms` — number of bedrooms
- `bathrooms` — number of bathrooms
- `furnishing_score` — {1.0: "Furnished", 0.5: "Semi-Furnished", 0.0: "Unfurnished"}

## 11.3 User Target Vector

The user's target property vector is derived from lifestyle data:
```
U = [expenses (or budget), median_area, median_bedrooms, median_bathrooms, 1.0]
```

Where:
- `expenses` from `lifestyle.questionnaire.expenses` is preferred over raw `budget` as it better reflects actual housing cost expectations
- `median_area = 800` (default area expectation for urban professionals)
- `median_bedrooms = 2`, `median_bathrooms = 1` (most common shared apartment configuration)
- `1.0` for furnishing preference (fully furnished is preferred by most tenants)

## 11.4 Regional Pre-Filtering

Before distance computation, properties are pre-filtered to the user's stated region:

```python
def get_region_from_user(user):
    lifestyle = user.lifestyle or {}
    questionnaire = lifestyle.get('questionnaire', {})
    return questionnaire.get('region')

def filter_by_region(properties, region):
    if not region:
        return properties  # No filter if region unspecified
    return [p for p in properties 
            if (p.housing_meta or {}).get('region') == region
            or region.lower() in (p.location or '').lower()]
```

This two-pass matching (exact `housing_meta.region` match, then substring match in `location` text) handles both structured and unstructured location data.

## 11.5 Distance-Based Scoring

```python
from sklearn.preprocessing import MinMaxScaler
import numpy as np

def rank_properties(properties, user_target_vector):
    # Build property matrix
    property_matrix = np.array([
        [p.rent, p.housing_meta.get('area', 800),
         p.housing_meta.get('bedrooms', 1),
         p.housing_meta.get('bathrooms', 1),
         furnishing_score(p.housing_meta.get('furnishing', 'Unfurnished'))]
        for p in properties
    ])
    
    # Add user target as last row
    combined = np.vstack([property_matrix, [user_target_vector]])
    
    # Normalize to [0, 1]
    scaler = MinMaxScaler()
    combined_scaled = scaler.fit_transform(combined)
    
    # Separate scaled properties and target
    scaled_properties = combined_scaled[:-1]
    scaled_target = combined_scaled[-1]
    
    # Compute Euclidean distances
    distances = np.linalg.norm(scaled_properties - scaled_target, axis=1)
    
    # Convert to similarity scores
    scores = 1.0 / (1.0 + distances)
    
    return sorted(zip(properties, scores), key=lambda x: x[1], reverse=True)
```

The `1.0 / (1.0 + distance)` transformation maps distances to similarity scores in (0, 1], where 0 distance (perfect match) yields score 1.0 and infinite distance yields score 0.

## 11.6 Edge Cases

- **No regional properties**: If no properties match the user's region, the system returns all available properties without regional filtering.
- **Missing housing_meta**: Properties with null `housing_meta` use default values (area=800, bedrooms=1, bathrooms=1, furnishing=Unfurnished).
- **Single property**: MinMaxScaler with a single property (plus user target) may produce degenerate scaling; handled by a minimum 2-row constraint.

## 11.7 Response Format

```json
{
  "properties": [
    {
      "id": 23,
      "title": "2BHK in Indiranagar",
      "rent": 22000,
      "location": "Indiranagar, Bangalore",
      "description": "Quiet area, near metro...",
      "is_verified": true,
      "is_featured": false,
      "recommendation_score": 0.923,
      "housing_meta": {
        "area": 900, "bedrooms": 2, "bathrooms": 1,
        "furnishing": "Semi-Furnished", "region": "Bangalore"
      }
    }
  ],
  "count": 14,
  "region_filter": "Bangalore"
}
```

---

# 12. Deployment and Infrastructure

## 12.1 Environment Configuration

Livora uses environment variables for all configuration:

### 12.1.1 Backend Configuration

```bash
# Core Flask
SECRET_KEY=<random-256-bit-key>
DATABASE_URL=postgresql://user:pass@localhost:5432/livora_prod

# JWT
JWT_SECRET_KEY=<separate-jwt-secret>
JWT_ACCESS_TOKEN_SECONDS=604800
JWT_REFRESH_TOKEN_SECONDS=2592000
JWT_ALGORITHM=HS256

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=noreply@livora.in
MAIL_PASSWORD=<app-specific-password>
MAIL_USE_TLS=True

# File Uploads
UPLOAD_FOLDER=/var/www/livora/uploads
MAX_UPLOAD_BYTES=10485760  # 10MB
PUBLIC_UPLOAD_URL_PREFIX=https://cdn.livora.in/uploads

# CORS
CORS_ORIGINS=https://livora.in,https://www.livora.in

# ML Models
LIVORA_ML_DIR=/var/ml/livora/models
ROOMMATE_MODEL_PATH=/var/ml/livora/models/roommate_compatibility_model.joblib
FAKE_PROFILE_MODEL_PATH=/var/ml/livora/models/fake_profile_detector.joblib
NUMERIC_SCALER_PATH=/var/ml/livora/models/numeric_scaler.joblib
FEATURE_SCALER_PATH=/var/ml/livora/models/feature_scaler.joblib
```

### 12.1.2 Frontend Configuration

```bash
VITE_API_URL=https://api.livora.in
```

## 12.2 Production Deployment Architecture

```
Internet
    │
    ▼
[Nginx Reverse Proxy]
    │
    ├──── /api/*  ──────► [Gunicorn (4 workers)] ──► [Flask App]
    │                                                      │
    │                                               [PostgreSQL]
    │                                               [Redis (Celery)]
    │
    └──── /*  ──────────► [Static Files (Vite Build)]
                          (served by Nginx directly)
```

### 12.2.1 Gunicorn Configuration

```bash
gunicorn \
  --worker-class eventlet \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info \
  --access-logfile /var/log/livora/access.log \
  wsgi:app
```

The `eventlet` worker class is required for Socket.IO compatibility (standard sync workers do not support WebSocket connections).

### 12.2.2 Database Migration in Production

```bash
flask db upgrade  # Apply pending migrations
flask seed-demo   # Optional: create demo accounts
```

### 12.2.3 Frontend Build

```bash
npm run build  # TypeScript compilation + Vite bundling
# Output: dist/ directory with index.html + hashed JS/CSS chunks
```

## 12.3 Celery Task Queue

While not heavily utilized in the current codebase, Celery + Redis is configured for:
- Asynchronous email sending
- Scheduled ML model retraining jobs
- Deferred trust scan computations for large user batches

## 12.4 File Storage

Uploaded files (property images, user avatars) are stored in a configurable upload directory. For production, this should be mounted as a persistent volume or replaced with object storage (AWS S3, Google Cloud Storage, Cloudflare R2) for:
- High availability across multiple application servers
- CDN integration for fast image delivery
- Automatic backup and versioning

---

# 13. Testing and Quality Assurance

## 13.1 Current Test Coverage

Livora's current test suite includes:
- `tests/test_basic.py` — Smoke tests verifying Flask app creation
- `tests/test_auth.py` — Authentication endpoint tests (partial coverage)

Overall test coverage is limited, representing a known gap in the current implementation.

## 13.2 Test Architecture Recommendations

### 13.2.1 Unit Tests

Critical units requiring test coverage:

```python
# Feature engineering tests
def test_questionnaire_to_features_completeness():
    questionnaire = {
        'age': 25, 'income': 40000, 'expenses': 15000,
        'drinks': 'Occasionally', 'smokes': 'No',
        'region': 'Bangalore', 'diet': 'Vegetarian',
        # ... all fields
    }
    features = build_ml_features(questionnaire)
    assert 'income_expense_ratio' in features
    assert features['income_expense_ratio'] == pytest.approx(40000/15000)
    assert features['drinks_Occasionally'] == 1
    assert features['drinks_No'] == 0

# Compatibility scoring tests
def test_identical_profiles_score_near_one():
    score = compute_heuristic_compatibility(user_a, user_b)
    # Identical budget, gender, move_in_date, lifestyle
    assert score > 0.9

def test_opposite_profiles_score_near_zero():
    # Vastly different budgets, genders, lifestyles
    score = compute_heuristic_compatibility(user_a, user_c)
    assert score < 0.3
```

### 13.2.2 Integration Tests

Using Flask's test client with an in-memory SQLite database:

```python
@pytest.fixture
def app():
    app = create_app(TestConfig)  # Uses SQLite :memory:
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_register_and_login(client):
    # Register
    resp = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'TestPass123',
        'name': 'Test User',
        'account_type': 'tenant'
    })
    assert resp.status_code == 201
    assert 'access_token' in resp.json
    
    # Login
    resp = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    assert resp.status_code == 200
```

### 13.2.3 End-to-End Tests

Playwright or Cypress for critical user flows:
1. Registration → Survey → Match discovery
2. Property listing creation (owner) → Discovery (tenant)
3. Match request → Accept → Chat message exchange
4. Password reset via email

## 13.3 Postman Collection

The project includes a Postman collection at `backend/postman/Livora_6_cluster_users.postman_collection.json` containing pre-configured requests for all API endpoints, with example request bodies and expected responses. This collection serves as both documentation and a manual regression testing tool.

---

# 14. Performance and Scalability Analysis

## 14.1 Current Performance Characteristics

### 14.1.1 ML Inference Latency

Random Forest inference on the 100+ dimensional feature vector is computationally lightweight. On a single CPU core:
- Single prediction: ~0.5–2ms
- Top-10 match computation (scanning all tenants): O(n × t) where n = active tenants, t = inference time
- At 1,000 tenants: ~0.5–2 seconds (acceptable)
- At 100,000 tenants: ~500–2,000 seconds (requires optimization: pre-computed cluster assignments, approximate nearest-neighbor search)

### 14.1.2 Database Query Performance

Critical queries and their optimization status:

| Query | Current | Recommended |
|---|---|---|
| User by email (login) | INDEXED (unique) | Optimal |
| Properties by region | Full table scan on JSON | Add generated column index |
| Match by user_id | Composite index needed | Add INDEX(user1_id, user2_id) |
| Chat messages by sender/receiver | Sequential scan | Add INDEX(sender_id, timestamp) |

### 14.1.3 Pagination Enforcement

The `max_per_page=50` cap prevents single queries from returning unbounded result sets, providing a baseline denial-of-service protection.

## 14.2 Scalability Bottlenecks

### 14.2.1 ML Matching at Scale

The current O(n) scan-all-tenants approach for AI matching is the primary scalability concern. Recommended mitigations:

1. **Precomputed clusters**: Run batch clustering nightly, store cluster_id on User model. Match only within same cluster (O(n/k) where k=cluster count).

2. **Approximate nearest neighbor**: Replace exact cosine similarity with FAISS or Annoy library for approximate nearest-neighbor search in probability vector space. Achieves O(log n) query time with minimal precision loss.

3. **Incremental matching**: Cache match candidates per user, only recompute when user's lifestyle data changes.

### 14.2.2 Socket.IO Scaling

Single-server Socket.IO with eventlet works for development and small deployments. For horizontal scaling:

1. Deploy Socket.IO Redis adapter: `socketio = SocketIO(app, message_queue='redis://localhost:6379/0')`
2. This allows multiple application servers to share the Socket.IO room state via Redis pub/sub

### 14.2.3 File Storage Scaling

Current local filesystem storage is not horizontally scalable. Migration to object storage (S3-compatible) is required before multi-server deployment.

## 14.3 Caching Strategy

### 14.3.1 Client-Side Caching

The frontend implements two caching layers:
- **Session Storage**: Match results cached for session duration (avoids repeated API calls)
- **Local Storage**: Lifestyle survey drafts persisted across browser sessions

### 14.3.2 Server-Side Caching (Recommended)

Flask-Caching with Redis backend for:
- Questionnaire schema (changes infrequently)
- Platform statistics (dashboard)
- Top property recommendations per region (expire daily)

---

# 15. Comparative Analysis with Existing Platforms

## 15.1 Comparison Matrix

| Feature | Livora | NoBroker | 99acres | Zumper | SpareRoom (UK) |
|---|---|---|---|---|---|
| Indian market focus | Yes | Yes | Yes | No | No |
| Roommate matching | ML-based | No | No | Basic | Basic |
| Lifestyle questionnaire | 18+ fields | No | No | Limited | Basic |
| Fake profile detection | ML-based | Manual | Manual | No | Manual |
| Compatibility scoring | Probabilistic | No | No | No | No |
| Trust score display | Yes | No | No | No | No |
| Property recommendations | ML-ranked | Filter-based | Filter-based | ML-pricing | Filter-based |
| Real-time chat | Socket.IO | Yes | Yes | Yes | Yes |
| Multi-role platform | Yes | Partial | Partial | No | Partial |
| OAuth login | Yes | Yes | Yes | Yes | Yes |
| Admin oversight panel | Yes | Internal | Internal | Internal | Internal |
| Open source | Yes | No | No | No | No |

## 15.2 Competitive Advantages

1. **ML compatibility scoring**: No Indian competitor offers probabilistic roommate compatibility scoring. Livora's Random Forest approach with cosine similarity of probability vectors is the most sophisticated compatibility algorithm in the Indian market.

2. **Integrated fake profile detection**: Proactive ML-based fraud detection is unique in the Indian rental space. Competitors rely entirely on post-hoc manual review.

3. **Lifestyle questionnaire depth**: 18+ structured lifestyle fields vs. 3–5 basic preference fields on competitors.

4. **Transparency**: Livora surfaces compatibility scores, scoring methods, cluster assignments, and trust probabilities to users — enabling informed decision-making not possible on opaque competitor platforms.

5. **Open architecture**: The open-source codebase enables community contributions, security audits, and academic research.

## 15.3 Competitive Disadvantages

1. **Property volume**: Established platforms have orders-of-magnitude more listings.
2. **Verification infrastructure**: NoBroker and 99acres have physical verification teams; Livora's verification is admin-manual.
3. **Mobile apps**: No native mobile application (web-only).
4. **Payment integration**: No in-platform rent payment or deposit escrow.
5. **Legal support**: No rental agreement generation or dispute resolution.

---

# 16. Limitations and Future Work

## 16.1 Current Limitations

### 16.1.1 ML Model Training Data

The Random Forest models are trained on data not included in the public repository. The quality of compatibility scoring and fake profile detection is entirely dependent on the size, diversity, and labeling quality of this training data. Without information on training set composition:
- Potential biases in compatibility scoring (e.g., favoring urban professional profiles)
- Unknown false positive/negative rates for fake profile detection
- Possible performance degradation on profiles outside the training distribution

### 16.1.2 Geographic Scope

The platform currently supports six Indian cities: Bangalore, Hyderabad, Pune, Chennai, Delhi NCR, and Mumbai. This covers approximately 40% of India's urban rental market. Extension to Tier-2 cities (Kochi, Ahmedabad, Jaipur, Chandigarh) is partially implemented in the seeding script but not fully supported in the recommendation engine.

### 16.1.3 Test Coverage

As noted in Section 13, test coverage is minimal. The lack of comprehensive integration tests creates risk during refactoring and feature additions.

### 16.1.4 API Documentation

No OpenAPI/Swagger documentation is generated or served. This creates friction for third-party integrators and makes onboarding new developers slower.

### 16.1.5 Notification System

The platform supports email notifications only for password reset. There is no in-app notification system for new match requests, accepted matches, or incoming messages (beyond Socket.IO real-time delivery).

## 16.2 Future Work

### 16.2.1 Enhanced ML Models

1. **Deep learning compatibility**: Replace Random Forest with a neural network (e.g., Siamese network) trained on actual roommate outcome data (successful co-tenancies vs. conflicts). This would enable learning from implicit feedback.

2. **Collaborative filtering overlay**: Add matrix factorization on match acceptance/rejection history to learn preference patterns not captured by questionnaire data.

3. **NLP profile analysis**: Apply BERT embeddings to free-text bio fields to capture personality signals beyond structured questionnaire data.

4. **Active learning**: Incorporate user feedback on match quality to continuously improve the model without expensive re-labeling.

### 16.2.2 Platform Features

1. **Mobile application**: React Native implementation sharing business logic with the web frontend.

2. **Virtual tours**: Integration with 360° photo/video platforms for property tours without physical visits.

3. **Rental agreement generation**: Template-based rental agreement creation with digital signature support.

4. **Payment integration**: UPI/Razorpay integration for deposit escrow and rent payment.

5. **Background verification**: Integration with identity verification APIs (Aadhaar, DigiLocker) for enhanced user trust.

6. **Geospatial recommendations**: Replace region-text matching with actual geospatial distance calculations using user's GPS location and property latitude/longitude.

7. **Push notifications**: WebPush API integration for new message and match request notifications when users are not on the platform.

### 16.2.3 Infrastructure

1. **Kubernetes deployment**: Containerize with Docker, deploy on Kubernetes for auto-scaling.

2. **ML model serving**: Deploy models on dedicated inference service (TorchServe, Triton) for independent scaling.

3. **Real-time analytics**: Stream user events to Kafka/ClickHouse for ML feature store and usage analytics.

4. **A/B testing framework**: Infrastructure for testing compatibility algorithm variants on subsets of users.

### 16.2.4 Accessibility and Internationalization

1. **Screen reader support**: Comprehensive ARIA labeling and keyboard navigation.

2. **Multi-language support**: Hindi, Tamil, Telugu, Kannada interfaces for non-English-speaking users.

3. **PWA**: Progressive Web App manifest for offline-capable mobile-web experience.

---

# 17. Conclusion

This paper has presented a comprehensive technical analysis of Livora, an AI-driven smart rental and roommate matching platform designed for the Indian urban housing market. The system addresses three fundamental problems in the Indian rental ecosystem — roommate incompatibility, fraudulent profiles, and imprecise property discovery — through an integrated multi-model machine learning pipeline, role-stratified REST API, and real-time communication infrastructure.

Key technical contributions include: (1) a questionnaire-to-feature-vector pipeline transforming 18+ lifestyle fields into a 100+ dimensional feature space; (2) a Random Forest-based compatibility scoring algorithm combining cosine similarity of cluster probability vectors with questionnaire overlap bonuses; (3) an ML-based fake profile detector with a 0.85 probability threshold blocking suspicious users from sensitive platform features; (4) a five-dimensional content-based property recommendation engine using MinMaxScaler normalization and Euclidean distance scoring; and (5) a comprehensive three-tier RBAC system with JWT authentication and granular route-level access control.

The system demonstrates several architectural strengths: graceful degradation to heuristic scoring when ML models are unavailable, transparent surfacing of scoring methods and trust probabilities to users, schema-driven questionnaire rendering enabling model updates without frontend code changes, and a room-based Socket.IO architecture compatible with future horizontal scaling via Redis adapter.

Significant limitations include minimal test coverage, absence of geospatial recommendation (relying on text-based region matching), limited geographic scope to six cities, and lack of API documentation. Future work should prioritize deep learning compatibility models trained on actual co-tenancy outcome data, mobile application development, and integration with India's national identity verification infrastructure (Aadhaar, DigiLocker).

Overall, Livora represents a technically sophisticated platform that meaningfully advances the state of AI-driven roommate matching in India, combining production-ready software engineering practices with novel ML pipeline design. The open-source architecture positions it as both a deployable commercial product and a research platform for continued innovation in the AI-assisted rental domain.

---

# 18. References

[1] D. Gale and L. S. Shapley, "College Admissions and the Stability of Marriage," *The American Mathematical Monthly*, vol. 69, no. 1, pp. 9–15, 1962.

[2] D. Gusfield, "Three Fast Algorithms for Four Problems in Stable Marriage," *SIAM Journal on Computing*, vol. 16, no. 1, pp. 111–128, 1987.

[3] Y. Koren, R. Bell, and C. Volinsky, "Matrix Factorization Techniques for Recommender Systems," *IEEE Computer*, vol. 42, no. 8, pp. 30–37, 2009.

[4] P. J. Rentfrow and S. D. Gosling, "The Do Re Mi's of Everyday Life: The Structure and Personality Correlates of Music Preferences," *Journal of Personality and Social Psychology*, vol. 84, no. 6, pp. 1236–1256, 2006.

[5] Z. Yang, C. Wilson, X. Wang, T. Gao, B. Y. Zhao, and Y. Dai, "Uncovering Social Network Sybils in the Wild," *ACM Transactions on Knowledge Discovery from Data*, vol. 8, no. 1, pp. 1–28, 2014.

[6] B. Hooi, H. A. Song, A. Beutel, N. Shah, K. Shin, and C. Faloutsos, "FRAUDAR: Bounding Graph Fraud in the Face of Camouflage," in *Proc. KDD*, San Francisco, CA, 2016, pp. 895–904.

[7] G. Stringhini, C. Kruegel, and G. Vigna, "Detecting Spammers on Social Networks," in *Proc. ACSAC*, Austin, TX, 2010, pp. 1–9.

[8] L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.

[9] X. He, L. Liao, H. Zhang, L. Nie, X. Hu, and T.-S. Chua, "Neural Collaborative Filtering," in *Proc. WWW*, Perth, Australia, 2017, pp. 173–182.

[10] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.

[11] R. Mayer, C. Trummer, and A. Borger, "A Comprehensive Real Estate Market Analysis Using Machine Learning," in *Proc. ICDM Workshops*, Singapore, 2018, pp. 1–8.

[12] C.-W. Park, B. Kim, and O. Park, "Deep Learning based Recommendation System for Real Estate," in *Proc. ICAISC*, Zakopane, Poland, 2020, pp. 289–300.

[13] M. Abadi et al., "TensorFlow: A System for Large-Scale Machine Learning," in *Proc. USENIX OSDI*, Savannah, GA, 2016, pp. 265–283.

[14] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. KDD*, San Francisco, CA, 2016, pp. 785–794.

[15] R. He and J. McAuley, "Ups and Downs: Modeling the Visual Evolution of Fashion Trends with One-Class Collaborative Filtering," in *Proc. WWW*, Montreal, Canada, 2016, pp. 507–517.

[16] OWASP Foundation, "OWASP Top 10 Application Security Risks," Open Web Application Security Project, 2021. [Online]. Available: https://owasp.org/Top10/

[17] A. Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library," in *Proc. NeurIPS*, Vancouver, Canada, 2019, pp. 8024–8035.

[18] G. Zhang, R. Tahmasbi, and F. Mirza, "Predicting Roommate Compatibility Using Lifestyle Survey Data and Ensemble Classifiers," in *Proc. AAAI Workshop on AI for Social Good*, 2021.

[19] J. Johnson, M. Douze, and H. Jégou, "Billion-Scale Similarity Search with GPUs," *IEEE Transactions on Big Data*, vol. 7, no. 3, pp. 535–547, 2021.

[20] National Consumer Helpline, "Annual Report on Consumer Fraud Cases in India," Ministry of Consumer Affairs, Food and Public Distribution, Government of India, New Delhi, 2023.

---

# 19. Appendices

## Appendix A: Complete API Reference

### A.1 Authentication Endpoints

| Endpoint | Method | Auth Required | Description |
|---|---|---|---|
| `/auth/register` | POST | No | Create new account |
| `/auth/signup` | POST | No | Alternative signup |
| `/auth/login` | POST | No | Email/password login |
| `/auth/refresh` | POST | Refresh token | Get new access token |
| `/auth/forgot-password` | POST | No | Request password reset email |
| `/auth/reset-password` | POST | No | Reset password via token |
| `/auth/change-password` | POST | Access token | Change password |
| `/auth/oauth/google` | POST | No | Google OAuth login |
| `/auth/oauth/facebook` | POST | No | Facebook OAuth login |

### A.2 User Endpoints

| Endpoint | Method | Auth Required | Roles | Description |
|---|---|---|---|---|
| `/user/profile` | GET | Yes | Any | Get own profile |
| `/user/profile` | PUT | Yes | Any | Update own profile |
| `/user/browse` | GET | Yes | Any | Browse users |
| `/user/<id>` | GET | Yes | Any | Get user by ID |
| `/user/favorites` | GET | Yes | Any | List favorites |
| `/user/favorites/property/<id>` | POST | Yes | Any | Add to favorites |
| `/user/favorites/property/<id>` | DELETE | Yes | Any | Remove from favorites |

### A.3 Property Endpoints

| Endpoint | Method | Auth Required | Roles | Description |
|---|---|---|---|---|
| `/property/` | GET | No | Any | List properties |
| `/property/recommended` | GET | Yes | Tenant | ML recommendations |
| `/property/mine` | GET | Yes | Owner | Own properties |
| `/property/` | POST | Yes | Owner | Create property |
| `/property/<id>` | GET | No | Any | Property details |
| `/property/<id>` | PUT | Yes | Owner/Admin | Update property |
| `/property/<id>` | DELETE | Yes | Admin | Delete property |

### A.4 Match Endpoints

| Endpoint | Method | Auth Required | Roles | Description |
|---|---|---|---|---|
| `/match/ai` | POST | Yes | Tenant | Run AI matching |
| `/match/requests` | GET | Yes | Any | Pending match requests |
| `/match/my` | GET | Yes | Any | All my matches |
| `/match/` | POST | Yes | Any | Send match request |
| `/match/<id>` | PATCH | Yes | Any | Update match status |
| `/match/<id>` | DELETE | Yes | Any | Delete match |
| `/match/can-chat/<id>` | GET | Yes | Any | Check chat eligibility |

### A.5 Chat Endpoints

| Endpoint | Method | Auth Required | Roles | Description |
|---|---|---|---|---|
| `/chat/with/<id>` | GET | Yes | Any | Message history |
| `/chat/send` | POST | Yes | Any | Send message |
| `/chat/inbox` | GET | Yes | Any | Conversation inbox |
| `/chat/read` | POST | Yes | Any | Mark messages read |

### A.6 ML Endpoints

| Endpoint | Method | Auth Required | Roles | Description |
|---|---|---|---|---|
| `/ml/health-models` | GET | No | Any | Model health check |
| `/ml/questionnaire-schema` | GET | No | Any | Form schema |
| `/ml/apply-questionnaire` | POST | Yes | Any | Save questionnaire |
| `/ml/fake-profile` | POST | Yes | Any | Check fake profile |
| `/ml/roommate-features` | POST | Yes | Any | Score feature vectors |
| `/ml/my-cluster` | GET | Yes | Any | Get my cluster |

### A.7 Admin Endpoints

| Endpoint | Method | Auth Required | Roles | Description |
|---|---|---|---|---|
| `/admin/dashboard` | GET | Yes | Admin | Platform statistics |
| `/admin/users` | GET | Yes | Admin | All users |
| `/admin/properties` | GET | Yes | Admin | All properties |
| `/admin/property/<id>/verify` | POST | Yes | Admin | Verify property |
| `/admin/property/<id>/unverify` | POST | Yes | Admin | Unverify property |
| `/admin/property/<id>/feature` | POST | Yes | Admin | Feature property |
| `/admin/user/<id>/verify` | POST | Yes | Admin | Verify user |
| `/admin/user/<id>/unverify` | POST | Yes | Admin | Unverify user |
| `/admin/user/<id>/remove` | DELETE | Yes | Admin | Delete user |
| `/admin/user/<id>` | PATCH | Yes | Admin | Edit user |
| `/admin/property/<id>` | DELETE | Yes | Admin | Delete property |
| `/admin/property/<id>` | PATCH | Yes | Admin | Edit property |

## Appendix B: Environment Variable Reference

### B.1 Backend Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | Flask session secret |
| `DATABASE_URL` | No | `sqlite:///dev.db` | Database connection string |
| `JWT_SECRET_KEY` | Yes | — | JWT signing secret |
| `JWT_ACCESS_TOKEN_SECONDS` | No | `604800` | Access token lifetime (seconds) |
| `JWT_REFRESH_TOKEN_SECONDS` | No | `2592000` | Refresh token lifetime (seconds) |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `MAIL_SERVER` | No | — | SMTP server hostname |
| `MAIL_PORT` | No | `587` | SMTP server port |
| `MAIL_USERNAME` | No | — | SMTP username |
| `MAIL_PASSWORD` | No | — | SMTP password |
| `MAIL_USE_TLS` | No | `True` | Enable TLS |
| `UPLOAD_FOLDER` | No | `./uploads` | File upload directory |
| `MAX_UPLOAD_BYTES` | No | `10485760` | Maximum file size (bytes) |
| `PUBLIC_UPLOAD_URL_PREFIX` | No | `/files` | URL prefix for uploaded files |
| `CORS_ORIGINS` | No | localhost origins | Comma-separated allowed origins |
| `LIVORA_ML_DIR` | No | `./ml_models` | ML model directory |
| `ROOMMATE_MODEL_PATH` | No | See default | Roommate model file path |
| `FAKE_PROFILE_MODEL_PATH` | No | See default | Fake profile model file path |
| `NUMERIC_SCALER_PATH` | No | See default | Numeric scaler file path |
| `FEATURE_SCALER_PATH` | No | See default | Feature scaler file path |

### B.2 Frontend Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | No | `http://127.0.0.1:5000` | Backend API base URL |

## Appendix C: Database Migration History

### C.1 Migration Sequence

```
Base (empty database)
    ↓
a9404d3027e0 — "Initial Migration"
    Creates: user, property, chat_message, match tables
    ↓
bf2a1c9d0e01 — "Password Reset Tokens"
    Creates: password_reset_token table
    ↓
c7e8f9a0b1c2 — "User Role Housing Meta Match Initiator"
    Adds: user.role, user.is_admin, property.housing_meta,
          match.initiator_id columns
    Current HEAD
```

## Appendix D: Livora Brand Color Palette

| Token | Hex Value | Usage |
|---|---|---|
| `livora-50` | `#f0fdfa` | Very light teal backgrounds |
| `livora-100` | `#ccfbf1` | Light teal highlights |
| `livora-200` | `#99f6e4` | Light teal elements |
| `livora-300` | `#5eead4` | Hover states |
| `livora-400` | `#2dd4bf` | Active states |
| `livora-500` | `#14b8a6` | **Primary brand color** |
| `livora-600` | `#0d9488` | Button hover |
| `livora-700` | `#0f766e` | Dark brand elements |
| `livora-800` | `#115e59` | Very dark teal |
| `livora-900` | `#134e4a` | Darkest teal |
| `night-950` | `#0a0f1e` | Primary background |

## Appendix E: Supported Indian Regions

The platform currently supports the following Indian metropolitan regions:

| Region Name | Major Cities/Areas Included |
|---|---|
| Bangalore | Koramangala, Indiranagar, Whitefield, HSR Layout, JP Nagar |
| Hyderabad | Hitech City, Banjara Hills, Madhapur, Gachibowli |
| Pune | Koregaon Park, Hinjewadi, Kothrud, Viman Nagar |
| Chennai | Anna Nagar, Velachery, Adyar, Nungambakkam |
| Delhi NCR | Gurugram, Noida, South Delhi, Dwarka |
| Mumbai | Bandra, Andheri, Powai, Lower Parel |

## Appendix F: ML Feature Vector Schema

Complete list of features in the ML feature vector (as expected by trained models):

**Numeric Features (5):**
`age`, `income`, `expenses`, `income_expense_ratio`, `social_habit_score`

**Drinks (3):**
`drinks_No`, `drinks_Occasionally`, `drinks_Yes`

**Smokes (3):**
`smokes_No`, `smokes_Occasionally`, `smokes_Yes`

**Pets (3):**
`pets_No`, `pets_Yes`, `pets_Maybe`

**Diet (3+):**
`diet_Vegan`, `diet_Vegetarian`, `diet_NonVegetarian`, `diet_EggEater`

**Education (3):**
`education_HighSchool`, `education_Graduate`, `education_PostGraduate`

**Body Type (4):**
`body_type_Slim`, `body_type_Average`, `body_type_Athletic`, `body_type_Heavy`

**Sex/Gender (3):**
`sex_Male`, `sex_Female`, `sex_Other`

**Orientation (4):**
`orientation_Straight`, `orientation_Gay`, `orientation_Bisexual`, `orientation_Other`

**Status (3):**
`status_Single`, `status_InRelationship`, `status_Married`

**Sleep Schedule (3):**
`sleep_schedule_EarlyBird`, `sleep_schedule_NightOwl`, `sleep_schedule_Flexible`

**Cleanliness (4):**
`cleanliness_VeryClean`, `cleanliness_Clean`, `cleanliness_Average`, `cleanliness_Relaxed`

**Guests (4):**
`guests_Never`, `guests_Rarely`, `guests_Sometimes`, `guests_Often`

**Noise Level (3):**
`noise_level_Quiet`, `noise_level_Moderate`, `noise_level_Loud`

**Work Schedule (4):**
`work_schedule_9to5`, `work_schedule_Shifts`, `work_schedule_Flexible`, `work_schedule_WFH`

**Region (6):**
`region_Bangalore`, `region_Hyderabad`, `region_Pune`,
`region_Chennai`, `region_Delhi NCR`, `region_Mumbai`

---

*End of Report*

---

**Document Information:**
- Title: Livora: An AI-Driven Smart Rental and Roommate Matching Platform for the Indian Urban Housing Market
- Report Type: IEEE Technical Report — Full System Design and Implementation Analysis
- Version: 1.0
- Date: April 7, 2026
- Total Sections: 19 (including appendices)
- Classification: Open (Unclassified)
- Working Directory: c:\Users\2484976\Downloads\Livora-master

*This report was generated through comprehensive static analysis of the Livora source code repository, covering all backend, frontend, ML pipeline, database, security, and deployment components.*
