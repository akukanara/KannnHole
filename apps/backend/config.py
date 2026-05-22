import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "thisiskannnhole_secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/kannnhole",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Monorepo Path Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    FRONTEND_DIST_DIR = os.getenv(
        "FRONTEND_DIST_DIR",
        os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "dist"))
    )
    INSTALLER_TEMPLATE_PATH = os.getenv(
        "INSTALLER_TEMPLATE_PATH",
        os.path.abspath(os.path.join(BASE_DIR, "..", "..", "packages", "agent", "installer_template.sh"))
    )
    KTMC_PY_PATH = os.getenv(
        "KTMC_PY_PATH",
        os.path.abspath(os.path.join(BASE_DIR, "..", "..", "packages", "agent", "ktmc.py"))
    )
    FRPC_PATH = os.getenv(
        "FRPC_PATH",
        os.path.abspath(os.path.join(BASE_DIR, "..", "..", "packages", "agent", "bin", "frp", "frpc"))
    )

    # FRP Config
    FRPS_BIND_ADDR = os.getenv("FRPS_BIND_ADDR", "0.0.0.0")
    FRPS_BIND_PORT = int(os.getenv("FRPS_BIND_PORT", "7000"))
    FRPS_SERVER_ADDR = os.getenv("FRPS_SERVER_ADDR", "127.0.0.1")
    FRPS_GLOBAL_TOKEN = os.getenv("FRPS_GLOBAL_TOKEN", "thisiskannnhole")

    # Profile upload settings
    USE_S3_UPLOAD = os.getenv("USE_S3_UPLOAD", "false").lower() == "true"
    PROFILE_UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), "data", "profile", "photos"
    )

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

