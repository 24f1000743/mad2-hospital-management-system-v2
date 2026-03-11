import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@hms.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    CELERY_TIMEZONE = 'Asia/Kolkata'
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "hms_v2_new.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask secret
    SECRET_KEY = os.environ.get("SECRET_KEY", "super_secret_hms_key")

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_secret_hms")

    # Uploads (optional)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Celery + Redis
    CELERY_BROKER_URL = os.environ.get(
        "CELERY_BROKER_URL", "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )
    
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "hospital.hms.app@gmail.com"
    MAIL_PASSWORD = "hms123"
    MAIL_DEFAULT_SENDER = "hospital.hms.app@gmail.com"

    # Debug
    DEBUG = True