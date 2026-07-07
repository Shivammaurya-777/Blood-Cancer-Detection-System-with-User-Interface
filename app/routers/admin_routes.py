from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_doctor_db
from app import models, schemas, auth

router = APIRouter(tags=["Admin - Doctor Management"])


@router.get("/admin/doctors", response_model=list[schemas.DoctorOut])
def list_doctors(
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    return db.query(models.Doctor).order_by(models.Doctor.created_at.desc()).all()


@router.get("/admin/doctors/{doctor_id}", response_model=schemas.DoctorOut)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/admin/doctors/{doctor_id}", response_model=schemas.DoctorOut)
def update_doctor(
    doctor_id: int,
    payload: schemas.DoctorUpdate,
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    update_data = payload.dict(exclude_unset=True)
    new_password = update_data.pop("new_password", None)
    new_login_id = update_data.get("login_id")

    if new_login_id:
        existing = (
            db.query(models.Doctor)
            .filter(models.Doctor.login_id == new_login_id, models.Doctor.id != doctor_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Login ID already in use by another doctor")

    for field, value in update_data.items():
        setattr(doctor, field, value)

    if new_password:
        doctor.password_hash = auth.hash_password(new_password)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/admin/doctors/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_doctor_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doctor)
    db.commit()
    return {"detail": f"Doctor '{doctor.full_name}' deleted successfully"}