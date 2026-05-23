"""Database models for MERVE Café.

Covers: User, Booking, MenuCategory, MenuItem, Order, OrderItem,
LoyaltyPoints, Promotion, Gallery, BlogPost, Notification, ContactMessage
and a lightweight SiteContent table for editable homepage/hero content.
"""
from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


# --------------------------------------------------------------------------- #
#  USER & AUTH
# --------------------------------------------------------------------------- #
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default="default-avatar.svg")
    role = db.Column(db.String(20), default="customer")  # 'admin' | 'customer'
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    is_vip = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", lazy=True, cascade="all, delete-orphan")
    loyalty = db.relationship("LoyaltyPoints", backref="user", uselist=False,
                              cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy=True,
                                    cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="user", lazy=True,
                                cascade="all, delete-orphan")

    # password helpers ------------------------------------------------------
    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def points(self) -> int:
        return self.loyalty.points if self.loyalty else 0

    @property
    def avatar_url(self):
        if self.avatar and self.avatar.startswith("http"):
            return self.avatar
        if self.avatar and self.avatar.startswith("default-avatar"):
            return "img/" + self.avatar
        return "uploads/avatars/" + (self.avatar or "default-avatar.svg")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# --------------------------------------------------------------------------- #
#  MENU
# --------------------------------------------------------------------------- #
class MenuCategory(db.Model):
    __tablename__ = "menu_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    icon = db.Column(db.String(20), default="✦")
    sort_order = db.Column(db.Integer, default=0)

    items = db.relationship("MenuItem", backref="category", lazy=True,
                            cascade="all, delete-orphan")


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("menu_categories.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    ingredients = db.Column(db.String(300), default="")
    price = db.Column(db.Float, nullable=False, default=0.0)
    calories = db.Column(db.Integer, default=0)
    popularity = db.Column(db.Integer, default=0)  # 0-100
    photo = db.Column(db.String(255), default="")
    badge = db.Column(db.String(20), default="")   # 'best' | 'premium' | 'new'
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def photo_url(self):
        if self.photo and self.photo.startswith("http"):
            return self.photo
        if self.photo:
            return "uploads/menu/" + self.photo
        return "img/placeholder-%s.svg" % (self.category.slug if self.category else "coffee")


# --------------------------------------------------------------------------- #
#  BOOKINGS
# --------------------------------------------------------------------------- #
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    guests = db.Column(db.Integer, default=2)
    res_date = db.Column(db.Date, nullable=False)
    res_time = db.Column(db.String(10), nullable=False)
    special_request = db.Column(db.Text, default="")
    is_vip = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="Pending")  # Pending | Approved | Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------- #
#  ORDERS
# --------------------------------------------------------------------------- #
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    customer_name = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    address = db.Column(db.String(255), default="")
    fulfillment = db.Column(db.String(20), default="delivery")  # delivery | pickup
    total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="Preparing")  # Preparing | On the way | Delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True,
                            cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"))
    title = db.Column(db.String(120))
    price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=1)

    @property
    def subtotal(self):
        return round(self.price * self.quantity, 2)


# --------------------------------------------------------------------------- #
#  LOYALTY
# --------------------------------------------------------------------------- #
class LoyaltyPoints(db.Model):
    __tablename__ = "loyalty_points"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    points = db.Column(db.Integer, default=0)
    coffees_bought = db.Column(db.Integer, default=0)
    free_coffees = db.Column(db.Integer, default=0)
    tier = db.Column(db.String(20), default="Bronze")  # Bronze | Gold | Platinum

    def recompute_tier(self):
        if self.points >= 1000:
            self.tier = "Platinum"
        elif self.points >= 400:
            self.tier = "Gold"
        else:
            self.tier = "Bronze"


# --------------------------------------------------------------------------- #
#  FAVORITES
# --------------------------------------------------------------------------- #
class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    item = db.relationship("MenuItem")


# --------------------------------------------------------------------------- #
#  PROMOTIONS
# --------------------------------------------------------------------------- #
class Promotion(db.Model):
    __tablename__ = "promotions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    code = db.Column(db.String(40), unique=True)
    discount_percent = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    valid_until = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------- #
#  GALLERY
# --------------------------------------------------------------------------- #
class Gallery(db.Model):
    __tablename__ = "gallery"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), default="")
    section = db.Column(db.String(40), default="Interior")  # Interior|Food|Drinks|Atmosphere|VIP zone
    image = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    @property
    def image_url(self):
        if self.image.startswith("http"):
            return self.image
        if "/" in self.image:
            return self.image
        return "img/" + self.image


# --------------------------------------------------------------------------- #
#  BLOG
# --------------------------------------------------------------------------- #
class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.String(300), default="")
    body = db.Column(db.Text, default="")
    cover = db.Column(db.String(255), default="")
    category = db.Column(db.String(40), default="News")
    meta_description = db.Column(db.String(200), default="")
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def cover_url(self):
        if self.cover and self.cover.startswith("http"):
            return self.cover
        if self.cover:
            return "uploads/" + self.cover
        return "img/placeholder-atmosphere.svg"


# --------------------------------------------------------------------------- #
#  NOTIFICATIONS & CONTACT
# --------------------------------------------------------------------------- #
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    message = db.Column(db.Text, nullable=False)
    handled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteContent(db.Model):
    """Editable key/value content for hero & homepage sections."""
    __tablename__ = "site_content"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, default="")

    @staticmethod
    def get(key, default=""):
        row = SiteContent.query.filter_by(key=key).first()
        return row.value if row else default
