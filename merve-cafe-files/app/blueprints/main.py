"""Public-facing pages: home, about, contact, gallery, blog."""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..extensions import db
from ..models import (MenuItem, MenuCategory, Gallery, BlogPost,
                      ContactMessage, Promotion, SiteContent)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = (MenuItem.query.filter_by(is_hidden=False)
                .order_by(MenuItem.popularity.desc()).limit(6).all())
    categories = MenuCategory.query.order_by(MenuCategory.sort_order).all()
    gallery = Gallery.query.order_by(Gallery.sort_order).limit(6).all()
    promos = Promotion.query.filter_by(active=True).limit(3).all()
    posts = (BlogPost.query.filter_by(published=True)
             .order_by(BlogPost.created_at.desc()).limit(3).all())
    return render_template("index.html", featured=featured, categories=categories,
                           gallery=gallery, promos=promos, posts=posts)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/gallery")
def gallery():
    sections = ["Interior", "Food", "Drinks", "Atmosphere", "VIP zone"]
    images = Gallery.query.order_by(Gallery.sort_order).all()
    return render_template("gallery.html", images=images, sections=sections)


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        msg = ContactMessage(
            name=request.form.get("name", "").strip(),
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
            message=request.form.get("message", "").strip(),
        )
        if not msg.name or not msg.message:
            flash("Заполните имя и сообщение.", "error")
        else:
            db.session.add(msg)
            db.session.commit()
            flash("Спасибо! Мы свяжемся с вами в ближайшее время.", "success")
            return redirect(url_for("main.contact"))
    return render_template("contact.html")


# --- BLOG ----------------------------------------------------------------- #
@main_bp.route("/blog")
def blog():
    posts = (BlogPost.query.filter_by(published=True)
             .order_by(BlogPost.created_at.desc()).all())
    return render_template("blog/list.html", posts=posts)


@main_bp.route("/blog/<slug>")
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    more = (BlogPost.query.filter(BlogPost.id != post.id, BlogPost.published == True)
            .order_by(BlogPost.created_at.desc()).limit(3).all())
    return render_template("blog/detail.html", post=post, more=more)
