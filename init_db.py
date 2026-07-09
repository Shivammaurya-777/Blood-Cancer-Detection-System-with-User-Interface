"""
Run this once to create all four database files with their tables,
and seed one default admin account so you can log in on day one.

Creates:
    admins.db     -> Admin
    doctors.db    -> Doctor, RegistrationRequest
    patients.db   -> Patient, Prediction
    feedback.db   -> Feedback

Usage:
    python init_db.py
"""

import bcrypt

from app.database import (
    Base,
    admin_engine, doctor_engine, patient_engine, feedback_engine,
    AdminSessionLocal,
)
from app import models


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Default admin credentials — CHANGE THESE after first login
DEFAULT_ADMIN_EMAIL = "admin@hospital.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"
DEFAULT_SECURITY_QUESTION = "What is your favorite color?"
DEFAULT_SECURITY_ANSWER = "blue"  # stored hashed, compared case-insensitively


def init():
    print("Creating tables across 4 separate database files...")

    Base.metadata.create_all(bind=admin_engine, tables=[models.Admin.__table__])
    print("  database/admins.db    -> admins")

    Base.metadata.create_all(bind=doctor_engine, tables=[
        models.RegistrationRequest.__table__,
        models.Doctor.__table__,
    ])
    print("  database/doctors.db   -> registration_requests, doctors")

    Base.metadata.create_all(bind=patient_engine, tables=[
        models.Patient.__table__,
        models.Prediction.__table__,
    ])
    print("  database/patients.db  -> patients, predictions")

    Base.metadata.create_all(bind=feedback_engine, tables=[models.Feedback.__table__])
    print("  database/feedback.db  -> feedback")

    db = AdminSessionLocal()
    try:
        existing = db.query(models.Admin).filter_by(email=DEFAULT_ADMIN_EMAIL).first()
        if not existing:
            admin = models.Admin(
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                security_question=DEFAULT_SECURITY_QUESTION,
                security_answer_hash=hash_password(DEFAULT_SECURITY_ANSWER.strip().lower()),
            )
            db.add(admin)
            db.commit()
            print(f"Default admin created -> email: {DEFAULT_ADMIN_EMAIL}  password: {DEFAULT_ADMIN_PASSWORD}")
            print(f"Security question: '{DEFAULT_SECURITY_QUESTION}'  answer: '{DEFAULT_SECURITY_ANSWER}'")
        else:
            if not existing.security_question:
                existing.security_question = DEFAULT_SECURITY_QUESTION
                existing.security_answer_hash = hash_password(DEFAULT_SECURITY_ANSWER.strip().lower())
                db.commit()
                print("Existing admin found — backfilled default security question.")
            else:
                print("Default admin already exists, skipping.")
    finally:
        db.close()

    print("Done. database/admins.db, database/doctors.db, database/patients.db, database/feedback.db are ready.")


if __name__ == "__main__":
    init()