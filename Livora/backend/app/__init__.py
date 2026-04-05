import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Extensions
ma = Marshmallow()
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

load_dotenv()


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    upload_dir = os.path.abspath(os.path.join(base_dir, "..", "uploads"))

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///livora.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "jwt-secret"),
        JWT_ACCESS_TOKEN_SECONDS=int(os.getenv("JWT_ACCESS_TOKEN_SECONDS", "604800")),
        JWT_REFRESH_TOKEN_SECONDS=int(os.getenv("JWT_REFRESH_TOKEN_SECONDS", "2592000")),
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True") == "True",
        MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "False") == "True",
        UPLOAD_FOLDER=upload_dir,
        MAX_UPLOAD_BYTES=int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024))),
        PUBLIC_UPLOAD_URL_PREFIX=os.getenv("PUBLIC_UPLOAD_URL_PREFIX", "/files"),
    )

    _cors = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:3000,http://localhost:3000",
    )
    _origins = [o.strip() for o in _cors.split(",") if o.strip()]
    CORS(app, origins=_origins, supports_credentials=True)
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    Migrate(app, db)

    from app.models import user, property, chat, match, password_reset
    from app.utils.exceptions import register_error_handlers

    register_error_handlers(app)

    from .routes import register_blueprints
    from .routes.upload import register_upload_file_route

    register_blueprints(app)
    register_upload_file_route(app)

    from .socket_events import register_socketio_handlers

    register_socketio_handlers(socketio)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "livora-backend"}

    _register_cli(app)

    return app


def _register_cli(app):
    import click

    @app.cli.command("create-admin")
    @click.option("--email", required=True)
    @click.option("--password", required=True)
    @click.option("--name", default="Administrator")
    def create_admin(email, password, name):
        """Create or promote an admin user."""
        from app.models.user import User

        u = User.query.filter_by(email=email).first()
        if u:
            u.is_admin = True
            u.role = "admin"
            u.set_password(password)
            u.name = name
        else:
            u = User(email=email, name=name, is_admin=True, role="admin")
            u.set_password(password)
            db.session.add(u)
        db.session.commit()
        click.echo(f"Admin ready: {email}")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Create demo owner + admin logins for local development (idempotent)."""
        from app.models.user import User

        demo_password = "LivoraDemo2026!"

        admin_email = "demo-admin@livora.local"
        u = User.query.filter_by(email=admin_email).first()
        if u:
            u.is_admin = True
            u.role = "admin"
            u.set_password(demo_password)
            u.name = "Demo Admin"
        else:
            u = User(
                email=admin_email,
                name="Demo Admin",
                is_admin=True,
                role="admin",
            )
            u.set_password(demo_password)
            db.session.add(u)

        owner_email = "demo-owner@livora.local"
        o = User.query.filter_by(email=owner_email).first()
        if o:
            o.role = "owner"
            o.is_admin = False
            o.set_password(demo_password)
            o.name = "Demo Owner"
        else:
            o = User(
                email=owner_email,
                name="Demo Owner",
                is_admin=False,
                role="owner",
            )
            o.set_password(demo_password)
            db.session.add(o)

        db.session.commit()
        click.echo("Demo accounts (password for both): " + demo_password)
        click.echo(f"  Admin: {admin_email}")
        click.echo(f"  Owner: {owner_email}")

    @app.cli.command("seed-diverse")
    def seed_diverse_cmd():
        """Seed many tenant/owner users and Indian-city listings (see app/seed_diverse.py)."""
        from app.seed_diverse import SEED_PASSWORD, run_seed_diverse

        run_seed_diverse()
        click.echo("Seed complete.")
        click.echo(f"  Password for all seed.* users: {SEED_PASSWORD}")
        click.echo("  Tenants: seed.t01@livora.local ... seed.t36@livora.local")
        click.echo("  Owners:  seed.o01@livora.local ... seed.o08@livora.local")
