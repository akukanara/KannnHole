from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os
import threading
import time
from .frps import start_frps, generate_frps_ini

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .routes import main
    from .auth import auth
    from .admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    def frps_background():
        time.sleep(1)
        generate_frps_ini(app.config)
        start_frps()

    disable_frps = os.getenv("KTM_DISABLE_FRPS_START", "false").lower() == "true"
    if not disable_frps:
        threading.Thread(target=frps_background, daemon=True).start()

    return app
