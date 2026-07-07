import os
import shutil
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_patient_db
from app import models, schemas, auth
from app.utils import ml_predict, id_generator

router = APIRouter(tags=["Prediction"])

UPLOAD_DIR = "app/static/uploads/cell_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/predict")
def predict_cancer(
    patient_name: str = Form(...),
    cell_image: UploadFile = File(...),
    db: Session = Depends(get_patient_db),
    doctor: models.Doctor = Depends(auth.get_current_doctor),
):
    # Save uploaded image
    ext = os.path.splitext(cell_image.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(cell_image.file, buffer)

    # Create patient record with auto-generated ID
    patient_id = id_generator.generate_patient_id(db)
    patient = models.Patient(
        patient_id=patient_id,
        patient_name=patient_name,
        doctor_id=doctor.id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Run model prediction
    cancer_type, confidence = ml_predict.predict(image_path)
    symptoms = ml_predict.get_symptoms(cancer_type)
    medicines = ml_predict.get_medicines(cancer_type)

    prediction = models.Prediction(
        patient_id=patient.patient_id,
        cell_image_path=image_path,
        cancer_type=cancer_type,
        confidence=confidence,
        symptoms=symptoms,
        medicines=medicines,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "patient_id": patient.patient_id,
        "patient_name": patient.patient_name,
        "cell_image_path": prediction.cell_image_path,
        "cancer_type": prediction.cancer_type,
        "confidence": prediction.confidence,
        "symptoms": prediction.symptoms,
        "medicines": prediction.medicines,
    }