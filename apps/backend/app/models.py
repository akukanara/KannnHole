from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_token = db.Column(db.String(64), nullable=True)
    profile_url = db.Column(db.String(256), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_token(self):
        self.email_token = uuid.uuid4().hex


class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(64), unique=True, nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    frpc_config = db.Column(db.JSON, nullable=False, default=dict)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('clients', lazy=True))
