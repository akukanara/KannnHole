import os
from flask import Blueprint, request, redirect, url_for, send_file, abort, current_app
from flask_login import login_user, logout_user
from .models import User
from . import db, login_manager
from sqlalchemy import or_
auth = Blueprint("auth", __name__)

def _frontend_dist_dir():
    return current_app.config.get("FRONTEND_DIST_DIR")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["username"]
        password = request.form["password"]
        
        # Cari berdasarkan username atau email
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))

        return redirect(url_for("auth.login", error="invalid"))

    login_page = os.path.join(_frontend_dist_dir(), "login", "index.html")
    if not os.path.exists(login_page):
        abort(503, description="Frontend build not found. Run: cd frontend && npm run build")
    return send_file(login_page)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
