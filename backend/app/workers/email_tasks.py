import asyncio
from app.workers.celery_app import celery_app
from app.services.email import get_email_service

def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.create_task(coro)

@celery_app.task(name="send_verification_email_task")
def send_verification_email_task(to_email: str, verification_token: str) -> bool:
    email_service = get_email_service()
    subject = "Verify your AxonTime HR Account"
    body = (
        f"Welcome to AxonTime HR!\n\n"
        f"Please verify your email address by submitting the following token:\n"
        f"{verification_token}\n\n"
        f"Or click here: http://localhost:3000/verify-email?token={verification_token}"
    )
    _run_async(email_service.send_email(to_email, subject, body))
    return True

@celery_app.task(name="send_password_reset_email_task")
def send_password_reset_email_task(to_email: str, reset_token: str) -> bool:
    email_service = get_email_service()
    subject = "Reset your AxonTime HR Password"
    body = (
        f"You requested a password reset for your AxonTime HR account.\n\n"
        f"Submit the following reset token to set a new password:\n"
        f"{reset_token}\n\n"
        f"Or click here: http://localhost:3000/reset-password?token={reset_token}\n\n"
        f"This link expires in 30 minutes. If you did not request this, please ignore this email."
    )
    _run_async(email_service.send_email(to_email, subject, body))
    return True
