from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from .database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True)
    email_verified = Column(Boolean, default=False)
    email_token = Column(String(64), nullable=True)
    profile_url = Column(String(256), nullable=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_token(self):
        self.email_token = uuid.uuid4().hex


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    client_id = Column(String(64), unique=True, nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    frpc_config = Column(JSON, nullable=False, default=dict)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref=backref('clients', lazy=True))
