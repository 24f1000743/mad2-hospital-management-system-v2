from datetime import date
from datetime import datetime
import csv
import os

from celery import Celery

from config import Config
from celery.schedules import crontab

from flask_mail import Message
from extensions import mail
from flask import render_template
from models import Doctor, Appointment, Patient


# Celery instance
celery = Celery(
    "hms_tasks",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
)
celery.conf.timezone = Config.CELERY_TIMEZONE

# Beat schedule: daily reminders & monthly reports
celery.conf.beat_schedule = {
    "daily-appointment-reminders": {
        "task": "hms_tasks.send_daily_reminders",
        "schedule": crontab(hour=8,minute=0),  # every 24 hours
    },
    "monthly-doctor-report": {
        "task": "hms_tasks.send_monthly_doctor_reports",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # approx monthly (simplified)
    },
}


def _get_app():
    from app import create_app

    return create_app()


@celery.task(name="hms_tasks.send_daily_reminders")
def send_daily_reminders():
    """
    Demo implementation:
    Prints reminders to console for today's booked appointments.
    In real deployment you would integrate email / SMS / GChat webhook here.
    """
    app = _get_app()
    with app.app_context():
        from models import Appointment

        today = date.today()
        appointments = Appointment.query.filter_by(
            date=today, status="Booked"
        ).all()
        for appt in appointments:
            msg = (
                f"[Reminder] Patient {appt.patient.full_name} has "
                f"appointment with Dr. {appt.doctor.full_name} "
                f"today at {appt.time.strftime('%H:%M')}"
            )
            email = appt.patient.email
            message = Message(subject="Hospital Appointment Reminder",recipients=[email])
            message.body = msg
            mail.send(message)
    return "OK"


@celery.task(name="hms_tasks.send_monthly_doctor_reports")
def send_monthly_doctor_reports():
    """
    Demo implementation:
    For each doctor, prints simple HTML-ish summary to console.
    """
    app = _get_app()
    with app.app_context():
        from models import Doctor, Appointment, Treatment

        today = date.today()
        month_start = today.replace(day=1)

        doctors = Doctor.query.all()
        for doc in doctors:
            appts = (
                Appointment.query.filter(
                    Appointment.doctor_id == doc.id,
                    Appointment.date >= month_start,
                    Appointment.date <= today,
                )
                .order_by(Appointment.date, Appointment.time)
                .all()
            )

            print(f"\n=== Monthly report for Dr. {doc.full_name} ===")
            for a in appts:
                t = a.treatment
                print(
                    f"{a.date.isoformat()} {a.time.strftime('%H:%M')} - "
                    f"Patient: {a.patient.full_name} - "
                    f"Diagnosis: {t.diagnosis if t else 'N/A'}"
                )
            print("=== End of report ===\n")
    return "OK"


@celery.task(name="hms_tasks.export_patient_treatments_csv")
def export_patient_treatments_csv(patient_id: int):
    """
    Async job to export treatments for a given patient as CSV.
    Returns path to CSV file (for demo).
    """
    app = _get_app()
    with app.app_context():
        from models import Patient, Appointment, Treatment

        patient = Patient.query.get(patient_id)
        if not patient:
            return None

        appts = (
            Appointment.query.filter_by(patient_id=patient_id)
            .order_by(Appointment.date, Appointment.time)
            .all()
        )

        export_dir = os.path.join(os.path.dirname(__file__), "exports")
        os.makedirs(export_dir, exist_ok=True)
        filename = f"patient_{patient_id}_treatments.csv"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "user_id",
                    "username",
                    "patient_name",
                    "consulting_doctor",
                    "appointment_date",
                    "appointment_time",
                    "diagnosis",
                    "prescription",
                    "next_visit_suggested",
                ]
            )
            for a in appts:
                t = a.treatment
                writer.writerow(
                    [
                        patient.user_id,
                        patient.user.username,
                        patient.full_name,
                        a.doctor.full_name,
                        a.date.isoformat(),
                        a.time.strftime("%H:%M"),
                        t.diagnosis if t else "",
                        t.prescription if t else "",
                        t.next_visit_date.isoformat()
                        if t and t.next_visit_date
                        else "",
                    ]
                )

        print(f"[CSV Export] Created {filepath}")
        return filepath
    
@celery.task(name="hms_tasks.send_monthly_doctor_reports")
def send_monthly_doctor_reports():

    app = _get_app()
    app.app_context()

    today = datetime.today()

    doctors = Doctor.query.all()

    for doctor in doctors:

        appointments = Appointment.query.filter_by(
            doctor_id=doctor.id
        ).all()

        html_report = render_template(
            "monthly_doctor_report.html",
            doctor=doctor,
            appointments=appointments
        )

        message = Message(
            subject="Monthly Doctor Activity Report",
            recipients=[doctor.email]
        )

        message.html = html_report

        mail.send(message)

    return "Monthly reports sent"