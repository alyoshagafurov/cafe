"""Customer account: dashboard, favorites, profile, notifications."""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify)
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Booking, Order, Favorite, MenuItem, Notification
from ..utils import save_upload

account_bp = Blueprint("account", __name__)


@account_bp.route("/account")
@login_required
def dashboard():
    bookings = (Booking.query.filter_by(user_id=current_user.id)
                .order_by(Booking.created_at.desc()).all())
    orders = (Order.query.filter_by(user_id=current_user.id)
              .order_by(Order.created_at.desc()).all())
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    notes = (Notification.query.filter_by(user_id=current_user.id)
             .order_by(Notification.created_at.desc()).limit(15).all())
    current = [b for b in bookings if b.status != "Rejected"][:5]
    return render_template("account/dashboard.html", bookings=bookings,
                           current=current, orders=orders, favorites=favorites,
                           notes=notes)


@account_bp.route("/account/profile", methods=["POST"])
@login_required
def update_profile():
    current_user.full_name = request.form.get("full_name", "").strip()
    current_user.phone = request.form.get("phone", "").strip()
    avatar = save_upload(request.files.get("avatar"), "avatars")
    if avatar:
        current_user.avatar = avatar
    db.session.commit()
    flash("Профиль обновлён.", "success")
    return redirect(url_for("account.dashboard"))


@account_bp.route("/api/favorite/<int:item_id>", methods=["POST"])
@login_required
def toggle_favorite(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    fav = Favorite.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    if fav:
        db.session.delete(fav)
        active = False
    else:
        db.session.add(Favorite(user_id=current_user.id, item_id=item_id))
        active = True
    db.session.commit()
    return jsonify({"favorite": active})


@account_bp.route("/account/notifications/read", methods=["POST"])
@login_required
def read_notes():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({"is_read": True})
    db.session.commit()
    return jsonify({"ok": True})
