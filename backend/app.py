# backend/app.py
from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db, migrate, bcrypt, jwt, cache, make_celery
from models import User, ROLE_ADMIN
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp
from routes.patient_routes import patient_bp
from extensions import mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)

    # blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(doctor_bp, url_prefix="/api/doctor")
    app.register_blueprint(patient_bp, url_prefix="/api/patient")

    # DB + default admin
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role=ROLE_ADMIN).first()
        if not admin:
            admin = User(username="admin", role=ROLE_ADMIN)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin / admin123")


    app.celery_app = make_celery(app)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)