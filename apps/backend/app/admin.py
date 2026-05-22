import os
from flask import Blueprint, request, redirect, url_for, abort, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from .models import db, Client, User

admin = Blueprint("admin", __name__)


def _frontend_dist_dir():
    return current_app.config.get("FRONTEND_DIST_DIR")


@admin.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)
    page = os.path.join(_frontend_dist_dir(), "admin", "index.html")
    if not os.path.exists(page):
        abort(503, description="Frontend build not found. Run: cd frontend && npm run build")
    return send_file(page)


@admin.route("/api/admin")
@login_required
def admin_data():
    if current_user.role != "admin":
        abort(403)
    users = User.query.all()
    clients = Client.query.all()
    return jsonify({
        "users": [
            {"id": u.id, "username": u.username, "email": u.email, "role": u.role}
            for u in users
        ],
        "clients": [
            {"id": c.id, "client_id": c.client_id, "user_id": c.user_id}
            for c in clients
        ]
    })


@admin.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        abort(403)

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("❌ Cannot delete yourself", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    # Hapus semua clients yang dimiliki user
    Client.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()
    flash("✅ User and related clients deleted", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/admin/clients/<client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    if current_user.role != "admin":
        abort(403)
    client = Client.query.filter_by(client_id=client_id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash("✅ Client deleted", "success")
    return redirect(url_for("admin.admin_dashboard"))

@admin.route("/admin/clients/<client_id>/tunnels/<int:index>/delete", methods=["POST"])
@login_required
def delete_tunnel(client_id, index):
    if current_user.role != "admin":
        abort(403)
    client = Client.query.filter_by(client_id=client_id).first_or_404()
    if index < 0 or index >= len(client.frpc_config):
        flash("❌ Invalid tunnel index", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    del client.frpc_config[index]
    db.session.commit()
    flash("✅ Tunnel deleted", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/admin/users/add", methods=["POST"])
@login_required
def add_user():
    if current_user.role != "admin":
        abort(403)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    email = request.form.get("email", "").strip()

    if not username or not password:
        flash("❗Username and password are required", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    if User.query.filter_by(username=username).first():
        flash("❗Username already exists", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    if email and User.query.filter_by(email=email).first():
        flash("❗Email already exists", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    user = User(username=username, email=email or None)
    user.set_password(password)
    user.role = "user"
    db.session.add(user)
    db.session.commit()

    flash("✅ User added successfully", "success")
    return redirect(url_for("admin.admin_dashboard"))

@admin.route("/admin/users/<int:user_id>/edit", methods=["POST"])
@login_required
def edit_user(user_id):
    if current_user.role != "admin":
        abort(403)

    user = User.query.get_or_404(user_id)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    email = request.form.get("email", "").strip()
    role = request.form.get("role", "").strip()

    # Validasi username
    if not username:
        flash("❗Username is required", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    existing = User.query.filter_by(username=username).first()
    if existing and existing.id != user.id:
        flash("❗Username already taken", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    # Validasi email
    if email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user.id:
            flash("❗Email already used", "danger")
            return redirect(url_for("admin.admin_dashboard"))

    # Apply changes
    user.username = username
    user.email = email or None
    if password:
        user.set_password(password)
    if role in ["user", "admin"]:
        user.role = role

    db.session.commit()
    flash("✅ User updated successfully", "success")
    return redirect(url_for("admin.admin_dashboard"))
