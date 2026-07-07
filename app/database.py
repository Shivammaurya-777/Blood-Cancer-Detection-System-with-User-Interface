"""
Database connection setup (SQLite + SQLAlchemy).

Data is split across FOUR separate SQLite files instead of one shared
database, so each concern is easy to find/inspect on disk:

    admins.db     -> Admin accounts
    doctors.db    -> Doctor accounts + registration requests
                     (kept together: a Doctor is created directly from a
                     RegistrationRequest in the same transaction, and
                     Doctor.request_id is a real foreign key to it)
    patients.db   -> Patients + their predictions
                     (kept together: a Prediction always belongs to a
                     Patient via a real foreign key, queried together)
    feedback.db   -> Doctor feedback submissions

Note: SQLite cannot enforce foreign keys *across* separate database files.
Columns like Patient.doctor_id and Feedback.doctor_id still store the
doctor's id (so you can cross-reference by hand or join in application
code), but they are plain integer columns rather than enforced foreign
keys, since the "doctors" table lives in a different .db file.

All .db files are auto-created the first time init_db.py runs.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# A single declarative Base is fine to share across all four databases -
# it just tracks table/column metadata. What matters is which *engine*
# each table gets created on (see init_db.py) and which *session* each
# router uses to query/write.
Base = declarative_base()


def _make_engine(db_filename: str):
    return create_engine(
        f"sqlite:///./{db_filename}",
        connect_args={"check_same_thread": False},
    )


admin_engine = _make_engine("admins.db")
doctor_engine = _make_engine("doctors.db")
patient_engine = _make_engine("patients.db")
feedback_engine = _make_engine("feedback.db")

AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)
DoctorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=doctor_engine)
PatientSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=patient_engine)
FeedbackSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=feedback_engine)


def get_admin_db():
    """FastAPI dependency: a session bound to admins.db"""
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_doctor_db():
    """FastAPI dependency: a session bound to doctors.db"""
    db = DoctorSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_patient_db():
    """FastAPI dependency: a session bound to patients.db"""
    db = PatientSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_feedback_db():
    """FastAPI dependency: a session bound to feedback.db"""
    db = FeedbackSessionLocal()
    try:
        yield db
    finally:
        db.close()