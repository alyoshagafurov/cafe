"""Online ordering: session cart, checkout, tracking, loyalty accrual."""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, session)
from flask_login import current_user

from ..extensions import db
from ..models import MenuItem, Order, OrderItem, LoyaltyPoints, Notification

orders_bp = Blueprint("orders", __name__)


def _cart():
    return session.setdefault("cart", {})


@orders_bp.route("/api/cart/add", methods=["POST"])
def cart_add():
    data = request.get_json(silent=True) or {}
    item = db.session.get(MenuItem, int(data.get("id", 0)))
    if not item:
        return jsonify({"error": "item not found"}), 404
    cart = _cart()
    key = str(item.id)
    qty = cart.get(key, {}).get("qty", 0) + int(data.get("qty", 1))
    cart[key] = {"title": item.title, "price": item.price, "qty": max(1, qty)}
    session.modified = True
    return jsonify({"ok": True, "count": sum(i["qty"] for i in cart.values())})


@orders_bp.route("/api/cart/set", methods=["POST"])
def cart_set():
    data = request.get_json(silent=True) or {}
    cart = _cart()
    key = str(data.get("id"))
    qty = int(data.get("qty", 0))
    if key in cart:
        if qty <= 0:
            cart.pop(key)
        else:
            cart[key]["qty"] = qty
    session.modified = True
    total = sum(i["price"] * i["qty"] for i in cart.values())
    return jsonify({"ok": True, "count": sum(i["qty"] for i in cart.values()),
                    "total": round(total, 2)})


@orders_bp.route("/api/cart")
def cart_view():
    cart = _cart()
    total = sum(i["price"] * i["qty"] for i in cart.values())
    return jsonify({"items": cart, "total": round(total, 2),
                    "count": sum(i["qty"] for i in cart.values())})


@orders_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = _cart()
    total = round(sum(i["price"] * i["qty"] for i in cart.values()), 2)
    if request.method == "POST":
        if not cart:
            flash("Корзина пуста.", "error")
            return redirect(url_for("menu.menu"))
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=request.form.get("name", "").strip(),
            phone=request.form.get("phone", "").strip(),
            address=request.form.get("address", "").strip(),
            fulfillment=request.form.get("fulfillment", "delivery"),
            total=total,
            status="Preparing",
        )
        db.session.add(order)
        db.session.flush()
        coffees = 0
        for key, line in cart.items():
            db.session.add(OrderItem(order_id=order.id, item_id=int(key),
                                     title=line["title"], price=line["price"],
                                     quantity=line["qty"]))
            mi = db.session.get(MenuItem, int(key))
            if mi and mi.category and mi.category.slug == "coffee":
                coffees += line["qty"]

        # loyalty accrual
        if current_user.is_authenticated:
            lp = current_user.loyalty or LoyaltyPoints(user_id=current_user.id)
            if not lp.id:
                db.session.add(lp)
            lp.points += int(total)
            lp.coffees_bought += coffees
            while lp.coffees_bought >= 5:
                lp.coffees_bought -= 5
                lp.free_coffees += 1
                db.session.add(Notification(
                    user_id=current_user.id,
                    message="🎉 Поздравляем! Вам начислен бесплатный кофе."))
            lp.recompute_tier()
            db.session.add(Notification(
                user_id=current_user.id,
                message=f"Заказ #{order.id} принят. Статус: Preparing."))

        db.session.commit()
        session["cart"] = {}
        session.modified = True
        flash("Заказ оформлен! Отслеживайте статус ниже.", "success")
        return redirect(url_for("orders.track", oid=order.id))
    return render_template("order/checkout.html", cart=cart, total=total)


@orders_bp.route("/order/<int:oid>")
def track(oid):
    order = Order.query.get_or_404(oid)
    return render_template("order/track.html", order=order)


@orders_bp.route("/api/order/<int:oid>/status")
def order_status(oid):
    order = db.session.get(Order, oid)
    if not order:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": order.id, "status": order.status})
