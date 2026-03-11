# backend/routes/doctor_routes.py

from datetime import datetime as dt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import json

from extensions import db, cache
from models import (
    Doctor,
    Appointment,
    Treatment,
    DoctorAvailability, User
)

doctor_bp = Blueprint("doctor", __name__)


# ================== CURRENT DOCTOR ==================

def get_current_doctor():
    identity = json.loads(get_jwt_identity())
    user = User.query.get(identity["id"])
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    #doctor = Doctor.query.first()
    return doctor


# ================== DOCTOR DASHBOARD INFO ==================

@doctor_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60)
def dashboard():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"message": "No doctor found in the system"}), 404

    return jsonify(
        {
            "doctor": {
                "id": doctor.id,
                "full_name": doctor.full_name,
                "specialization": doctor.specialization,
            }
        }
    ), 200


# ================== APPOINTMENTS LIST ==================

@doctor_bp.route("/appointments", methods=["GET"])
@jwt_required()
def doctor_appointments():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"message": "No doctor found in the system"}), 404

    appts = (
        Appointment.query.filter_by(doctor_id=doctor.id)
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    result = []
    for a in appts:
        result.append(
            {
                "id": a.id,
                "patient": a.patient.full_name if a.patient else "",
                "date": a.date.isoformat(),
                "time": a.time.strftime("%H:%M"),
                "status": a.status,
            }
        )

    return jsonify(result), 200


# ================== UPDATE APPOINTMENT STATUS ==================

@doctor_bp.route("/appointments/<int:appointment_id>/status", methods=["PATCH"])
@jwt_required()
def update_status(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"message": "No doctor found in the system"}), 404

    appt = Appointment.query.filter_by(
        id=appointment_id, doctor_id=doctor.id
    ).first()
    if not appt:
        return jsonify({"message": "Appointment not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("Booked", "Completed", "Cancelled"):
        return jsonify({"message": "Invalid status"}), 400

    appt.status = status
    db.session.commit()
    return jsonify({"message": "Status updated"}), 200


# ================== SAVE / UPDATE TREATMENT ==================

@doctor_bp.route("/appointments/<int:appointment_id>/treatment", methods=["POST"])
@jwt_required()
def save_treatment(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"message": "No doctor found in the system"}), 404

    appt = Appointment.query.filter_by(
        id=appointment_id, doctor_id=doctor.id
    ).first()
    if not appt:
        return jsonify({"message": "Appointment not found"}), 404

    data = request.get_json(silent=True) or {}

    treatment = appt.treatment or Treatment(appointment_id=appt.id)
    treatment.diagnosis = data.get("diagnosis")
    treatment.prescription = data.get("prescription")
    treatment.notes = data.get("notes")

    db.session.add(treatment)
    db.session.commit()

    return jsonify({"message": "Treatment saved"}), 200


# ================== AVAILABILITY: GET ==================

@doctor_bp.route("/availability", methods=["GET"])
@jwt_required()
@cache.cached(timeout=120)
def get_availability():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"message": "No doctor found in the system"}), 404

    slots = (
        DoctorAvailability.query.filter_by(doctor_id=doctor.id)
        .order_by(DoctorAvailability.date, DoctorAvailability.start_time)
        .all()
    )

    result = []
    for s in slots:
        result.append(
            {
                "id": s.id,
                "date": s.date.isoformat(),
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
            }
        )

    return jsonify(result), 200


# ================== AVAILABILITY: SAVE ==================

@doctor_bp.route("/availability", methods=["POST"])
@jwt_required()
def save_availability():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"message": "No doctor found in the system"}), 404

    data = request.get_json(silent=True) or {}
    print("RAW AVAILABILITY DATA:", data)

    # Accept either:
    # { "slots": [ {...}, {...} ] } OR [ {...}, {...} ]
    if isinstance(data, dict):
        slots = data.get("slots") or []
    elif isinstance(data, list):
        slots = data
    else:
        slots = []

    # Remove all old slots for this doctor
    DoctorAvailability.query.filter_by(doctor_id=doctor.id).delete()

    for item in slots:
        try:
            date_str = item.get("date")
            start_str = item.get("start_time") or item.get("start")
            end_str = item.get("end_time") or item.get("end")

            if not date_str or not start_str or not end_str:
                continue

            slot_date = dt.strptime(date_str, "%Y-%m-%d").date()
            start_time = dt.strptime(start_str, "%H:%M").time()
            end_time = dt.strptime(end_str, "%H:%M").time()

            slot = DoctorAvailability(
                doctor_id=doctor.id,
                date=slot_date,
                start_time=start_time,
                end_time=end_time,
            )
            db.session.add(slot)
        except Exception as e:
            print("BAD SLOT:", item, "ERROR:", e)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB ERROR saving availability:", e)
        return jsonify({"message": "Database error while saving availability"}), 500

    return jsonify({"message": "Availability saved"}), 200