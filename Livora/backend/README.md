# Livora Backend

Smart Rental and Roommate Finding Platform (Flask Backend)

## Features
- User authentication (OAuth + Email)
- User profiles (budget, lifestyle, preferences)
- AI-based roommate matching
- Search filters
- Property listings (CRUD, images, videos, map integration)
- Real-time availability
- Virtual tours scheduling
- In-app chat
- AI recommendation engine
- Admin panel
- Monetization (subscriptions, credits, featured listings)

## Setup
1. Clone the repo
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in values
5. Run migrations: `flask db upgrade`
6. Start server: `python run.py`

## Structure
- `app/` - Main application code
- `models/` - SQLAlchemy models
- `routes/` - Flask blueprints (API endpoints)
- `services/` - Business logic, AI, etc.
- `schemas/` - Marshmallow schemas
- `utils/` - Utilities, validators, exceptions
- `tests/` - Unit/integration tests

## Notes
- Frontend is React (not included here)
- AI/ML logic is a placeholder, extend as needed
- Use best practices for security, validation, and error handling
