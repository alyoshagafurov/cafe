"""REST API layer with JWT authentication.

Demonstrates the stateless token security required by the brief, alongside
the cookie-based Flask-Login sessions used by the web UI.
"""
from flask import Blueprint, request, jsonify

from ..extensions import db
from ..models import User, MenuItem, MenuCategory, Booking
from ..utils import generate_jwt, jwt_required

api_bp = Blueprint("api", __name__)


@api_bp.route("/auth/token", methods=["POST"])
def token():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(username=data.get("username", "")).first()
    if user and user.check_password(data.get("password", "")):
        return jsonify({"token": generate_jwt(user), "role": user.role})
    return jsonify({"error": "Invalid credentials"}), 401


@api_bp.route("/menu")
def api_menu():
    cats = MenuCategory.query.order_by(MenuCategory.sort_order).all()
    return jsonify([{
        "category": c.name,
        "slug": c.slug,
        "items": [{
            "id": i.id, "title": i.title, "price": i.price,
            "calories": i.calories, "badge": i.badge,
            "description": i.description,
        } for i in c.items if not i.is_hidden]
    } for c in cats])


@api_bp.route("/me")
@jwt_required
def api_me():
    user = db.session.get(User, request.jwt_user_id)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": user.id, "username": user.username, "role": user.role,
        "is_vip": user.is_vip, "points": user.points,
    })


@api_bp.route("/bookings", methods=["POST"])
@jwt_required
def api_create_booking():
    from datetime import datetime
    data = request.get_json(silent=True) or {}
    try:
        res_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    except (KeyError, ValueError):
        return jsonify({"error": "valid 'date' (YYYY-MM-DD) required"}), 400
    b = Booking(user_id=request.jwt_user_id, name=data.get("name", ""),
                phone=data.get("phone", ""), guests=int(data.get("guests", 2)),
                res_date=res_date, res_time=data.get("time", "19:00"),
                is_vip=bool(data.get("is_vip")), status="Pending")
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id, "status": b.status}), 201
