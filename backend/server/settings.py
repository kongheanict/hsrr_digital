from pathlib import Path
import os
from decouple import config
# ------------------------------------------------
# BASE
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

# ------------------------------------------------
# APPLICATIONS
# ------------------------------------------------
INSTALLED_APPS = [
    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",

    # Local apps
    "apps.students",
    # add "apps.teachers", "apps.quizzes", etc. as you create them
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # CORS (must be before CommonMiddleware)
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    # Whitenoise for static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

# ------------------------------------------------
# TEMPLATES
# ------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Vue build will copy index.html here
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"
ASGI_APPLICATION = "server.asgi.application"

# ------------------------------------------------
# DATABASE (default SQLite, replace with Postgres in prod)
# ------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DATABASE_NAME"),
        "USER": config("DATABASE_USER"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": config("DATABASE_HOST", default="localhost"),
        "PORT": config("DATABASE_PORT", default="5432"),
    }
}
# ------------------------------------------------
# PASSWORDS
# ------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------
# I18N
# ------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Phnom_Penh"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------
# STATIC & MEDIA
# ------------------------------------------------
STATIC_URL = "/static/"

# Where static files live during development
STATICFILES_DIRS = [BASE_DIR / "static"]

# Where collectstatic will put everything (for production)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise compressed storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media uploads
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------
# DEFAULT PRIMARY KEY
# ------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------
# REST FRAMEWORK
# ------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ------------------------------------------------
# CORS (allow Vue dev server at 5173)
# ------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # dev only
# Better in production:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "https://yourdomain.com",
# ]
