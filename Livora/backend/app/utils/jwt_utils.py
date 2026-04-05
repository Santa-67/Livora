"""Helpers for Flask-JWT-Extended (identity is stored as string)."""


def jwt_user_id():
    from flask_jwt_extended import get_jwt_identity

    return int(get_jwt_identity())
