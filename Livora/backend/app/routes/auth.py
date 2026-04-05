import datetime
import hashlib
import logging
import secrets

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mail import Message
from app import db, mail
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.schemas.user_schema import UserSchema
from app.utils.validators import sanitize_text

bp = Blueprint("auth", __name__, url_prefix="/auth")
logger = logging.getLogger(__name__)


def _send_reset_email(to_email: str, token_plain: str) -> None:
    if not current_app.config.get("MAIL_SERVER"):
        logger.warning(
            "MAIL_SERVER not set; password reset token for %s (dev only): %s",
            to_email,
            token_plain,
        )
        return
    body = (
        "Use this token with POST /auth/reset-password:\n\n"
        f"Token: {token_plain}\n\n"
        "This link expires in one hour."
    )
    msg = Message("Livora password reset", recipients=[to_email], body=body)
    try:
        mail.send(msg)
    except Exception as exc:  # noqa: BLE001 — SMTP/DNS/network must not break reset flow
        logger.warning(
            "Could not send reset email to %s (%s); token (dev fallback): %s",
            to_email,
            exc,
            token_plain,
        )


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    schema = UserSchema()
    try:
        validated = schema.load(data)
    except Exception as e:
        return jsonify({"error": "Validation failed", "details": str(e)}), 422
    email = validated.email
    password = data.get("password")
    name = validated.name
    if not password:
        return jsonify({"error": "Password is required"}), 400
    acct = (data.get("account_type") or "tenant").strip().lower()
    if acct not in ("tenant", "owner"):
        return jsonify({"error": "account_type must be tenant or owner"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    user = validated
    user.name = sanitize_text(user.name, max_length=100)
    if user.bio:
        user.bio = sanitize_text(user.bio, max_length=500)
    user.set_password(password)
    user.role = "owner" if acct == "owner" else "tenant"
    user.is_admin = False
    user.is_verified = False
    db.session.add(user)
    db.session.commit()
    access_token, refresh_token = _issue_tokens(user)
    return (
        jsonify(
            {
                "msg": "Registration successful",
                "user": user.to_dict(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ),
        201,
    )


@bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    if not email or not password or not name:
        return jsonify({"error": "Missing required fields"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    user = User(email=email, name=name)
    user.set_password(password)
    user.role = "tenant"
    user.is_admin = False
    user.is_verified = False
    db.session.add(user)
    db.session.commit()
    access_token, refresh_token = _issue_tokens(user)
    return jsonify(
        {
            "msg": "Signup successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    ), 201


def _issue_tokens(user: User):
    access = create_access_token(
        identity=str(user.id),
        expires_delta=datetime.timedelta(
            seconds=int(current_app.config.get("JWT_ACCESS_TOKEN_SECONDS", 604800))
        ),
    )
    refresh = create_refresh_token(
        identity=str(user.id),
        expires_delta=datetime.timedelta(
            seconds=int(current_app.config.get("JWT_REFRESH_TOKEN_SECONDS", 2592000))
        ),
    )
    return access, refresh


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    access_token, refresh_token = _issue_tokens(user)
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }
    )


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    uid = get_jwt_identity()
    access_token = create_access_token(
        identity=uid,
        expires_delta=datetime.timedelta(
            seconds=int(current_app.config.get("JWT_ACCESS_TOKEN_SECONDS", 604800))
        ),
    )
    return jsonify({"access_token": access_token})


@bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    msg = {"msg": "If that email is registered, you will receive reset instructions."}
    if not email:
        return jsonify(msg)
    user = User.query.filter_by(email=email).first()
    if user and user.password_hash:
        PasswordResetToken.query.filter_by(user_id=user.id, used=False).update(
            {"used": True}, synchronize_session=False
        )
        token_plain = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_plain.encode()).hexdigest()
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        row = PasswordResetToken(
            user_id=user.id, token_hash=token_hash, expires_at=expires, used=False
        )
        db.session.add(row)
        db.session.commit()
        _send_reset_email(user.email, token_plain)
    return jsonify(msg)


@bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token_plain = data.get("token")
    new_password = data.get("password")
    if not token_plain or not new_password:
        return jsonify({"error": "token and password required"}), 400
    if len(new_password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400
    th = hashlib.sha256(str(token_plain).encode()).hexdigest()
    row = PasswordResetToken.query.filter_by(token_hash=th, used=False).first()
    if not row or row.expires_at < datetime.datetime.utcnow():
        return jsonify({"error": "invalid or expired token"}), 400
    user = User.query.get(row.user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    user.set_password(new_password)
    row.used = True
    db.session.commit()
    return jsonify({"msg": "Password updated; you can log in now."})


def _oauth_upsert_user(email: str, name: str, provider: str, oauth_id: str) -> User:
    user = User.query.filter_by(oauth_provider=provider, oauth_id=oauth_id).first()
    if user:
        return user
    user = User.query.filter_by(email=email).first()
    if user:
        user.oauth_provider = provider
        user.oauth_id = oauth_id
        db.session.commit()
        return user
    user = User(
        email=email,
        name=sanitize_text(name or email.split("@")[0], max_length=100),
        oauth_provider=provider,
        oauth_id=oauth_id,
        password_hash=None,
    )
    db.session.add(user)
    db.session.commit()
    return user


@bp.route("/oauth/google", methods=["POST"])
def oauth_google():
    data = request.get_json() or {}
    id_token = data.get("id_token")
    if not id_token:
        return jsonify({"error": "id_token required"}), 400
    try:
        r = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=15,
        )
    except requests.RequestException as exc:
        return jsonify({"error": "Google verification failed", "details": str(exc)}), 502
    if r.status_code != 200:
        return jsonify({"error": "invalid id_token"}), 401
    info = r.json()
    email = info.get("email")
    sub = info.get("sub")
    name = info.get("name") or email
    if not email or not sub:
        return jsonify({"error": "Google token missing email or sub"}), 400
    user = _oauth_upsert_user(email, name, "google", sub)
    access_token, refresh_token = _issue_tokens(user)
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }
    )


@bp.route("/oauth/facebook", methods=["POST"])
def oauth_facebook():
    data = request.get_json() or {}
    access_token = data.get("access_token")
    if not access_token:
        return jsonify({"error": "access_token required"}), 400
    try:
        r = requests.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,name,email", "access_token": access_token},
            timeout=15,
        )
    except requests.RequestException as exc:
        return jsonify({"error": "Facebook verification failed", "details": str(exc)}), 502
    if r.status_code != 200:
        return jsonify({"error": "invalid access_token"}), 401
    info = r.json()
    oauth_id = info.get("id")
    name = info.get("name") or "User"
    email = info.get("email") or f"fb_{oauth_id}@facebook.placeholder"
    if not oauth_id:
        return jsonify({"error": "Facebook response missing id"}), 400
    user = _oauth_upsert_user(email, name, "facebook", str(oauth_id))
    jwt_access, jwt_refresh = _issue_tokens(user)
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify(
        {
            "access_token": jwt_access,
            "refresh_token": jwt_refresh,
            "user": user.to_dict(),
        }
    )


@bp.route("/oauth/<provider>", methods=["POST"])
def oauth_login(provider):
    p = (provider or "").lower()
    if p == "google":
        return oauth_google()
    if p == "facebook":
        return oauth_facebook()
    return jsonify({"error": f"Unknown provider: {provider}. Use google or facebook."}), 400


@bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    from app.utils.jwt_utils import jwt_user_id

    data = request.get_json() or {}
    old = data.get("current_password")
    new = data.get("new_password")
    if not new or len(new) < 8:
        return jsonify({"error": "new_password must be at least 8 characters"}), 400
    user = User.query.get(jwt_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.password_hash and (not old or not user.check_password(old)):
        return jsonify({"error": "current password incorrect"}), 400
    user.set_password(new)
    db.session.commit()
    return jsonify({"msg": "Password changed"})
