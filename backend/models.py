from datetime import datetime, date, time

from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from config import Config

ROLE_ADMIN = "admin"
ROLE_DOCTOR = "doctor"
ROLE_PATIENT = "patient"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", back_populates="user", uselist=False)
    patient = db.relationship("Patient", back_populates="user", uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_default_admin():
        """
        Create a single admin user if it does not exist.
        Called from app.py after db.create_all().
        """
        admin = User.query.filter_by(role=ROLE_ADMIN).first()
        if not admin:
            admin = User(
                username=Config.ADMIN_USERNAME,
                email=Config.ADMIN_EMAIL,
                role=ROLE_ADMIN,
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print("Default admin created:")
            print(f"   username={Config.ADMIN_USERNAME}, password={Config.ADMIN_PASSWORD}")


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    doctors = db.relationship("Doctor", back_populates="department")


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))

    user = db.relationship("User", back_populates="doctor")
    department = db.relationship("Department", back_populates="doctors")
    appointments = db.relationship("Appointment", back_populates="doctor")
    availabilities = db.relationship("DoctorAvailability", back_populates="doctor",cascade="all, delete-orphan")


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    gender = db.Column(db.String(20))
    dob = db.Column(db.Date)

    user = db.relationship("User", back_populates="patient")
    appointments = db.relationship("Appointment", back_populates="patient")


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="Booked")  # Booked / Completed / Cancelled
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor = db.relationship("Doctor", back_populates="appointments")
    patient = db.relationship("Patient", back_populates="appointments")
    treatment = db.relationship("Treatment", back_populates="appointment", uselist=False)


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit_date = db.Column(db.Date)

    appointment = db.relationship("Appointment", back_populates="treatment")


class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availabilities"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    doctor = db.relationship("Doctor", back_populates="availabilities")

    @staticmethod
    def set_availability_for_doctor(doctor_id, slots):
        """
        slots: list of dicts {date: 'YYYY-MM-DD', start: 'HH:MM', end: 'HH:MM'}
        Replaces all availability rows for next 7 days.
        """
        DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete()
        for s in slots:
            d = date.fromisoformat(s["date"])
            start = time.fromisoformat(s["start"])
            end = time.fromisoformat(s["end"])
            db.session.add(
                DoctorAvailability(
                    doctor_id=doctor_id,
                    date=d,
                    start_time=start,
                    end_time=end,
                    is_available=True,
                )
            )
        db.session.commit()