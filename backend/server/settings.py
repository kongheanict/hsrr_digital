from pathlib import Path
import environ
import os
import pytz
from datetime import timedelta

# ------------------------------------------------
# BASE
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Telegram settings
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = env('TELEGRAM_CHAT_ID')

# Timezone settings
TIME_ZONE = 'Asia/Phnom_Penh'
USE_TZ = True
os.environ['TZ'] = TIME_ZONE
# Validate timezone (optional, move to a custom function if needed)
try:
    pytz.timezone(TIME_ZONE)
except pytz.exceptions.UnknownTimeZoneError:
    raise ValueError(f"Invalid timezone: {TIME_ZONE}")

AUTH_USER_MODEL = 'authentication.CustomUser'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

DATABASES = {
    'default': env.db('DATABASE_URL')
}

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
    'nested_admin',
    'django_select2',
    'django_ckeditor_5',

    # Local apps
    "apps.students",
    "apps.courses",
    "apps.quizzes",
    "apps.classes",
    "apps.core",
    "apps.teachers",
    "apps.authentication",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.middleware.locale.LocaleMiddleware',
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
LANGUAGE_CODE = 'km'  # Default to Khmer
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ('en', 'អង់គ្លេស'),
    ('km', 'ខ្មែរ'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ------------------------------------------------
# STATIC & MEDIA
# ------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://45.76.151.28',
]
# Disable CORS_ALLOW_ALL_ORIGINS in production
CORS_ALLOW_ALL_ORIGINS = DEBUG  # True only in DEBUG mode

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'apps.authentication.serializers.CustomTokenObtainPairSerializer',  # Corrected path
}

# ------------------------------------------------
# CORS
# ------------------------------------------------

# ------------------------------------------------
# CKEDITOR
# ------------------------------------------------
CSP_FRAME_SRC = ('https://www.youtube-nocookie.com', 'https://www.youtube.com', 'https://drive.google.com')

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'fontFamily', 'fontSize', '|',
            'bold', 'italic', 'underline', '|',
            'bulletedList', 'numberedList', 'outdent', 'indent', '|',
            'link', 'insertImage', 'mediaEmbed', '|',
            'sourceEditing'
        ],
        'fontFamily': {
            'options': [
                'default',
                'Khmer OS, sans-serif',
                'Khmer OS Battambang, sans-serif',
                'Khmer OS Bokor, cursive',
                'Khmer OS Content, sans-serif',
                'Khmer OS Fasthand, cursive',
                'Khmer OS Moul, serif',
                'Arial, Helvetica, sans-serif',
                'Times New Roman, Times, serif',
                'Verdana, Geneva, sans-serif'
            ],
            'supportAllValues': True
        },
        'fontSize': {
            'options': ['8px', '10px', '12px', '14px', 'default', '16px', '18px', '24px', '36px'],
        },
        'language': 'en',
        'image': {
            'toolbar': ['imageTextAlternative', 'imageStyle:full', 'imageStyle:side']
        },
        'mediaEmbed': {
            'previewsInData': True
        },
        'width': '900px',
        'height': 'auto'
    }
}