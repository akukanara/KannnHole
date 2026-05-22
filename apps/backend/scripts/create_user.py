#!/usr/bin/env python3
import argparse
import getpass
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app, db
from app.models import User


def parse_args():
    parser = argparse.ArgumentParser(description="Create a KTM user")
    parser.add_argument("--username", help="Unique username")
    parser.add_argument("--password", help="User password")
    parser.add_argument("--email", default="", help="Optional email")
    parser.add_argument("--role", choices=["admin", "user"], default="user", help="User role")
    return parser.parse_args()


def prompt_if_missing(value, label, secret=False, default=None):
    if value:
        return value
    suffix = f" [{default}]" if default else ""
    while True:
        if secret:
            entered = getpass.getpass(f"{label}{suffix}: ")
        else:
            entered = input(f"{label}{suffix}: ")
        entered = entered.strip()
        if not entered and default is not None:
            return default
        if entered:
            return entered
        print(f"error: {label.lower()} cannot be empty", file=sys.stderr)


def main():
    os.environ["KTM_DISABLE_FRPS_START"] = "true"
    args = parse_args()
    username = prompt_if_missing(args.username, "Username").strip()
    password = prompt_if_missing(args.password, "Password", secret=True)
    role = prompt_if_missing(args.role, "Role", default="user").strip().lower()
    if role not in {"admin", "user"}:
        print("error: role must be 'admin' or 'user'", file=sys.stderr)
        return 1
    email = args.email.strip() or None

    if not username:
        print("error: username cannot be empty", file=sys.stderr)
        return 1

    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.filter_by(username=username).first():
            print(f"error: username '{username}' already exists", file=sys.stderr)
            return 2

        if email and User.query.filter_by(email=email).first():
            print(f"error: email '{email}' already exists", file=sys.stderr)
            return 3

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print(f"created user: id={user.id} username={user.username} role={user.role}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
