from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.tasks import send_verification_otp
from core.settings.base import OTP_CODE_ACTIVATION_TIME
from apps.users.models import User, VerificationOtp
from apps.users.utils import generate_code


@receiver(post_save, sender=User)
def create_verification_otp(sender, instance, created, **kwargs):
    if created:
        code = generate_code()
        VerificationOtp.objects.create(user=instance, code=code, verify_type=VerificationOtp.VerificationType.REGISTER,
                                       expires_in=datetime.now() + timedelta(minutes=OTP_CODE_ACTIVATION_TIME))
        send_verification_otp(email=instance.email, code=code)
        print("Signal is working")