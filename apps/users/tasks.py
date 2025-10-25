from celery import shared_task
from django.core.mail import send_mail

from core.settings import base


@shared_task
def send_verification_otp(email, code):
    subject = "Tasdiqlash kodi"
    message = f"Salom. Sizning kodingiz: {code}"
    from_email = base.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email],
              fail_silently=False)