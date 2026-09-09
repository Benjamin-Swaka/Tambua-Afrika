import os
from pathlib import Path

from django.core.checks import DEBUG
import dj_database_url
from dotenv import load_dotenv


# ==============================================
# BASE DIRECTORY / ENVIRONMENT
# ==============================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ==============================================
# SECURITY
# ==============================================

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-development-only-key")

if not DEBUG and SECRET_KEY == "django-insecure-development-only-key":
    raise RuntimeError("SECRET_KEY env var is not set — refusing to run in production with the insecure default.")



ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]

# ==============================================
# PRODUCTION SECURITY HARDENING
# ==============================================

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30   # 30 days; raise once confident
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False  

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
    "faq_app",
    "chatbot",
]


# ==============================================
# MIDDLEWARE
# ==============================================


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # <-- add this line
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

                "chatbot.context_processors.chatbot_stats",
            ],
        },
    },
]


# ==============================================
# WSGI
# ==============================================

WSGI_APPLICATION = "config.wsgi.application"




DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
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

# STATIC FILES — replace your existing STATIC_URL block with this
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"   

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True

ACCOUNT_EMAIL_VERIFICATION_BY_CODE_FORMAT = {
    "numeric": True,
    "length": 6,
    "dashed": False,
}


ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT = 900  # 15 minutes
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS = 5


ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND = True

ACCOUNT_UNIQUE_EMAIL = True


ACCOUNT_PREVENT_ENUMERATION = True


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
# PASSWORD RESET ("Forgot password")
# ==============================================

# Log the user straight in once they've set a new password instead of
# forcing them through a separate login step right after.
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# Password reset links expire after this many days.
PASSWORD_RESET_TIMEOUT_DAYS = 1

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

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    import warnings
    warnings.warn(
        "EMAIL_HOST_USER / EMAIL_HOST_PASSWORD are not set (check your .env "
        "file) -- falling back to the console email backend. Verification "
        "codes and password reset emails will print to the terminal instead "
        "of being sent. Run `python manage.py send_test_email you@example.com` "
        "once real SMTP credentials are set to confirm delivery works.",
        RuntimeWarning,
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

# ==============================================
# PESAPAL (ticket payments)
# ==============================================
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
PESAPAL_ENV = os.getenv("PESAPAL_ENV", "sandbox")
PESAPAL_CONSUMER_KEY = os.getenv("PESAPAL_CONSUMER_KEY", "")
PESAPAL_CONSUMER_SECRET = os.getenv("PESAPAL_CONSUMER_SECRET", "")
PESAPAL_IPN_ID = os.getenv("PESAPAL_IPN_ID", "")
PESAPAL_BASE_URL = (
    "https://pay.pesapal.com/v3/api" if PESAPAL_ENV == "live"
    else "https://cybqa.pesapal.com/pesapalv3/api"
)


CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}