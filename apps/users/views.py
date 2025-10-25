from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.users.models import User
from apps.users.serializers import UserRegisterSerializer


class UserRegisterView(CreateAPIView):
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer