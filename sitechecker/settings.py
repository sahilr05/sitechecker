"""
Django settings for sitechecker project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (os.getenv("DJANGO_SECRET_KEY"),)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "celery",
    "widget_tweaks",
    # Custom
    "accounts",
    "checkerapp",
    "phonenumber_field",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sitechecker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# DATABASES = {
#     "default": {
#         "ENGINE": os.environ.get("SQL_ENGINE"),
#         "NAME": os.environ.get("SQL_DATABASE"),
#         "USER": os.environ.get("SQL_USER"),
#         "PASSWORD": os.environ.get("SQL_PASSWORD"),
#         "HOST": os.environ.get("SQL_HOST", "localhost"),
#         "PORT": os.environ.get("SQL_PORT"),
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": os.getenv("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("SQL_DATABASE", "sitechecker"),
        "USER": os.getenv("SQL_USER", "postgres"),
        "PASSWORD": os.getenv("SQL_PASSWORD"),
        "HOST": os.getenv("SQL_HOST", "localhost"),
        "PORT": os.getenv("SQL_PORT"),
    }
}

WSGI_APPLICATION = "sitechecker.wsgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGOUT_REDIRECT_URL = "checkerapp:home"
LOGIN_REDIRECT_URL = "checkerapp:home"
LOGIN_URL = "/login"

STATIC_URL = "/static/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# EMAIL stuff
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# Celery
BROKER_URL = (os.environ.get("REDIS_HOST", "redis://127.0.0.1:6379/0"),)  # docker
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0

# CELERY_RESULT_BACKEND = 'django-db'
# CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_TASK_SERIALIZER = "pickle"

# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
