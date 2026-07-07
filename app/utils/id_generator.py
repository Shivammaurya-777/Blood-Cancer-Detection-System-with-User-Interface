"""
Generates human-readable unique IDs:
- Patient ID:  PT-2026-0001
- Doctor login ID suggestion: DR-2026-0001 (admin can override when approving)
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app import models


def generate_patient_id(db: Session) -> str:
    year = datetime.now().year
    prefix = f"PT-{year}-"

    last = (
        db.query(models.Patient)
        .filter(models.Patient.patient_id.like(f"{prefix}%"))
        .order_by(models.Patient.patient_id.desc())
        .first()
    )

    if last:
        last_number = int(last.patient_id.split("-")[-1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{prefix}{next_number:04d}"


def suggest_doctor_login_id(db: Session) -> str:
    year = datetime.now().year
    prefix = f"DR-{year}-"

    last = (
        db.query(models.Doctor)
        .filter(models.Doctor.login_id.like(f"{prefix}%"))
        .order_by(models.Doctor.login_id.desc())
        .first()
    )

    if last:
        try:
            last_number = int(last.login_id.split("-")[-1])
            next_number = last_number + 1
        except ValueError:
            next_number = 1
    else:
        next_number = 1

    return f"{prefix}{next_number:04d}"
