from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import (
    auth_routes,
    registration_routes,
    prediction_routes,
    patient_routes,
    feedback_routes,
    admin_routes,
    stats_routes,
)

app = FastAPI(title="Blood Cancer Detection System API")

# Allow the frontend to call this API (same-origin now, but kept permissive
# in case the frontend is ever hosted separately again).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images (degree images, cell images, landing background images)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve the frontend's CSS and JS as static assets
app.mount("/frontend/css", StaticFiles(directory="frontend/css"), name="frontend_css")
app.mount("/frontend/js", StaticFiles(directory="frontend/js"), name="frontend_js")

app.include_router(auth_routes.router)
app.include_router(registration_routes.router)
app.include_router(prediction_routes.router)
app.include_router(patient_routes.router)
app.include_router(feedback_routes.router)
app.include_router(admin_routes.router)
app.include_router(stats_routes.router)


# ---------------- FRONTEND PAGE ROUTES ----------------
# These serve the actual HTML pages so the site works by simply starting the
# server and opening it in a browser - no double-clicking HTML files needed.

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")


@app.get("/register")
def serve_register_page():
    return FileResponse("frontend/register.html")


@app.get("/doctor/login")
def serve_doctor_login_page():
    return FileResponse("frontend/doctor_login.html")


@app.get("/doctor/dashboard")
def serve_doctor_dashboard_page():
    return FileResponse("frontend/doctor_dashboard.html")


# Admin pages are never linked from public pages - reachable only by typing
# the URL directly, as requested.
@app.get("/admin")
def serve_admin_login_page():
    return FileResponse("frontend/admin_login.html")


@app.get("/admin/dashboard")
def serve_admin_dashboard_page():
    return FileResponse("frontend/admin_dashboard.html")


@app.get("/admin/forgot-password")
def serve_admin_forgot_password_page():
    return FileResponse("frontend/admin_forgot_password.html")


@app.get("/admin/change-password")
def serve_admin_change_password_page():
    return FileResponse("frontend/admin_change_password.html")
