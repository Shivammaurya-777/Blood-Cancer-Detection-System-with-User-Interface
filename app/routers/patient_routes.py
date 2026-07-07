from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_patient_db
from app import models, schemas, auth

router = APIRouter(tags=["Patients"])


@router.get("/patients/{patient_id}", response_model=schemas.PatientHistoryOut)
def get_patient_history(
    patient_id: str,
    db: Session = Depends(get_patient_db),
    doctor: models.Doctor = Depends(auth.get_current_doctor),
):
    patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient