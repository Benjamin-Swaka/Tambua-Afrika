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
    "faq_app",
    "chatbot",
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
                
                "chatbot.context_processors.chatbot_stats",
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

# Verify by 6-digit OTP code instead of a clickable link.
# This avoids link-based verification issues entirely (broken email
# clients stripping links, links opening on the wrong device, spam
# filters flagging links, etc.) and matches the flow requested by
# the product team.
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True

# allauth's default OTP is an 8-character dashed alphanumeric code (e.g.
# "VKVD-BNBD") -- fine on its own, but our code-entry screen was built
# for a plain 6-digit numeric code (numeric keypad, 6-box input), so the
# two didn't match and codes couldn't be typed in. Force a plain numeric
# code here so the email content and the entry screen agree.
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_FORMAT = {
    "numeric": True,
    "length": 6,
    "dashed": False,
}

# How long (seconds) an emailed signup code stays valid, and how many
# attempts a user gets before the code is invalidated.
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT = 900  # 15 minutes
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS = 5

# Let a user request a fresh code if the first one expires or never
# arrives, instead of getting stuck (a fresh code is automatically sent
# the next time they attempt to log in with an unverified address).
ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND = True

ACCOUNT_UNIQUE_EMAIL = True

# IMPORTANT: with mandatory verification, allauth deliberately shows the
# *same* "check your email" screen whether or not the address is already
# registered (this stops attackers from using signup to discover which
# emails exist on the site). If the address already belongs to a
# verified account, allauth still emails that address -- but the email
# says "you already have an account, log in / reset your password"
# instead of containing a new OTP code. So: if a genuinely first-time
# user says they got an "account already exists" email, the real fix is
# to check for (and clean up) a stale/duplicate User + EmailAddress row
# already sitting in the database for that email -- see the
# `find_stale_signups` management command added below.
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

# If SMTP credentials aren't configured (e.g. no .env file, or it's
# missing EMAIL_HOST_USER/EMAIL_HOST_PASSWORD), silently trying to send
# real mail would just fail every time verification codes are needed --
# often with no obvious error to the person testing signup. Fall back to
# printing emails straight to the console so local development still
# works, and log a loud warning so it's obvious *why* nothing is landing
# in an inbox.
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