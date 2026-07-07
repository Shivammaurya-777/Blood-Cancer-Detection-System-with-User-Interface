"""
Email service.

CURRENTLY SIMULATED: emails are printed to the console and appended to
`sent_emails.log` instead of actually being sent, since no SMTP/email
provider credentials were supplied yet.

To go live later:
1. Set env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
2. Uncomment the real-send code in `send_email()` below.
"""

import os
from datetime import datetime

SIMULATE = True  # flip to False once real SMTP credentials are configured
LOG_FILE = "sent_emails.log"


def send_email(to_email: str, subject: str, body: str) -> None:
    if SIMULATE:
        entry = (
            f"\n--- EMAIL ({datetime.now().isoformat()}) ---\n"
            f"To: {to_email}\nSubject: {subject}\n\n{body}\n"
            f"----------------------------------------\n"
        )
        print(entry)
        with open(LOG_FILE, "a") as f:
            f.write(entry)
        return

    # ---- Real SMTP sending (enable when ready) ----
    # import smtplib
    # from email.mime.text import MIMEText
    #
    # msg = MIMEText(body)
    # msg["Subject"] = subject
    # msg["From"] = os.getenv("SMTP_USER")
    # msg["To"] = to_email
    #
    # with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", 587))) as server:
    #     server.starttls()
    #     server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
    #     server.send_message(msg)


def send_approval_email(to_email: str, full_name: str, login_id: str, password: str) -> None:
    subject = "Your registration has been approved"
    body = (
        f"Dear Dr. {full_name},\n\n"
        f"Your registration has been approved. You can now log in to the "
        f"Blood Cancer Detection System with the following credentials:\n\n"
        f"Login ID: {login_id}\n"
        f"Password: {password}\n\n"
        f"Please change your password after your first login (if supported) "
        f"and keep these credentials confidential.\n\n"
        f"Regards,\nAdmin Team"
    )
    send_email(to_email, subject, body)


def send_rejection_email(to_email: str, full_name: str, reason: str) -> None:
    subject = "Your registration was not approved"
    body = (
        f"Dear {full_name},\n\n"
        f"We regret to inform you that your registration request was not approved.\n\n"
        f"Reason: {reason}\n\n"
        f"You are welcome to submit a new request with corrected/updated details.\n\n"
        f"Regards,\nAdmin Team"
    )
    send_email(to_email, subject, body)
