from .base import *
import os
# import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ["revalyze.uz", "www.revalyze.uz"]

# DATABASES = {
#     "default": dj_database_url.config(default=os.getenv("DATABASE_URL"))
# }

# Production email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")

# CORS and security
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://revalyze.uz",
]