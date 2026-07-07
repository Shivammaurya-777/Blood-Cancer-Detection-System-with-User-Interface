from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_doctor_db, get_patient_db, get_feedback_db
from app import models, schemas
from app.utils import ml_predict

router = APIRouter(tags=["Stats"])


@router.get("/stats", response_model=schemas.StatsOut)
def get_stats(
    doctor_db: Session = Depends(get_doctor_db),
    patient_db: Session = Depends(get_patient_db),
    feedback_db: Session = Depends(get_feedback_db),
):
    doctors = doctor_db.query(models.Doctor).count()
    feedbacks = feedback_db.query(models.Feedback).count()

    predictions_query = patient_db.query(models.Prediction).all()
    predictions = len(predictions_query)
    patients = patient_db.query(models.Patient).count()

    positive = sum(1 for p in predictions_query if ml_predict.is_positive(p.cancer_type))
    negative = predictions - positive

    return schemas.StatsOut(
        doctors=doctors,
        feedbacks=feedbacks,
        predictions=predictions,
        patients=patients,
        positive=positive,
        negative=negative,
    )