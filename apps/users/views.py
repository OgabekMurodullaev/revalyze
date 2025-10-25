from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User, VerificationOtp
from apps.users.serializers import UserRegisterSerializer, VerifyOtpSerializer, ResendOtpSerializer
from apps.users.tasks import send_verification_otp
from apps.users.utils import generate_code
from core.settings.base import OTP_CODE_ACTIVATION_TIME


class UserRegisterView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = VerificationOtp.objects.filter(user=user).order_by('-created_at').first()
            data = {
                "message": "Tasdiqlash kodi emailingizga yuborild",
                "code id": otp.id if otp else None
            }

            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = VerifyOtpSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data["otp"]
        user = otp.user

        otp.is_active = False
        otp.save(update_fields=["is_active"])

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return Response(
            {
                "message": "Hisobingiz muvaffaqiyatli tasdiqlandi",
                "user_email": user.email
            },
            status=status.HTTP_200_OK
        )


class ResendOtpView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ResendOtpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['email']

        VerificationOtp.objects.filter(
            user=user,
            verify_type=VerificationOtp.VerificationType.REGISTER
        ).delete()

        code = generate_code()
        code = VerificationOtp.objects.create(user=user, code=code, verify_type=VerificationOtp.VerificationType.REGISTER,
                                       expires_in=datetime.now() + timedelta(minutes=OTP_CODE_ACTIVATION_TIME))
        send_verification_otp(user.email, code)
        return Response({"message": "Tasdiqlash kodi emailingizga yuborildi", "code_id": code.id}, status=status.HTTP_200_OK)