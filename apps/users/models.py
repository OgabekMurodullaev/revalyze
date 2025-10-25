from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .utils import check_otp_code


class User(AbstractUser):
    class UserRoleChoices(models.TextChoices):
        USER = "user", _("User")
        RECRUITER = "recruiter", _("Recruiter")
        ADMIN = "admin", _("Admin")

    username = None

    email = models.EmailField(unique=True)
    role = models.CharField(_("Role"), max_length=9, choices=UserRoleChoices, default=UserRoleChoices.USER)
    is_verified = models.BooleanField(_("Verified"), default=False)

    USERNAME_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class VerificationOtp(models.Model):
    class VerificationType(models.TextChoices):
        REGISTER = "register", _("Register")
        RESET_PASSWORD = "reset_password", _("Reset password")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_otp")
    code = models.IntegerField(_("Otp code"), validators=[check_otp_code])
    verify_type = models.CharField(_("Verification type"), max_length=14, choices=VerificationType.choices,
                                   default=VerificationType.REGISTER)
    expires_in = models.DateTimeField(_("Expires in"))
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.user.email} | code: {self.code}"

    class Meta:
        verbose_name = _("Verification Otp")
        verbose_name_plural = _("Verification Otps")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField(_("Bio"), max_length=128, null=True, blank=True)
    location = models.CharField(_("Location"), max_length=128, null=True, blank=True)
    phone_number = models.CharField(_("Phone Number"), max_length=20, validators=[RegexValidator(r'^\+?1?\d{9,13}$')])
    linkedin_url = models.URLField(_("Linkedin url"), null=True, blank=True)
    github_url = models.URLField(_("Github url"), null=True, blank=True)
    profile_image = models.ImageField(_("Profile image"), upload_to="profile-images/", null=True, blank=True)
    preferred_job_titles = models.JSONField(_("Preferred job titles"), null=True, blank=True)
    resume_count = models.IntegerField(_("Resume count"), default=0)

    def __str__(self):
        return f"{self.user.email}'s profile"

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("Users Profiles")