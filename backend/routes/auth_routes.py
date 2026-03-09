from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db
from models import User, Patient, ROLE_PATIENT

auth_bp = Blueprint("auth", __name__)

def _identity(user):
    return {"id": user.id, "role": user.role}

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name") or data.get("fullName") or username
    phone = data.get("phone")

    if not username or not password:
        return jsonify({"message": "username & password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username exists"}), 400

    user = User(username=username, role=ROLE_PATIENT)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    patient = Patient(user_id=user.id, full_name=full_name, phone=phone)
    db.session.add(patient)
    db.session.commit()

    token = create_access_token(identity=_identity(user))
    return jsonify({"token": token, "role": "patient"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401
    if not user.is_active or user.is_blacklisted:
        return jsonify({"message": "Blocked"}), 403

    token = create_access_token(identity=_identity(user))
    return jsonify({"token": token, "role": user.role}), 200