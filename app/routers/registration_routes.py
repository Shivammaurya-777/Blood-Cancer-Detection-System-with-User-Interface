import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_doctor_db
from app import models, schemas, auth
from app.utils import email_service, sms_service

router = APIRouter(tags=["Registration"])

UPLOAD_DIR = "app/static/uploads/degree_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _save_upload(file: UploadFile, folder: str) -> str:
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(folder, unique_name)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return dest_path


# ---------- Doctor: submit registration ----------
@router.post("/register", response_model=schemas.RegistrationRequestOut)
def register_doctor(
    full_name: str = Form(...),
    mobile_number: str = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    degree: str = Form(...),
    degree_image: UploadFile = File(...),
    db: Session = Depends(get_doctor_db),
):
    image_path = _save_upload(degree_image, UPLOAD_DIR)

    request = models.RegistrationRequest(
        full_name=full_name,
        mobile_number=mobile_number,
        gender=gender,
        email=email,
        degree=degree,
        degree_image_path=image_path,
        status="pending",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


# ---------- Admin: list pending requests ----------
@router.get("/admin/requests", response_model=list[schemas.RegistrationRequestOut])
def list_requests(
    status_filter: str = "pending",
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    query = db.query(models.RegistrationRequest)
    if status_filter != "all":
        query = query.filter(models.RegistrationRequest.status == status_filter)
    return query.order_by(models.RegistrationRequest.created_at.desc()).all()


# ---------- Admin: view one request ----------
@router.get("/admin/requests/{request_id}", response_model=schemas.RegistrationRequestOut)
def get_request(
    request_id: int,
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    request = db.query(models.RegistrationRequest).filter(models.RegistrationRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


# ---------- Admin: approve request ----------
@router.post("/admin/requests/{request_id}/approve", response_model=schemas.DoctorOut)
def approve_request(
    request_id: int,
    payload: schemas.ApproveRequest,
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    request = db.query(models.RegistrationRequest).filter(models.RegistrationRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {request.status}")

    existing = db.query(models.Doctor).filter(models.Doctor.login_id == payload.login_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="That login ID is already taken")

    doctor = models.Doctor(
        full_name=request.full_name,
        mobile_number=request.mobile_number,
        gender=request.gender,
        email=request.email,
        degree=request.degree,
        degree_image_path=request.degree_image_path,
        login_id=payload.login_id,
        password_hash=auth.hash_password(payload.password),
        request_id=request.id,
    )
    request.status = "approved"

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    email_service.send_approval_email(doctor.email, doctor.full_name, payload.login_id, payload.password)
    sms_service.send_approval_sms(doctor.mobile_number, payload.login_id, payload.password)

    return doctor


# ---------- Admin: reject request ----------
@router.post("/admin/requests/{request_id}/reject", response_model=schemas.RegistrationRequestOut)
def reject_request(
    request_id: int,
    payload: schemas.RejectRequest,
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    request = db.query(models.RegistrationRequest).filter(models.RegistrationRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {request.status}")

    request.status = "rejected"
    request.rejection_reason = payload.reason
    db.commit()
    db.refresh(request)

    email_service.send_rejection_email(request.email, request.full_name, payload.reason)
    sms_service.send_rejection_sms(request.mobile_number, payload.reason)

    return request