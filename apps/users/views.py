from datetime import datetime, timedelta

from django.db import transaction

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import VerificationOtp, UserProfile
from apps.users.permissions import IsOwnerOrReadOnly
from apps.users.serializers import UserRegisterSerializer, VerifyOtpSerializer, ResendOtpSerializer, \
    UserLoginSerializer, UserLogoutSerializer, UserProfileSerializer
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


class UserLoginView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        data = {
            "message": "Muvaffaqiyatli login",
            "access": str(access),
            "refresh": str(refresh)
        }
        return Response(data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserLogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Tizimdan chiqildi."}, status=status.HTTP_204_NO_CONTENT)



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


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.select_related('user')
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'put', 'patch', 'delete']

    def get_queryset(self):
        return self.queryset

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()