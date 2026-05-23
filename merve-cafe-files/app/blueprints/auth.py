"""Authentication: register, login (remember me), logout."""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash)
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User, LoyaltyPoints
from ..utils import save_upload

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("account.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3:
            flash("Имя пользователя слишком короткое.", "error")
        elif len(password) < 5:
            flash("Пароль должен быть не короче 5 символов.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Такое имя пользователя уже занято.", "error")
        else:
            user = User(username=username, role="customer")
            user.set_password(password)
            avatar = save_upload(request.files.get("avatar"), "avatars")
            if avatar:
                user.avatar = avatar
            db.session.add(user)
            db.session.flush()
            db.session.add(LoyaltyPoints(user_id=user.id, points=0))
            db.session.commit()
            login_user(user)
            flash("Добро пожаловать в MERVE Café!", "success")
            return redirect(url_for("account.dashboard"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("account.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            nxt = request.args.get("next")
            if user.is_admin:
                return redirect(nxt or url_for("admin.dashboard"))
            return redirect(nxt or url_for("account.dashboard"))
        flash("Неверное имя пользователя или пароль.", "error")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))
