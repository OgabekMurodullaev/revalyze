from django.utils import timezone
from rest_framework import serializers
from .models import User, VerificationOtp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Bu email bilan ro'yxatdan o'tilgan")
        return email

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class VerifyOtpSerializer(serializers.Serializer):
    code_id = serializers.IntegerField(required=True)
    code = serializers.CharField(required=True, max_length=6)

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Kod faqat raqamlardan iborat bo'lishi kerak")
        return value

    def validate(self, data):
        code_id = data.get('code_id')
        code = data.get('code')

        otp = VerificationOtp.objects.filter(id=code_id, code=code).first()

        if not otp:
            raise serializers.ValidationError({"detail": "Bunday kod topilmadi"})

        if not otp.is_active:
            raise serializers.ValidationError({"detail": "Bu kod allaqachon ishlatilgan."})

        if otp.expires_in < timezone.now():
            raise serializers.ValidationError({"detail": "Kodning amal qilish muddati tugagan."})

        data["otp"] = otp
        return data


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user = User.objects.filter(email=email, is_verified=False).first()
        if not user:
            raise serializers.ValidationError({"detail": "Tizimda bunday foydalanuvchi topilmadi."})
        return user