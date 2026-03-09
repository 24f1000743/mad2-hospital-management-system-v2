# backend/routes/_init_.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


def get_current_user():
    """
    Returns the current logged-in User model based on JWT.
    Any route can do:
        user = get_current_user()
    """
    ident = get_jwt_identity()
    if not ident:
        return None

    # Lazy import to avoid circular imports
    from models import User

    return User.query.get(ident.get("id"))


def role_required(required_role):
    """
    Usage:
        @admin_bp.route("/something")
        @role_required(ROLE_ADMIN)
        def admin_only():
            ...
    Internally uses jwt_required + get_current_user.
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()   # token must be present in Authorization header
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user or user.role != required_role:
                return jsonify({"message": "Forbidden"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator