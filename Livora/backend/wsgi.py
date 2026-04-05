"""WSGI entry for gunicorn/uwsgi (HTTP only; use run.py for Socket.IO dev server)."""

from app import create_app

app = create_app()
