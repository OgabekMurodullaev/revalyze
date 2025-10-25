from django.urls import path

from apps.users.views import UserRegisterView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
]