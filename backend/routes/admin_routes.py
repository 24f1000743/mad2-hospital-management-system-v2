# backend/admin_routes.py  (ya backend/routes/admin_routes.py agar routes folder ke andar hai)
from flask import Blueprint, request, jsonify
from extensions import db
from models import User, Doctor, Patient, Appointment, Department, ROLE_DOCTOR
from extensions import cache

admin_bp = Blueprint("admin", __name__)


# ---------- SIMPLE DASHBOARD (NO AUTH FOR NOW) ----------

@admin_bp.route("/dashboard", methods=["GET"])
@cache.cached(timeout=60)
def admin_dashboard():
    """Return simple counts for admin dashboard."""
    return jsonify(
        {
            "stats": {
                "doctors": Doctor.query.count(),
                "patients": Patient.query.count(),
                "appointments": Appointment.query.count(),
            }
        }
    )


# ---------- PATIENTS LIST (SHOW ALL REGISTERED PATIENTS) ----------

@admin_bp.route("/patients", methods=["GET"])
def admin_patients():
    """
    Return all patients.
    This assumes Patient rows are created on register, which your app already does.
    """
    patients = Patient.query.join(User).filter(User.is_active == True).all()
    data = []
    for p in patients:
        # p.user might exist if relationship set in models, safety check for now
        username = p.user.username if getattr(p, "user", None) else None
        data.append(
            {
                "id": p.id,
                "full_name": p.full_name,
                "username": username,
                "phone": p.phone,
                "address": p.address,
            }
        )
    return jsonify(data)


# ---------- DOCTORS LIST (SHOW ALL DOCTORS) ----------

@admin_bp.route("/doctors", methods=["GET"])
def admin_doctors():
    doctors = Doctor.query.join(User).filter(User.is_active == True).all()
    data = []
    for d in doctors:
        username = d.user.username if getattr(d, "user", None) else None
        department_name = (
            d.department.name if getattr(d, "department", None) else None
        )
        data.append(
            {
                "id": d.id,
                "full_name": d.full_name,
                "username": username,
                "specialization": d.specialization,
                "department": department_name,
                "bio": d.bio,
            }
        )
    return jsonify(data)


# ---------- ADD DOCTOR (ROBUST, WITH CLEAR ERROR MESSAGE) ----------

@admin_bp.route("/doctors", methods=["POST"])
def add_doctor():
    """
    Body can be like:
    {
      "username": "doc1",
      "password": "123",
      "fullName": "Dr One",
      "full_name": "Dr One",   # either fullName or full_name, dono me se jo milega
      "specialization": "Cardiology",
      "department": "Cardiology",
      "bio": "some text"
    }
    """
    data = request.get_json(silent=True) or {}
    print("ADD_DOCTOR DATA:", data)

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    full_name = (
        (data.get("full_name") or data.get("fullName") or "").strip()
    )
    specialization = (data.get("specialization") or "").strip()
    department_name = (data.get("department") or "").strip()
    bio = (data.get("bio") or "").strip()

    # basic validation
    if not username or not password:
        return jsonify({"message": "username and password required"}), 400

    if not full_name:
        full_name = username
    if not specialization:
        specialization = "General"

    # username unique
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    try:
        # create login user
        user = User(username=username, role=ROLE_DOCTOR)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # so user.id is available

        # optional department
        department = None
        if department_name:
            department = Department.query.filter_by(name=department_name).first()
            if not department:
                department = Department(name=department_name, description="")
                db.session.add(department)
                db.session.flush()

        # create doctor profile
        doctor = Doctor(
            user_id=user.id,
            full_name=full_name,
            specialization=specialization,
            bio=bio,
            department_id=department.id if department else None,
        )
        db.session.add(doctor)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Doctor added successfully",
                    "doctor_id": doctor.id,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        print("ADD_DOCTOR ERROR:", repr(e))
        # yahan se exact error frontend pe dikh jayega
        return (
            jsonify(
                {
                    "message": f"Database error: {type(e)._name_}: {str(e)}"
                }
            ),
            500,
        )


# ---------- APPOINTMENTS LIST (SIMPLE) ----------

@admin_bp.route("/appointments", methods=["GET"])
def admin_appointments():
    appts = Appointment.query.all()
    data = []
    for a in appts:
        data.append(
            {
                "id": a.id,
                "doctor": a.doctor.full_name if getattr(a, "doctor", None) else None,
                "patient": a.patient.full_name
                if getattr(a, "patient", None)
                else None,
                "date": a.date.isoformat(),
                "time": a.time.strftime("%H:%M"),
                "status": a.status,
            }
        )
    return jsonify(data)

from flask import Blueprint, request, jsonify
from extensions import db
from models import User, Doctor, Patient

# assuming you already have:
# admin_bp = Blueprint("admin", _name_, url_prefix="/api/admin")

@admin_bp.route("/doctors/<int:doctor_id>/deactivate", methods=["PATCH"])
def deactivate_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404

    user = User.query.get(doctor.user_id) if hasattr(doctor, "user_id") else None

    if user:
        user.is_active = False

    db.session.commit()
    return jsonify({"message": "Doctor deactivated"}), 200


@admin_bp.route("/patients/<int:patient_id>/deactivate", methods=["PATCH"])
def deactivate_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    user = User.query.get(patient.user_id) if hasattr(patient, "user_id") else None

    if user:
        user.is_active = False

    db.session.commit()
    return jsonify({"message": "Patient deactivated"}), 200