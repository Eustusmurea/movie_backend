# users/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email_task(email, first_name="User"):
    subject = "🎬 Welcome to Movie Backend!"
    from_email = os.environ.get("EMAIL_HOST_USER", "no-reply@movie-backend.local")
    to = [email]

    # Render HTML template
    html_content = render_to_string(
        "emails/welcome_email.html",
        {"user": {"first_name": first_name, "email": email}}
    )


    # Plain-text fallback
    text_content = (
        f"Hello {first_name},\n\n"
        "Thank you for registering with Movie Backend! 🎉\n"
        "We’re thrilled to have you on board.\n\n"
        "🍿 Happy watching!\n"
        "— The Movie Backend Team"
    )

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to, reply_to=["support@movie-backend.local"]
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        return f"✅ Welcome email sent to {email}"
    except Exception as e:
        logger.error(f"❌ Failed to send welcome email to {email}: {e}")
        return f"Error sending email to {email}"
