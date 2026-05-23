"""Application factory for MERVE Café."""
import os

from flask import Flask, render_template
from dotenv import load_dotenv

from .config import config_map
from .extensions import db, login_manager

load_dotenv()


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # ensure instance + upload folders exist
    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)
    for sub in ("avatars", "menu"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], sub), exist_ok=True)

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # register blueprints
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.menu import menu_bp
    from .blueprints.booking import booking_bp
    from .blueprints.orders import orders_bp
    from .blueprints.account import account_bp
    from .blueprints.admin import admin_bp
    from .blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # context processor — expose brand + cart count everywhere
    from .models import SiteContent

    @app.context_processor
    def inject_globals():
        from flask import session
        cart = session.get("cart", {})
        cart_count = sum(i.get("qty", 0) for i in cart.values()) if cart else 0
        return {
            "BRAND": "MERVE Café",
            "cart_count": cart_count,
            "site": SiteContent,
        }

    # error pages
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403,
                               msg="Доступ запрещён."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404,
                               msg="Страница не найдена."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500,
                               msg="Внутренняя ошибка сервера."), 500

    # CLI helper: flask init-db
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created.")

    return app
