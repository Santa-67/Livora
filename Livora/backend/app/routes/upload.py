import os
import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from app.utils.jwt_utils import jwt_user_id

bp = Blueprint("upload", __name__, url_prefix="/upload")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/image", methods=["POST"])
@jwt_required()
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "file field required"}), 400

    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"error": "empty filename"}), 400
    if not _allowed_file(f.filename):
        return jsonify({"error": "only png, jpg, jpeg, gif, webp allowed"}), 400

    folder = Path(current_app.config["UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    ext = secure_filename(f.filename).rsplit(".", 1)[-1].lower()
    name = f"{jwt_user_id()}_{uuid.uuid4().hex}.{ext}"
    path = folder / name
    f.save(path)

    max_bytes = current_app.config.get("MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
    if path.stat().st_size > max_bytes:
        path.unlink(missing_ok=True)
        return jsonify({"error": f"file too large (max {max_bytes} bytes)"}), 400

    base = current_app.config.get("PUBLIC_UPLOAD_URL_PREFIX", "/files")
    url = f"{base.rstrip('/')}/{name}"
    return jsonify({"url": url, "filename": name}), 201


def register_upload_file_route(app):
    folder = app.config["UPLOAD_FOLDER"]
    prefix = app.config.get("PUBLIC_UPLOAD_URL_PREFIX", "/files").rstrip("/")

    @app.route(f"{prefix}/<path:name>")
    def uploaded_file(name):
        return send_from_directory(folder, name, max_age=3600)
