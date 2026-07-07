# HemaScan — Blood Cancer Detection System

A hospital-only system: doctors register and get approved by an admin, then use
an AI model to screen blood cell images for leukemia types, track patient
history, and submit feedback. Admins approve/reject doctor registrations and
manage doctor accounts.

## Tech stack
- Backend: FastAPI (Python) + SQLite (via SQLAlchemy) + JWT auth
- Frontend: Plain HTML/CSS/JS (no build step needed)
- ML: PyTorch (.pth) model — plug in your trained model, see below

---

## 1. Setup

```bash
cd blood_cancer_system
pip install -r requirements.txt
python init_db.py       # creates database.db + a default admin account
```

Default admin login (change this after first login):
- Email: `admin@hospital.com`
- Password: `Admin@123`

## 2. Run the backend

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is now live at `http://localhost:8000`.

## 3. Run the frontend

The frontend is plain static HTML/CSS/JS — any static server works:

```bash
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080/index.html` in your browser.

> If you deploy backend/frontend on different hosts, update `API_BASE` in
> `frontend/js/api.js`.

## 4. Plug in your trained model

Drop your trained PyTorch model file here:
```
app/ml_model/model.pt
```

Then open `app/utils/ml_predict.py` and:
1. Set `CLASS_NAMES` to match your model's exact output classes, in order.
2. If your `.pt` file was saved as a full model (`torch.save(model, path)`), it loads automatically.
   If it was saved as a `state_dict`, follow the comment in `_load_model()` to plug in your architecture.
3. Fill in `SYMPTOMS_MAP` and `MEDICINES_MAP` with clinically verified content per class — the placeholders
   in there now are NOT medical advice and must be reviewed/filled by a qualified clinical team.

Until a model file is present, the app automatically falls back to a **mock predictor**
(random class + confidence) so you can test the full flow end-to-end.

## 5. Email & SMS notifications

Currently **simulated** — approval/rejection messages are printed to the console
and logged to `sent_emails.log` / `sent_sms.log` instead of actually sending.

To go live:
- Email: edit `app/utils/email_service.py`, set `SIMULATE = False`, fill in SMTP credentials
- SMS: edit `app/utils/sms_service.py`, set `SIMULATE = False`, integrate your SMS provider (Twilio, MSG91, etc.)

## 6. Project structure

```
blood_cancer_system/
├── app/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── database.py              # DB engine/session
│   ├── models.py                # SQLAlchemy tables
│   ├── schemas.py                # Pydantic request/response models
│   ├── auth.py                  # JWT auth + password hashing
│   ├── utils/
│   │   ├── email_service.py
│   │   ├── sms_service.py
│   │   ├── id_generator.py      # auto Patient ID / Doctor login ID
│   │   └── ml_predict.py        # loads model.pt, runs prediction
│   ├── routers/                 # all API endpoints, grouped by feature
│   ├── static/uploads/          # uploaded degree + cell images
│   └── ml_model/                # put your model.pt here
├── frontend/
│   ├── index.html               # landing page
│   ├── register.html            # doctor registration
│   ├── doctor_login.html
│   ├── admin_login.html
│   ├── doctor_dashboard.html    # prediction, patient history, feedback
│   ├── admin_dashboard.html     # requests, doctor management, feedback
│   ├── css/style.css
│   └── js/
├── init_db.py
└── requirements.txt
```

## 7. End-to-end flow (already tested)

1. Doctor submits registration → `POST /register`
2. Admin views pending requests → `GET /admin/requests`
3. Admin approves (sets login ID + password) → `POST /admin/requests/{id}/approve` → sends email+SMS
   OR admin rejects with a reason → `POST /admin/requests/{id}/reject` → sends email+SMS
4. Doctor logs in with the issued credentials → `POST /doctor/login`
5. Doctor uploads a cell image + patient name → `POST /predict` → auto-generates Patient ID, runs model, saves record
6. Doctor searches patient history by Patient ID → `GET /patients/{id}`
7. Doctor submits feedback → `POST /feedback`
8. Admin views feedback list → `GET /admin/feedback`
9. Admin manages doctors (edit/delete) → `PUT` / `DELETE /admin/doctors/{id}`

All of the above was verified working with real HTTP requests during development.
