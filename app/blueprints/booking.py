"""Online table booking (incl. VIP) and status lookup."""
from datetime import datetime

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify)
from flask_login import current_user

from ..extensions import db
from ..models import Booking, Notification

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        date_raw = request.form.get("date", "")
        try:
            res_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
        except ValueError:
            res_date = None

        if not name or not phone or not res_date:
            flash("Заполните имя, телефон и дату.", "error")
            return render_template("booking.html")

        b = Booking(
            user_id=current_user.id if current_user.is_authenticated else None,
            name=name,
            phone=phone,
            guests=int(request.form.get("guests", 2) or 2),
            res_date=res_date,
            res_time=request.form.get("time", "19:00"),
            special_request=request.form.get("special_request", "").strip(),
            is_vip=bool(request.form.get("is_vip")),
            status="Pending",
        )
        db.session.add(b)
        if current_user.is_authenticated:
            db.session.add(Notification(
                user_id=current_user.id,
                message="Ваша бронь принята и ожидает подтверждения.",
            ))
        db.session.commit()
        flash("Бронь отправлена! Статус: Pending. Мы скоро подтвердим.", "success")
        return redirect(url_for("booking.booking", submitted=b.id))

    return render_template("booking.html")


@booking_bp.route("/api/booking/<int:bid>/status")
def booking_status(bid):
    b = db.session.get(Booking, bid)
    if not b:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": b.id, "status": b.status})
