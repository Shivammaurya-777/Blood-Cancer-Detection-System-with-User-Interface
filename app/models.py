"""
ORM models — one class per database table.

These are now split across four separate SQLite database files (see
app/database.py for why). Relationships that would span two different
.db files can't be enforced or traversed by SQLAlchemy, so:

  - Doctor <-> RegistrationRequest: kept as a real relationship() +
    ForeignKey, because both live together in doctors.db.
  - Patient <-> Prediction: kept as a real relationship() + ForeignKey,
    because both live together in patients.db.
  - Patient.doctor_id and Feedback.doctor_id: kept as plain integer
    columns (no ForeignKey, no relationship()) since "doctors" lives in
    a different physical database file (doctors.db). The id is still
    stored for reference/lookup in application code.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ============================================================
# doctors.db — Doctor accounts + registration requests
# ============================================================

class RegistrationRequest(Base):
    __tablename__ = "registration_requests"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    email = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    degree_image_path = Column(String, nullable=False)

    # pending / approved / rejected
    status = Column(String, default="pending", nullable=False)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("Doctor", back_populates="request", uselist=False)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    email = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    degree_image_path = Column(String, nullable=False)

    login_id = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Same-file relationship (both tables live in doctors.db) - kept real.
    request_id = Column(Integer, ForeignKey("registration_requests.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("RegistrationRequest", back_populates="doctor")

    # NOTE: no relationship() to Patient/Feedback here anymore - those
    # tables now live in separate database files (patients.db, feedback.db)
    # and can't be traversed via SQLAlchemy relationships across files.


# ============================================================
# admins.db — Admin accounts
# ============================================================

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    security_question = Column(String, nullable=True)
    security_answer_hash = Column(String, nullable=True)


# ============================================================
# patients.db — Patients + their predictions
# ============================================================

class Patient(Base):
    __tablename__ = "patients"

    # e.g. "PT-2026-0001" — generated in utils/id_generator.py
    patient_id = Column(String, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)

    # Plain reference to a doctor's id - doctors.db is a separate file,
    # so this is NOT an enforced foreign key, just a stored reference.
    doctor_id = Column(Integer, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Same-file relationship (both tables live in patients.db) - kept real.
    predictions = relationship("Prediction", back_populates="patient")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)

    cell_image_path = Column(String, nullable=False)
    cancer_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    symptoms = Column(Text, nullable=False)
    medicines = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="predictions")


# ============================================================
# feedback.db — Doctor feedback submissions
# ============================================================

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    # Plain reference to a doctor's id - doctors.db is a separate file,
    # so this is NOT an enforced foreign key, just a stored reference.
    doctor_id = Column(Integer, nullable=False, index=True)

    # stores fixed-question answers as JSON text, e.g. {"q1": "5", "q2": "4"}
    ratings_json = Column(Text, nullable=False)
    comments = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())