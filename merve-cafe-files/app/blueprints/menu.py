"""Menu page + search / filter API."""
from flask import Blueprint, render_template, request, jsonify

from ..models import MenuItem, MenuCategory

menu_bp = Blueprint("menu", __name__)


@menu_bp.route("/menu")
def menu():
    categories = MenuCategory.query.order_by(MenuCategory.sort_order).all()
    items = MenuItem.query.filter_by(is_hidden=False).order_by(MenuItem.popularity.desc()).all()
    return render_template("menu.html", categories=categories, items=items)


@menu_bp.route("/api/menu/search")
def search():
    """Live search + filter used by the menu page JS."""
    q = request.args.get("q", "").strip().lower()
    cat = request.args.get("category", "").strip()
    badge = request.args.get("badge", "").strip()
    sort = request.args.get("sort", "popular")

    query = MenuItem.query.filter_by(is_hidden=False)
    if cat and cat != "all":
        category = MenuCategory.query.filter_by(slug=cat).first()
        if category:
            query = query.filter_by(category_id=category.id)
    if badge:
        query = query.filter_by(badge=badge)

    items = query.all()
    if q:
        items = [i for i in items if q in i.title.lower()
                 or q in (i.description or "").lower()
                 or q in (i.ingredients or "").lower()]

    if sort == "price_asc":
        items.sort(key=lambda i: i.price)
    elif sort == "price_desc":
        items.sort(key=lambda i: i.price, reverse=True)
    else:
        items.sort(key=lambda i: i.popularity, reverse=True)

    return jsonify([{
        "id": i.id,
        "title": i.title,
        "description": i.description,
        "ingredients": i.ingredients,
        "price": i.price,
        "calories": i.calories,
        "popularity": i.popularity,
        "badge": i.badge,
        "category": i.category.slug if i.category else "",
        "photo_url": i.photo_url,
    } for i in items])
