from pathlib import Path
import environ
import os
# ------------------------------------------------
# BASE
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/



env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

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

    # Local apps
    "apps.students",
    'django_ckeditor_5',
    'apps.courses',
    "apps.quizzes",
    "apps.classes",
    "apps.core",
    "apps.teachers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # CORS (must be before CommonMiddleware)
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    'django.middleware.locale.LocaleMiddleware',

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
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://45.76.151.28',
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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


USE_I18N = True
USE_L10N = True # Enable localization of formats (dates, numbers, etc.)

LANGUAGE_CODE = 'en-us' # Set your default language

LANGUAGES = [
    ('en', 'អង់គ្លេស'),
    ('km', 'ខ្មែរ'), # Add Khmer language
    # Add more languages as needed
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

CSP_FRAME_SRC = ('https://www.youtube-nocookie.com', 'https://www.youtube.com', 'https://drive.google.com')

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'fontFamily', 'fontSize', '|',  # Font family and size
            'bold', 'italic', 'underline', '|',
            'bulletedList', 'numberedList', 'outdent', 'indent', '|',
            'link', 'insertImage', 'mediaEmbed', '|',  # Image and media embeds
            'sourceEditing'  # Source code editing
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
        'language': 'en',  # Khmer ('km') not fully supported; content can still be Khmer
        'image': {
            'toolbar': ['imageTextAlternative', 'imageStyle:full', 'imageStyle:side']
        },
        'mediaEmbed': {
            'previewsInData': True  # Enables oEmbed previews (YouTube, Vimeo, etc.)
        },
        'width': '900px',
        'height': 'auto'
    }
}
