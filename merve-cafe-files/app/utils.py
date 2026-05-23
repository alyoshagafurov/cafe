"""Helper utilities: role decorators, JWT tokens, file uploads."""
import os
import uuid
from functools import wraps
from datetime import datetime

import jwt
from flask import current_app, abort, request, jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename


# --------------------------------------------------------------------------- #
#  ROLE PROTECTION
# --------------------------------------------------------------------------- #
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


# --------------------------------------------------------------------------- #
#  JWT (used by the REST API layer for stateless auth)
# --------------------------------------------------------------------------- #
def generate_jwt(user):
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + current_app.config["JWT_EXPIRES"],
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_jwt(token):
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else None
        data = decode_jwt(token) if token else None
        if not data:
            return jsonify({"error": "Unauthorized — valid Bearer token required."}), 401
        request.jwt_user_id = int(data["sub"])
        request.jwt_role = data.get("role")
        return view(*args, **kwargs)
    return wrapped


# --------------------------------------------------------------------------- #
#  UPLOADS
# --------------------------------------------------------------------------- #
def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_IMAGE_EXT"]


def save_upload(file_storage, subfolder=""):
    """Save an uploaded image, return the stored filename (relative)."""
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, secure_filename(name)))
    return name
