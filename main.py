# IMPORTS
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import shutil
import sqlite3  # For catching database-specific errors

# Import Database modules
from database.db import cursor_user, conn_user
from database.db import cursor_patients, conn_patients
from database.db import cursor_feedback, conn_feedback
from database.db import cursor_predictions, conn_predictions
from saved_models.load_model import predict_image


# APP SETUP
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from pathlib import Path

# Get the base directory 
BASE_DIR = Path(__file__).resolve().parent

# Setup Templates with absolute path
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

# Setup Static files with absolute path
app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR, "static"))), name="static")

# PAGE ROUTES

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashbord.html")

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    return templates.TemplateResponse(request=request, name="feedback.html")

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse(request=request, name="history.html")
    


# PATIENT SEARCH API
# Fetch patient detaila by patient_id from database and return as JSON response
@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):
    cursor_patients.execute(
        "SELECT user_id, patient_name, detected_class, confidence_score, symptoms, image_path, created_at FROM patients WHERE patient_id=?",
        (patient_id,)
    )
    patient = cursor_patients.fetchone()

    if patient:
        return {
            "user_id": patient[0],
            "patient_name": patient[1],
            "detected_class": patient[2],
            "confidence_score": patient[3],
            "symptoms": patient[4],
            "image_path": patient[5],
            "created_at": patient[6]
        }
    else:
        return {"error": "Patient not found"}


# PREDICTION API

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    patient_name: str = Form(...),
    user_id: str = Form(...)
):
    print(f"Received predict request: patient_id={patient_id}, user_id={user_id}, file={file.filename}")
    try:
        # Ensure the upload directory exists before saving the file
        upload_dir = BASE_DIR / "static" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        file_path_str = str(file_path)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved to: {file_path_str}")

        # Model prediction
        predicted_class, confidence, symptoms = predict_image(file_path_str)

        print(f"Prediction: {predicted_class}, confidence: {confidence}")

        # Check for prediction errors
        if predicted_class == "ERROR":
            return {"error": f"Prediction failed: {symptoms}", "predicted_class": "ERROR", "confidence": 0.0, "symptoms": "Unable to analyze image"}

        # Save or update patient data
        cursor_patients.execute(
            "SELECT * FROM patients WHERE patient_id=?",
            (patient_id,)
        )

        if cursor_patients.fetchone():
            # Update existing patient
            cursor_patients.execute("""
                UPDATE patients SET 
                    patient_name=?, 
                    detected_class=?, 
                    confidence_score=?, 
                    symptoms=?, 
                    image_path=?
                WHERE patient_id=?
            """, (patient_name, predicted_class, confidence, symptoms, file_path_str, patient_id))
        else:
            # Insert new patient
            cursor_patients.execute("""
                INSERT INTO patients (patient_id, user_id, patient_name, detected_class, confidence_score, symptoms, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, user_id, patient_name, predicted_class, confidence, symptoms, file_path_str))

        # Save prediction
        cursor_predictions.execute("""
            INSERT INTO predictions (patient_id, predicted_class, confidence, image_path)
            VALUES (?, ?, ?, ?)
        """, (patient_id, predicted_class, confidence, file_path_str))

        # Commit changes to both databases
        conn_patients.commit()
        conn_predictions.commit()

        print("Data saved successfully")

        return {"predicted_class": predicted_class, "confidence": confidence, "symptoms": symptoms}

    except Exception as e:
        # Rollback in case of error
        conn_patients.rollback()
        conn_predictions.rollback()
        error_msg = f"Server error during prediction: {str(e)}"
        print(error_msg)
        return {"error": error_msg, "predicted_class": "ERROR", "confidence": 0.0, "symptoms": "Prediction failed due to server error"}


# FEEDBACK API
@app.post("/feedback")
async def submit_feedback(
    userid: str = Form(...),
    feedback: str = Form(...)
):
    cursor_feedback.execute("""
        INSERT INTO feedback (userid, feedback)
        VALUES (?, ?)
    """, (userid, feedback))

    conn_feedback.commit()

    return {"message": "Feedback submitted successfully"}


# HISTORY API
@app.get("/history/{patient_id}")
def get_history(patient_id: str):
    cursor_predictions.execute("""
        SELECT predicted_class, confidence, image_path, created_at
        FROM predictions
        WHERE patient_id=?
        ORDER BY created_at DESC
    """, (patient_id,))

    rows = cursor_predictions.fetchall()

    return {
        "history": [
            {
                "class": r[0],
                "confidence": r[1],
                "image": r[2],
                "date": r[3]
            }
            for r in rows
        ]
    }



# AUTHENTICATION API

@app.post("/api/signup")
async def api_signup(user_id: str = Form(...), email: str = Form(...), password: str = Form(...)):
    # Validate required fields
    if not user_id or not email or not password:
        raise HTTPException(status_code=400, detail="User ID, email, and password are required")

    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Check for existing user_id or email before insert
    cursor_user.execute("SELECT user_id, email FROM users WHERE user_id = ? OR email = ?", (user_id, email))
    existing_user = cursor_user.fetchone()
    if existing_user:
        if existing_user[0] == user_id:
            raise HTTPException(status_code=400, detail="User ID already registered")
        else:
            raise HTTPException(status_code=400, detail="Email already registered")

    try:
        cursor_user.execute("INSERT INTO users (user_id, email, password) VALUES (?, ?, ?)", (user_id, email, password))
        conn_user.commit()
        print(f"User registered successfully: {user_id} / {email}")
        return {"message": "User created successfully"}

    except sqlite3.IntegrityError as e:
        print(f"Registration failed (integrity error): {str(e)}")
        raise HTTPException(status_code=400, detail="User ID or email already registered")

    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.post("/login")
async def login_validation(user_id: str = Form(...), password: str = Form(...)):
    cursor_user.execute("SELECT * FROM users WHERE user_id = ? AND password = ?", (user_id, password))
    user = cursor_user.fetchone()

    if user:
        print(f"Login successful for: {user_id}")
        return {"status": "success", "redirect": "/dashboard"}
    else:
        print(f"Login failed: Invalid credentials for {user_id}")
        raise HTTPException(status_code=401, detail="Invalid User ID or Password")