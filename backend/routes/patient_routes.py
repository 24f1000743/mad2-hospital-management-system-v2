# backend/routes/patient_routes.py

from datetime import datetime as dt, date as date_cls
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import json

from extensions import db, cache
from models import (
    User,
    Patient,
    Doctor,
    Department,
    Appointment,
    Treatment,
    DoctorAvailability,
    ROLE_PATIENT,
)

patient_bp = Blueprint("patient", __name__)


# ======================== HELPERS ========================

def get_current_patient():
    identity = json.loads(get_jwt_identity())
    patient = Patient.query.filter_by(user_id=identity['id']).first()
    return patient


def serialize_doctor(doctor: Doctor):
    dept_name = doctor.department.name if getattr(doctor, "department", None) else None
    return {
        "id": doctor.id,
        "full_name": doctor.full_name,
        "specialization": doctor.specialization,
        "department": dept_name,
    }


def serialize_department(dept: Department):
    return {
        "id": dept.id,
        "name": dept.name,
        "description": dept.description,
    }


# ======================== DASHBOARD ========================

@patient_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def patient_dashboard():
    """
    Returns summary data for the patient dashboard:
      - patient basic info
      - list of departments
      - list of doctors
      - upcoming appointments
      - past appointments / treatments
    """
    patient = get_current_patient()
    if not patient:
        return jsonify({"message": "No patient found in the system"}), 404

    # Patient info
    patient_info = {
        "id": patient.id,
        "full_name": getattr(patient, "full_name", None),
        "phone": getattr(patient, "phone", None),
    }

    # Departments
    departments = [serialize_department(d) for d in Department.query.all()]

    # Doctors
    doctors = [serialize_doctor(d) for d in Doctor.query.all()]

    # Appointments for this patient
    today = date_cls.today()
    appts_q = Appointment.query.filter_by(patient_id=patient.id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    )

    upcoming = []
    history = []

    for a in appts_q.all():
        base = {
            "id": a.id,
            "doctor": a.doctor.full_name if a.doctor else "",
            "doctor_id": a.doctor_id,
            "date": a.date.isoformat() if a.date else None,
            "time": a.time.strftime("%H:%M") if a.time else None,
            "status": a.status,
        }

        if a.date and a.date >= today and a.status in ("Booked", "Rescheduled"):
            upcoming.append(base)
        else:
            # attach treatment info if exists
            if a.treatment:
                base.update(
                    {
                        "diagnosis": a.treatment.diagnosis,
                        "prescription": a.treatment.prescription,
                        "notes": a.treatment.notes,
                    }
                )
            history.append(base)

    return jsonify(
        {
            "patient": patient_info,
            "departments": departments,
            "doctors": doctors,
            "upcoming_appointments": upcoming,
            "history": history,
        }
    ), 200


# ======================== DOCTOR SEARCH ========================

@patient_bp.route("/doctors", methods=["GET"])
@jwt_required()
@cache.cached(timeout=120)
def patient_doctors_list():
    """
    Returns list of doctors, optionally filtered by specialization or name.
    Query params:
      - search: text to search in doctor name or specialization
    """
    search = (request.args.get("search") or "").strip().lower()

    q = Doctor.query
    if search:
        q = q.filter(
            db.or_(
                Doctor.full_name.ilike(f"%{search}%"),
                Doctor.specialization.ilike(f"%{search}%"),
            )
        )

    doctors = [serialize_doctor(d) for d in q.all()]
    return jsonify(doctors), 200


# ======================== DOCTOR AVAILABILITY (FOR PATIENT) ========================

@patient_bp.route("/doctors/<int:doctor_id>/availability", methods=["GET"])
@jwt_required()
def patient_doctor_availability(doctor_id):
    """
    Returns availability slots for a given doctor, visible to the patient.
    Used when booking appointments from the patient dashboard.
    """
    today = date_cls.today()
    slots = (
        DoctorAvailability.query
        .filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= today,
        )
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


# ======================== BOOK APPOINTMENT ========================

@patient_bp.route("/appointments", methods=["POST"])
@jwt_required()
def book_appointment():
    patient = get_current_patient()
    if not patient:
        return jsonify({"message": "No patient found in the system"}), 404

    data = request.get_json(silent=True) or {}
    doctor_id = data.get("doctor_id")
    date_str = data.get("date")
    time_str = data.get("time")

    if not doctor_id or not date_str or not time_str:
        return jsonify({"message": "doctor_id, date and time are required"}), 400

    try:
        appt_date = dt.strptime(date_str, "%Y-%m-%d").date()
        appt_time = dt.strptime(time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"message": "Invalid date or time format"}), 400

    # Prevent double booking for same doctor at same date/time
    conflict = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=appt_date,
        time=appt_time,
    ).first()
    if conflict:
        return jsonify({"message": "Slot already booked for this doctor"}), 409

    appt = Appointment(
        doctor_id=doctor_id,
        patient_id=patient.id,
        date=appt_date,
        time=appt_time,
        status="Booked",
    )
    db.session.add(appt)
    db.session.commit()

    return jsonify({"message": "Appointment booked", "id": appt.id}), 201


# ======================== PATIENT APPOINTMENTS LIST ========================

@patient_bp.route("/appointments", methods=["GET"])
@jwt_required()
def patient_appointments():
    patient = get_current_patient()
    if not patient:
        return jsonify({"message": "No patient found in the system"}), 404

    appts = (
        Appointment.query.filter_by(patient_id=patient.id)
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    result = []
    for a in appts:
        result.append(
            {
                "id": a.id,
                "doctor": a.doctor.full_name if a.doctor else "",
                "doctor_id": a.doctor_id,
                "date": a.date.isoformat() if a.date else None,
                "time": a.time.strftime("%H:%M") if a.time else None,
                "status": a.status,
            }
        )

    return jsonify(result), 200


# ======================== CANCEL APPOINTMENT ========================

@patient_bp.route("/appointments/<int:appointment_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_appointment(appointment_id):
    patient = get_current_patient()
    if not patient:
        return jsonify({"message": "No patient found in the system"}), 404

    appt = Appointment.query.filter_by(
        id=appointment_id, patient_id=patient.id
    ).first()
    if not appt:
        return jsonify({"message": "Appointment not found"}), 404

    appt.status = "Cancelled"
    db.session.commit()
    return jsonify({"message": "Appointment cancelled"}), 200


# ======================== TREATMENT HISTORY ========================

@patient_bp.route("/treatments", methods=["GET"])
@jwt_required()
def patient_treatments():
    patient = get_current_patient()
    if not patient:
        return jsonify({"message": "No patient found in the system"}), 404

    appts = (
        Appointment.query.filter_by(patient_id=patient.id)
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    result = []
    for a in appts:
        if not a.treatment:
            continue
        result.append(
            {
                "appointment_id": a.id,
                "doctor": a.doctor.full_name if a.doctor else "",
                "date": a.date.isoformat() if a.date else None,
                "time": a.time.strftime("%H:%M") if a.time else None,
                "diagnosis": a.treatment.diagnosis,
                "prescription": a.treatment.prescription,
                "notes": a.treatment.notes,
            }
        )

    return jsonify(result), 200