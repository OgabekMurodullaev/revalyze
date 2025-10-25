from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User, VerificationOtp
from apps.users.serializers import UserRegisterSerializer


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