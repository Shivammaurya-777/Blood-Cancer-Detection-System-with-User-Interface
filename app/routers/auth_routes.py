from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_doctor_db, get_admin_db
from app import models, schemas, auth

router = APIRouter(tags=["Auth"])


@router.post("/doctor/login", response_model=schemas.TokenResponse)
def doctor_login(payload: schemas.DoctorLoginRequest, db: Session = Depends(get_doctor_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.login_id == payload.login_id).first()
    if not doctor or not auth.verify_password(payload.password, doctor.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login ID or password")

    token = auth.create_access_token(subject=doctor.login_id, role="doctor")
    return schemas.TokenResponse(access_token=token, role="doctor")


@router.post("/admin/login", response_model=schemas.TokenResponse)
def admin_login(payload: schemas.AdminLoginRequest, db: Session = Depends(get_admin_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == payload.email).first()
    if not admin or not auth.verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token(subject=admin.email, role="admin")
    return schemas.TokenResponse(access_token=token, role="admin")


# ---------- Admin: forgot password (security question flow) ----------
@router.post("/admin/forgot-password/question", response_model=schemas.AdminForgotPasswordQuestionResponse)
def get_security_question(payload: schemas.AdminForgotPasswordQuestionRequest, db: Session = Depends(get_admin_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == payload.email).first()
    if not admin or not admin.security_question:
        raise HTTPException(status_code=404, detail="No admin account with a security question set up for that email")
    return schemas.AdminForgotPasswordQuestionResponse(question=admin.security_question)


@router.post("/admin/forgot-password/reset")
def reset_password_with_answer(payload: schemas.AdminResetPasswordRequest, db: Session = Depends(get_admin_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == payload.email).first()
    if not admin or not admin.security_answer_hash:
        raise HTTPException(status_code=404, detail="Admin account not found")

    if not auth.verify_password(payload.answer.strip().lower(), admin.security_answer_hash):
        raise HTTPException(status_code=401, detail="Incorrect answer to security question")

    admin.password_hash = auth.hash_password(payload.new_password)
    db.commit()
    return {"detail": "Password reset successful. You can now log in with your new password."}


# ---------- Admin: change password (while logged in) ----------
@router.post("/admin/change-password")
def change_password(
    payload: schemas.AdminChangePasswordRequest,
    db: Session = Depends(get_admin_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    if not auth.verify_password(payload.current_password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    admin.password_hash = auth.hash_password(payload.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}