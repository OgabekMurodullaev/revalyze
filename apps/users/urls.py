from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    UserRegisterView,
    VerifyOtpView,
    ResendOtpView,
    UserLoginView,
    UserLogoutView,
    UserProfileViewSet,
                              )

router = DefaultRouter()
router.register('profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('resend-otp/', ResendOtpView.as_view(), name='otp-resend'),
    path('verify-otp/', VerifyOtpView.as_view(), name='otp-verify'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('', include(router.urls))
]
