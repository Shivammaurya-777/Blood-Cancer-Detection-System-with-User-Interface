from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_feedback_db
from app import models, schemas, auth

router = APIRouter(tags=["Feedback"])


@router.post("/feedback", response_model=schemas.FeedbackOut)
def submit_feedback(
    payload: schemas.FeedbackCreate,
    db: Session = Depends(get_feedback_db),
    doctor: models.Doctor = Depends(auth.get_current_doctor),
):
    feedback = models.Feedback(
        doctor_id=doctor.id,
        ratings_json=payload.ratings_json,
        comments=payload.comments,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/admin/feedback", response_model=list[schemas.FeedbackOut])
def list_feedback(
    db: Session = Depends(get_feedback_db),
    admin: models.Admin = Depends(auth.get_current_admin),
):
    return db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()