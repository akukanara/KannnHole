import os
import sys

# Detect if the application is running in a PyInstaller frozen state
IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN:
    # Directory where the executable binary is located (for writeable/runtime files)
    EXE_DIR = os.path.dirname(sys.executable)
    # Temporary directory where PyInstaller unpacks internal files/assets
    BUNDLE_DIR = sys._MEIPASS
else:
    EXE_DIR = os.path.abspath(os.path.dirname(__file__))
    BUNDLE_DIR = EXE_DIR


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "thisiskannnhole_secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/kannnhole",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Monorepo Path Configuration (using frozen bundle assets if compiled)
    BASE_DIR = BUNDLE_DIR

    FRONTEND_DIST_DIR = os.getenv(
        "FRONTEND_DIST_DIR",
        os.path.join(BUNDLE_DIR, "frontend") if IS_FROZEN else os.path.abspath(os.path.join(BUNDLE_DIR, "..", "frontend", "dist"))
    )
    INSTALLER_TEMPLATE_PATH = os.getenv(
        "INSTALLER_TEMPLATE_PATH",
        os.path.join(BUNDLE_DIR, "agent", "installer_template.sh") if IS_FROZEN else os.path.abspath(os.path.join(BUNDLE_DIR, "..", "..", "packages", "agent", "installer_template.sh"))
    )
    KTMC_BIN_PATH = os.getenv(
        "KTMC_BIN_PATH",
        os.path.join(BUNDLE_DIR, "agent", "ktmc") if IS_FROZEN else os.path.abspath(os.path.join(BUNDLE_DIR, "..", "..", "packages", "agent", "ktmc"))
    )
    FRPC_PATH = os.getenv(
        "FRPC_PATH",
        os.path.join(BUNDLE_DIR, "agent", "bin", "frpc") if IS_FROZEN else os.path.abspath(os.path.join(BUNDLE_DIR, "..", "..", "packages", "agent", "bin", "frp", "frpc"))
    )

    # FRP Config
    FRPS_BIND_ADDR = os.getenv("FRPS_BIND_ADDR", "0.0.0.0")
    FRPS_BIND_PORT = int(os.getenv("FRPS_BIND_PORT", "7000"))
    FRPS_SERVER_ADDR = os.getenv("FRPS_SERVER_ADDR", "127.0.0.1")
    FRPS_GLOBAL_TOKEN = os.getenv("FRPS_GLOBAL_TOKEN", "thisiskannnhole")

    # Profile upload settings
    USE_S3_UPLOAD = os.getenv("USE_S3_UPLOAD", "false").lower() == "true"
    
    # Store uploads in EXE_DIR (writeable directory)
    PROFILE_UPLOAD_FOLDER = os.path.join(EXE_DIR, "data", "profile", "photos")

    # For S3 uploads
    S3_BUCKET = os.getenv("S3_BUCKET", "your-bucket-name")
    S3_REGION = os.getenv("S3_REGION", "ap-southeast-1")
    S3_KEY = os.getenv("S3_KEY", "your-aws-access-key")
    S3_SECRET = os.getenv("S3_SECRET", "your-aws-secret-key")

    # Enable email verification
    ENABLE_EMAIL_VERIFICATION = os.getenv("ENABLE_EMAIL_VERIFICATION", "true").lower() == "true"

    # Email SMTP config
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.zoho.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME", "KannnHole Tunnel"),
        os.getenv("MAIL_DEFAULT_SENDER_EMAIL", "noreply@kannnhole.xyz"),
    )
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
