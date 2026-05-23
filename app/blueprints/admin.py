"""Luxury admin dashboard and management endpoints."""
from datetime import datetime, timedelta
from collections import Counter

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify)
from flask_login import login_required, current_user

from ..extensions import db
from ..models import (User, Booking, Order, OrderItem, MenuItem, MenuCategory,
                      Promotion, Gallery, BlogPost, ContactMessage,
                      Notification, SiteContent)
from ..utils import admin_required, save_upload

admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
@login_required
def guard():
    if not current_user.is_admin:
        from flask import abort
        abort(403)


# --------------------------------------------------------------------------- #
#  DASHBOARD + ANALYTICS
# --------------------------------------------------------------------------- #
@admin_bp.route("/")
def dashboard():
    stats = {
        "orders": Order.query.count(),
        "revenue": round(sum(o.total for o in Order.query.all()), 2),
        "bookings": Booking.query.count(),
        "pending": Booking.query.filter_by(status="Pending").count(),
        "customers": User.query.filter_by(role="customer").count(),
        "vip": User.query.filter_by(is_vip=True).count(),
    }

    # revenue last 7 days
    today = datetime.utcnow().date()
    days, revenue = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        days.append(d.strftime("%d.%m"))
        day_total = sum(o.total for o in Order.query.all()
                        if o.created_at and o.created_at.date() == d)
        revenue.append(round(day_total, 2))

    # popular dishes
    counter = Counter()
    for oi in OrderItem.query.all():
        counter[oi.title] += oi.quantity
    popular = counter.most_common(5)

    # busiest hours (from bookings)
    hour_counter = Counter()
    for b in Booking.query.all():
        hour_counter[b.res_time] += 1
    busiest = hour_counter.most_common(5)

    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(6).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(6).all()

    return render_template("admin/dashboard.html", stats=stats, days=days,
                           revenue=revenue, popular=popular, busiest=busiest,
                           recent_bookings=recent_bookings, recent_orders=recent_orders)


# --------------------------------------------------------------------------- #
#  BOOKINGS
# --------------------------------------------------------------------------- #
@admin_bp.route("/bookings")
def bookings():
    status = request.args.get("status", "")
    q = Booking.query
    if status:
        q = q.filter_by(status=status)
    rows = q.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", rows=rows, status=status)


@admin_bp.route("/bookings/<int:bid>/<action>", methods=["POST"])
def booking_action(bid, action):
    b = Booking.query.get_or_404(bid)
    mapping = {"accept": "Approved", "reject": "Rejected", "pending": "Pending"}
    if action in mapping:
        b.status = mapping[action]
        if b.user_id:
            db.session.add(Notification(
                user_id=b.user_id,
                message=f"Статус вашей брони на {b.res_date}: {b.status}."))
        db.session.commit()
    return redirect(request.referrer or url_for("admin.bookings"))


# --------------------------------------------------------------------------- #
#  ORDERS
# --------------------------------------------------------------------------- #
@admin_bp.route("/orders")
def orders():
    rows = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", rows=rows)


@admin_bp.route("/orders/<int:oid>/status", methods=["POST"])
def order_status(oid):
    o = Order.query.get_or_404(oid)
    o.status = request.form.get("status", o.status)
    if o.user_id:
        db.session.add(Notification(user_id=o.user_id,
                                    message=f"Заказ #{o.id}: {o.status}."))
    db.session.commit()
    return redirect(url_for("admin.orders"))


# --------------------------------------------------------------------------- #
#  MENU MANAGEMENT
# --------------------------------------------------------------------------- #
@admin_bp.route("/menu")
def menu():
    categories = MenuCategory.query.order_by(MenuCategory.sort_order).all()
    items = MenuItem.query.order_by(MenuItem.category_id).all()
    return render_template("admin/menu.html", categories=categories, items=items)


@admin_bp.route("/menu/save", methods=["POST"])
def menu_save():
    iid = request.form.get("id")
    item = db.session.get(MenuItem, int(iid)) if iid else MenuItem()
    item.title = request.form.get("title", "").strip()
    item.category_id = int(request.form.get("category_id"))
    item.description = request.form.get("description", "").strip()
    item.ingredients = request.form.get("ingredients", "").strip()
    item.price = float(request.form.get("price", 0) or 0)
    item.calories = int(request.form.get("calories", 0) or 0)
    item.popularity = int(request.form.get("popularity", 0) or 0)
    item.badge = request.form.get("badge", "")
    item.is_hidden = bool(request.form.get("is_hidden"))
    photo = save_upload(request.files.get("photo"), "menu")
    if photo:
        item.photo = photo
    elif request.form.get("photo_url"):
        item.photo = request.form.get("photo_url").strip()
    if not iid:
        db.session.add(item)
    db.session.commit()
    flash("Блюдо сохранено.", "success")
    return redirect(url_for("admin.menu"))


@admin_bp.route("/menu/<int:iid>/delete", methods=["POST"])
def menu_delete(iid):
    item = MenuItem.query.get_or_404(iid)
    db.session.delete(item)
    db.session.commit()
    flash("Блюдо удалено.", "info")
    return redirect(url_for("admin.menu"))


@admin_bp.route("/menu/<int:iid>/toggle", methods=["POST"])
def menu_toggle(iid):
    item = MenuItem.query.get_or_404(iid)
    item.is_hidden = not item.is_hidden
    db.session.commit()
    return redirect(url_for("admin.menu"))


@admin_bp.route("/categories/save", methods=["POST"])
def category_save():
    name = request.form.get("name", "").strip()
    slug = request.form.get("slug", "").strip().lower().replace(" ", "-")
    if name and slug:
        cat = MenuCategory(name=name, slug=slug,
                           icon=request.form.get("icon", "✦"),
                           sort_order=int(request.form.get("sort_order", 0) or 0))
        db.session.add(cat)
        db.session.commit()
        flash("Категория добавлена.", "success")
    return redirect(url_for("admin.menu"))


# --------------------------------------------------------------------------- #
#  PROMOTIONS
# --------------------------------------------------------------------------- #
@admin_bp.route("/promotions")
def promotions():
    rows = Promotion.query.order_by(Promotion.created_at.desc()).all()
    return render_template("admin/promotions.html", rows=rows)


@admin_bp.route("/promotions/save", methods=["POST"])
def promo_save():
    valid = request.form.get("valid_until")
    p = Promotion(
        title=request.form.get("title", "").strip(),
        description=request.form.get("description", "").strip(),
        code=request.form.get("code", "").strip().upper() or None,
        discount_percent=int(request.form.get("discount_percent", 0) or 0),
        active=bool(request.form.get("active")),
        valid_until=datetime.strptime(valid, "%Y-%m-%d").date() if valid else None,
    )
    db.session.add(p)
    db.session.commit()
    flash("Акция создана.", "success")
    return redirect(url_for("admin.promotions"))


@admin_bp.route("/promotions/<int:pid>/delete", methods=["POST"])
def promo_delete(pid):
    db.session.delete(Promotion.query.get_or_404(pid))
    db.session.commit()
    return redirect(url_for("admin.promotions"))


# --------------------------------------------------------------------------- #
#  CUSTOMERS
# --------------------------------------------------------------------------- #
@admin_bp.route("/customers")
def customers():
    rows = User.query.filter_by(role="customer").order_by(User.created_at.desc()).all()
    return render_template("admin/customers.html", rows=rows)


@admin_bp.route("/customers/<int:uid>/vip", methods=["POST"])
def customer_vip(uid):
    u = User.query.get_or_404(uid)
    u.is_vip = not u.is_vip
    db.session.commit()
    return redirect(url_for("admin.customers"))


# --------------------------------------------------------------------------- #
#  CONTENT (hero / homepage)
# --------------------------------------------------------------------------- #
@admin_bp.route("/content", methods=["GET", "POST"])
def content():
    keys = ["hero_title", "hero_subtitle", "hero_tagline",
            "about_text", "banner_text"]
    if request.method == "POST":
        for k in keys:
            val = request.form.get(k, "")
            row = SiteContent.query.filter_by(key=k).first()
            if not row:
                row = SiteContent(key=k)
                db.session.add(row)
            row.value = val
        db.session.commit()
        flash("Контент обновлён.", "success")
        return redirect(url_for("admin.content"))
    values = {k: SiteContent.get(k) for k in keys}
    return render_template("admin/content.html", values=values)


# --------------------------------------------------------------------------- #
#  GALLERY
# --------------------------------------------------------------------------- #
@admin_bp.route("/gallery", methods=["GET", "POST"])
def gallery():
    if request.method == "POST":
        img = save_upload(request.files.get("image"), "")
        url = request.form.get("image_url", "").strip()
        if img or url:
            db.session.add(Gallery(
                title=request.form.get("title", "").strip(),
                section=request.form.get("section", "Interior"),
                image=("uploads/" + img) if img else url,
                sort_order=int(request.form.get("sort_order", 0) or 0)))
            db.session.commit()
            flash("Фото добавлено в галерею.", "success")
        return redirect(url_for("admin.gallery"))
    rows = Gallery.query.order_by(Gallery.sort_order).all()
    return render_template("admin/gallery.html", rows=rows)


@admin_bp.route("/gallery/<int:gid>/delete", methods=["POST"])
def gallery_delete(gid):
    db.session.delete(Gallery.query.get_or_404(gid))
    db.session.commit()
    return redirect(url_for("admin.gallery"))


# --------------------------------------------------------------------------- #
#  BLOG
# --------------------------------------------------------------------------- #
@admin_bp.route("/blog")
def blog():
    rows = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/blog.html", rows=rows)


@admin_bp.route("/blog/save", methods=["POST"])
def blog_save():
    pid = request.form.get("id")
    post = db.session.get(BlogPost, int(pid)) if pid else BlogPost()
    post.title = request.form.get("title", "").strip()
    slug = request.form.get("slug", "").strip().lower().replace(" ", "-")
    post.slug = slug or post.title.lower().replace(" ", "-")
    post.excerpt = request.form.get("excerpt", "").strip()
    post.body = request.form.get("body", "").strip()
    post.category = request.form.get("category", "News")
    post.meta_description = request.form.get("meta_description", "").strip()
    post.published = bool(request.form.get("published"))
    cover = save_upload(request.files.get("cover"), "")
    if cover:
        post.cover = cover
    elif request.form.get("cover_url"):
        post.cover = request.form.get("cover_url").strip()
    if not pid:
        db.session.add(post)
    db.session.commit()
    flash("Пост сохранён.", "success")
    return redirect(url_for("admin.blog"))


@admin_bp.route("/blog/<int:pid>/delete", methods=["POST"])
def blog_delete(pid):
    db.session.delete(BlogPost.query.get_or_404(pid))
    db.session.commit()
    return redirect(url_for("admin.blog"))


# --------------------------------------------------------------------------- #
#  MESSAGES
# --------------------------------------------------------------------------- #
@admin_bp.route("/messages")
def messages():
    rows = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", rows=rows)
