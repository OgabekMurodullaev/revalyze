from django.urls import path

from apps.users.views import UserRegisterView, VerifyOtpView, ResendOtpView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('resend-otp/', ResendOtpView.as_view(), name='otp-resend'),
    path('verify-otp/', VerifyOtpView.as_view(), name='otp-verify'),
]