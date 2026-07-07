"""
SMS service.

CURRENTLY SIMULATED: SMS messages are printed to the console and appended
to `sent_sms.log` instead of actually being sent, since no SMS provider
(Twilio / MSG91 / Fast2SMS / etc.) credentials were supplied yet.

To go live later:
1. Pick a provider and install its SDK (e.g. `pip install twilio`)
2. Set env vars for the provider's credentials
3. Replace the body of `send_sms()` with the real API call
"""

from datetime import datetime

SIMULATE = True
LOG_FILE = "sent_sms.log"


def send_sms(to_mobile: str, message: str) -> None:
    if SIMULATE:
        entry = (
            f"\n--- SMS ({datetime.now().isoformat()}) ---\n"
            f"To: {to_mobile}\nMessage: {message}\n"
            f"-------------------------------\n"
        )
        print(entry)
        with open(LOG_FILE, "a") as f:
            f.write(entry)
        return

    # ---- Real SMS sending (enable when ready), e.g. with Twilio ----
    # from twilio.rest import Client
    # client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    # client.messages.create(
    #     body=message,
    #     from_=os.getenv("TWILIO_FROM_NUMBER"),
    #     to=to_mobile,
    # )


def send_approval_sms(to_mobile: str, login_id: str, password: str) -> None:
    message = (
        f"Your registration is approved. Login ID: {login_id}, "
        f"Password: {password}. Keep this confidential."
    )
    send_sms(to_mobile, message)


def send_rejection_sms(to_mobile: str, reason: str) -> None:
    message = f"Your registration was not approved. Reason: {reason}"
    send_sms(to_mobile, message)
