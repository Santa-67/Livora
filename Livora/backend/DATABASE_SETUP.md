# Livora Backend Database Setup Guide

1. **Install Requirements**
   - Run: `pip install -r requirements.txt`

2. **Configure Environment**
   - Copy `.env.example` to `.env` and fill in your secrets.
   - Default DB is SQLite. For production, set `DATABASE_URL` to your Postgres/MySQL URI.

3. **Initialize Database**
   - Run: `flask db init`
   - Run: `flask db migrate -m "Initial migration"`
   - Run: `flask db upgrade`

4. **Run the App**
   - Run: `flask run` or `python run.py`

5. **(Optional) Create Admin User**
   - Use Flask shell or add a registration route for admin creation.

# Flask-Migrate and SQLAlchemy are already configured in app/__init__.py.
# For questions, see README.md or contact the maintainer.
