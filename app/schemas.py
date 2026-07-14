"""
Pydantic schemas — define the shape of data going in/out of the API.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ---------- Auth ----------
class DoctorLoginRequest(BaseModel):
    login_id: str
    password: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminForgotPasswordQuestionRequest(BaseModel):
    email: EmailStr


class AdminForgotPasswordQuestionResponse(BaseModel):
    question: str


class AdminResetPasswordRequest(BaseModel):
    email: EmailStr
    answer: str
    new_password: str


class AdminChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class StatsOut(BaseModel):
    doctors: int
    feedbacks: int
    predictions: int
    patients: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# ---------- Registration ----------
class RegistrationRequestOut(BaseModel):
    id: int
    full_name: str
    mobile_number: str
    gender: str
    email: EmailStr
    degree: str
    degree_image_path: str
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApproveRequest(BaseModel):
    login_id: str
    password: str


class RejectRequest(BaseModel):
    reason: str


# ---------- Doctor ----------
class DoctorOut(BaseModel):
    id: int
    full_name: str
    mobile_number: str
    gender: str
    email: EmailStr
    degree: str
    degree_image_path: str
    login_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    degree: Optional[str] = None
    login_id: Optional[str] = None
    new_password: Optional[str] = None


# ---------- Patient / Prediction ----------
class PredictionOut(BaseModel):
    id: int
    cell_image_path: str
    cancer_type: str
    confidence: float
    symptoms: str
    medicines: str
    created_at: datetime

    class Config:
        from_attributes = True


class PatientHistoryOut(BaseModel):
    patient_id: str
    patient_name: str
    created_at: datetime
    predictions: list[PredictionOut] = []

    class Config:
        from_attributes = True


# ---------- Feedback ----------
class FeedbackCreate(BaseModel):
    ratings_json: str   # JSON string of {"q1": "5", "q2": "4", ...}
    comments: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    doctor_id: int
    ratings_json: str
    comments: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True