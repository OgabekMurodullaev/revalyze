from tokenize import TokenError

from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, VerificationOtp, UserProfile


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


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Email yoki parol noto'g'ri")

        if not user.is_verified:
            raise serializers.ValidationError("Foydalanuvchi tizimda tasdiqlanmagan")


        return {'user': user}


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        self.token = data['refresh']
        return data

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user = User.objects.filter(email=email, is_verified=False).first()
        if not user:
            raise serializers.ValidationError({"detail": "Tizimda bunday foydalanuvchi topilmadi."})
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user', 'resumes_count']