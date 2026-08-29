import os
from pathlib import Path

from dotenv import load_dotenv


# ==============================================
# BASE DIRECTORY / ENVIRONMENT
# ==============================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ==============================================
# SECURITY
# ==============================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-development-only-key"
)

DEBUG = os.getenv(
    "DEBUG",
    "True"
).lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]


# ==============================================
# APPLICATIONS
# ==============================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Django Sites
    "django.contrib.sites",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    # Google only
    "allauth.socialaccount.providers.google",

    # ==========================================
    # CUSTOM APPLICATIONS
    # ==========================================

    "core",
    "ink",
    "stage",
    "comics",
    "shop",
    "submissions",
    "journal",
    "users",
]


# ==============================================
# MIDDLEWARE
# ==============================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    'django.middleware.locale.LocaleMiddleware',

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    
    "allauth.account.middleware.AccountMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==============================================
# URLS
# ==============================================

ROOT_URLCONF = "config.urls"


# ==============================================
# TEMPLATES
# ==============================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",

                # Required by allauth
                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==============================================
# WSGI
# ==============================================

WSGI_APPLICATION = "config.wsgi.application"


# ==============================================
# DATABASE
# ==============================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==============================================
# PASSWORD VALIDATION
# ==============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


# INTERNATIONALIZATION

LANGUAGE_CODE = "en"         

USE_I18N = True
USE_L10N = True             
USE_TZ = True

# Supported languages
LANGUAGES = [
    ('en', 'English'),
    ('sw', 'Swahili'),
    ('fr', 'French'),
]

# Where Django will look for translation files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# STATIC FILES
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# MEDIA FILES
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# DEFAULT PRIMARY KEY
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==============================================
# DJANGO SITES FRAMEWORK
# ==============================================

SITE_ID = 1


# ==============================================
# AUTHENTICATION BACKENDS
# ==============================================

AUTHENTICATION_BACKENDS = [
    # Normal username/password authentication
    "django.contrib.auth.backends.ModelBackend",

    # django-allauth authentication
    "allauth.account.auth_backends.AuthenticationBackend",
]


# ==============================================
# DJANGO-ALLAUTH
# ==============================================

# Users log in using their email address
ACCOUNT_LOGIN_METHODS = {
    "email",
}


# ==============================================
# SIGNUP
# ==============================================

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "first_name",
    "last_name",
    "password1*",
    "password2*",
]


# ==============================================
# EMAIL VERIFICATION
# ==============================================

# We are using mandatory verification because
# users must verify their email before continuing.
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_UNIQUE_EMAIL = True


# ==============================================
# SESSION
# ==============================================

ACCOUNT_SESSION_REMEMBER = True


# ==============================================
# REDIRECTS
# ==============================================

LOGIN_REDIRECT_URL = "dashboard_routing"
ACCOUNT_LOGIN_ON_CODE_CONFIRM = True   # default is True, but be explicit

LOGIN_URL = "account_login"

LOGIN_REDIRECT_URL = "dashboard_routing"

LOGOUT_REDIRECT_URL = "home"

ACCOUNT_LOGIN_BY_CODE_ENABLED = False
ACCOUNT_LOGIN_ON_CODE_CONFIRM = True

# Email subject prefix
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Tambua Afrika - "

# ==============================================
# CUSTOM ALLAUTH FORMS
# ==============================================

ACCOUNT_FORMS = {
    "login": "users.forms.CustomLoginForm",
    "signup": "users.forms.CustomSignupForm",
}


# ==============================================
# EMAIL / SMTP
# ==============================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.gmail.com"
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587"
    )
)

EMAIL_USE_TLS = os.getenv(
    "EMAIL_USE_TLS",
    "True"
).lower() == "true"

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER"
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD"
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
)


# ==============================================
# GOOGLE OAUTH
# ==============================================

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv(
                "GOOGLE_CLIENT_ID"
            ),

            "secret": os.getenv(
                "GOOGLE_CLIENT_SECRET"
            ),

            "key": "",
        },

        "SCOPE": [
            "profile",
            "email",
        ],

        "AUTH_PARAMS": {
            "access_type": "online",
        },

        "METHOD": "oauth2",

        "VERIFIED_EMAIL": True,
    }
}